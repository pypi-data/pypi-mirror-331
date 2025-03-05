from __future__ import annotations

import functools
import logging
from typing import Any, Union, List
from pysqream.column_buffer import ColumnsBuffer
from pysqream.globals import ROWS_PER_FLUSH, FETCH_MANY_DEFAULT, TYPE_MAPPER, BYTES_PER_FLUSH_LIMIT, TEXT_ITEM_SIZE
from pysqream.logger import log_and_raise, logger
from pysqream.utils import NotSupportedError, ProgrammingError, ArraysAreDisabled, mark_dbapi_attribute, dbapi_method
from pysqream.server.sqsocket import SQSocket
from pysqream.server.sqclient import SQClient
from pysqream.server.connection_params import ConnectionParams


class Cursor:
    """
    Represent a database cursor, which is used to manage the context of
    a statement (execute and fetch).

    Cursors created from the same connection are not
    isolated, i.e., any changes done to the database by a cursor are
    immediately visible by the other cursors.

    Base PEP 249 – Python Database API Specification v2.0
    https://peps.python.org/pep-0249/#id12
    """

    def __init__(self, conn_params: ConnectionParams, client: SQClient, connection_ld: int, allow_array: bool):

        # DB-API must have attributes
        self.arraysize = mark_dbapi_attribute(FETCH_MANY_DEFAULT)
        self.rowcount = mark_dbapi_attribute(-1)
        self.lastrowid = mark_dbapi_attribute(None)
        self.description = mark_dbapi_attribute(None)

        # SQreamDB connection attributes
        self.conn_params: ConnectionParams = conn_params
        self.client: SQClient = client
        self.connection_id: int = connection_ld
        self.allow_array: bool = allow_array

        # State management
        self.open_statement: bool = False
        self.is_cursor_closed: bool = False
        self.is_connection_initiated_close: bool = False
        self.base_connection_closed: bool = False

        # Buffer and data management
        self.buffer: ColumnsBuffer = ColumnsBuffer()  # flushing buffer every BUFFER_SIZE bytes
        self.stmt_id: Union[id, None] = None  # For error handling when called out of order
        self.statement_type: Union[str, None] = None
        self.more_to_fetch: bool = False
        self.capacity: int = 0

        # Data tracking
        self.rows_fetched: Union[int, None] = None
        self.rows_returned: Union[int, None] = None
        self.parsed_rows: List[Any] = []
        self.row_size: int = 0
        self.rows_per_flush: int = 0
        self.cols: List = []
        self.col_types: List = []
        self.col_sizes: List = []
        self.col_scales: List = []
        self.unsorted_data_columns: List = []

    def __enter__(self) -> Cursor:
        """
        Implementation for context manager ("with" clause)
        """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Implementation for context manager ("with" clause)
        """

        self.close()

    def __iter__(self):
        """
        Implementation for iterating connection in for-in clause
        """

        for item in self.fetchall():
            yield item

    # DB-API Must have methods
    # ------------------------
    @dbapi_method
    def execute(self, statement: str, params: list[tuple[Any]] | tuple[[tuple[Any]]] | None = None,
                data_as: str = 'rows', amount: int | None = None) -> Cursor:
        """
        Execute a statement. If params was provided - compile statement first
        and replace all question marks on passed parameters.

        :param statement: str a statement to execute with placeholders
        :param params: list[tuple[Any]] | tuple[tuple[Any]]: sequence of parameters to ingest into query
        :param data_as: string type of passed params. Possible values (`alchemy_flat_list`, `numpy`, `rows` - default)
        :param amount: int - amount of values of given params to insert

        Examples:
            query: SELECT * FROM <table_name> WHERE id IN (?, ?, ?) AND price >= ?;
            params: [(1, 2, 3, 450.69),]

            query: SELECT * FROM <table_name> WHERE id = %s AND price < %s;
            params: [(1, 200.00),]

            query: INSERT INTO <table_name> (id, name, description, price) VALUES (?, ?, ?, ?);
            params: [(1, 'Ryan Gosling', 'Actor', 0.0),]
            for next params it is better to use `executemany`
            params: [(1, 'Ryan Gosling', 'Actor', 0.0), (2, 'Mark Wahlberg', 'No pain no gain', 150.0)]

            query: UPDATE <table_name> SET price = ?, description = ? WHERE name = ?;
            params: [(999.999, 'Best actor', 'Ryan Gosling'),]

            query: DELETE FROM <table_name> WHERE id = ? AND other like ?;
            params: [(404, 200),]
        """

        try:
            self.__verify_cur_open()
            self.__execute_sqream_statement(statement, params=params, data_as=data_as, amount=amount)
            self.__fill_description()
        except Exception as e:
            self.__close_stmt()
            raise e
        finally:
            self.rows_fetched = 0
            self.rows_returned = 0

        return self

    @dbapi_method
    def executemany(self, statement: str, rows_or_cols: list[tuple[Any]] | tuple[[tuple[Any]]] | None = None,
                    data_as: str = 'rows', amount: int | None = None) -> Cursor:
        """
        Execute a statement, preferably used for insertion

        :param statement: str a statement to execute with placeholders
        :param rows_or_cols: list[tuple[Any]] | tuple[tuple[Any]]: sequence of parameters to ingest into query
        :param data_as: string type of passed params. Possible values (`alchemy_flat_list`, `numpy`, `rows` - default)
        :param amount: int - amount of values of given params to insert
        """

        return self.execute(statement, params=rows_or_cols, data_as=data_as, amount=amount)

    @dbapi_method
    def fetchmany(self, size: int = None, data_as: str = 'rows', fetchone: bool = False):
        """
        Fetch an amount of result rows
        """

        size = size or self.arraysize

        if self.statement_type not in (None, 'SELECT'):
            log_and_raise(ProgrammingError, 'No open statement while attempting fetch operation')

        if not self.more_to_fetch:
            if len(self.parsed_rows) == 0:
                return [] if not fetchone else None
        else:
            self.__fetch_and_parse(size, data_as)

        # Get relevant part of parsed rows and reduce storage and counter
        if data_as == 'rows':
            res = self.parsed_rows[0:size if size != -1 else None]
            del self.parsed_rows[:size if size != -1 else None]
            self.buffer.clear()
            self.unsorted_data_columns.clear()

        if logger.isEnabledFor(logging.INFO):
            logger.info(f'Fetched {size} rows')

        return (res if res else []) if not fetchone else (res[0] if res else None)

    @dbapi_method
    def fetchone(self, data_as: str = 'rows'):
        """
        Fetch one result row
        """

        if data_as not in ('rows',):
            log_and_raise(ProgrammingError, "Bad argument to fetchone()")

        return self.fetchmany(1, data_as, fetchone=True)

    @dbapi_method
    def fetchall(self, data_as: str = 'rows'):
        """
        Fetch all result rows
        """

        if data_as not in ('rows',):
            log_and_raise(ProgrammingError, "Bad argument to fetchall()")

        return self.fetchmany(-1, data_as)

    @dbapi_method
    def nextset(self):
        """
        No multiple result sets so currently always returns None
        """

        log_and_raise(NotSupportedError, "Nextset is not supported")

    @dbapi_method
    def setinputsizes(self, sizes):
        log_and_raise(NotSupportedError, "Setinputsizes is not supported")

    @dbapi_method
    def setoutputsize(self, size, column=None):
        log_and_raise(NotSupportedError, "Setoutputsize is not supported")

    @dbapi_method
    def close(self):
        """
        Closes the statement against sqream, cleans the buffer and change the cursor status to closed
        """

        self.__close_stmt()
        self.is_cursor_closed = True

    # Internal Methods
    # ----------------
    def get_statement_type(self) -> str:
        return self.statement_type

    def get_statement_id(self) -> int:
        return self.stmt_id

    def __verify_cur_open(self) -> None:
        if self.is_cursor_closed:
            log_and_raise(ProgrammingError,
                          f"{'Connection' if self.is_connection_initiated_close else 'Cursor'}"
                          f" has been closed")

    def __execute_sqream_statement(self, statement: str, params: list[Any] | tuple[Any] | None = None,
                                   data_as: str = "rows", amount: int | None = None) -> None:
        """
        High-level method overview:
        1) statement preparation + reconnect + execute
        2) queryTypeIn and queryTypeOut
        3) if queryTypeIn isn't empty is means statement was parameterized
        4) collect all information about all columns (such a col types, scales, row_size, etc.) and send it to server
        5) if statement was `select` - perform lists for fetching and do 4 step for queryTypeOut
        """

        self.latest_stmt = statement

        if self.open_statement:
            self.__close_stmt()

        self.open_statement = True
        self.more_to_fetch = True

        self.stmt_id = self.client.get_statement_id()
        self.lb_params = self.client.prepare_statement(statement)

        if self.lb_params.get("reconnect", False):
            # If reconnect exists and issued, close socket, open a new socket with new port/ip sent be the reconnect response
            self.client.reconnect(self.stmt_id, self.connection_id, self.conn_params.database, self.conn_params.service,
                                  self.conn_params.username, self.conn_params.password, self.lb_params["listener_id"], self.lb_params['ip'],
                                  self.lb_params['port_ssl'] if self.conn_params.use_ssl else self.lb_params['port'])

        self.client.execute_statement()
        self.column_list = parameterized_columns = self.client.get_query_type_in()

        if parameterized_columns:
            self.__handle_parameterized(data_as, params, amount)

        self.column_list = self.client.get_query_type_out()

        if self.column_list:  # if there is data in `queryTypeOut`, means it was a `SELECT` query
            self.statement_type = "SELECT"
            self.result_rows = []
            self.parsed_rows = []
            self.data_columns = []
            self.unparsed_row_amount = self.parsed_row_amount = 0
            self.__generate_columns_data()
            self.__fill_col_lists()
        else:
            self.statement_type = "DML"
            self.__close_stmt()

        if logger.isEnabledFor(logging.INFO):
            logger.info(f'Executing statement over connection {self.connection_id} '
                        f'with statement id {self.stmt_id}:\n{statement}')

    def __handle_parameterized(self, data_as: str, params: list[Any] | tuple[Any], amount: int | None) -> None:
        """
        prepares the data and send it to the server
        """

        # Check if arrays are allowed before executing the rest
        if not self.__validate_arrays_usage():
            log_and_raise(ArraysAreDisabled, "Arrays are disabled in this connection.")

        self.__generate_columns_data()
        self.__fill_col_lists()

        self.row_size = sum([sum(self.col_sizes),
                             sum(null for null in self.col_nul if null is True),
                             sum(tvc for tvc in self.col_tvc if tvc is True)
                             ])

        if self.row_size * ROWS_PER_FLUSH <= BYTES_PER_FLUSH_LIMIT:
            self.rows_per_flush = int(ROWS_PER_FLUSH)
        else:
            self.rows_per_flush = int(BYTES_PER_FLUSH_LIMIT / self.row_size)

        self.buffer.clear()

        if data_as == 'alchemy_flat_list':
            # Unflatten SQLalchemy data list
            row_len = len(self.column_list)
            rows_or_cols = [params[i: i + row_len] for i in range(0, len(params), row_len)]
            data_as = 'rows'
        else:
            rows_or_cols = params

        if 'numpy' in repr(type(params[0])):
            data_as = 'numpy'

        column_lengths = [len(row_or_col) for row_or_col in rows_or_cols]

        if column_lengths.count(column_lengths[0]) != len(column_lengths):
            log_and_raise(ProgrammingError,
                          "Incosistent data sequences passed for inserting. "
                          "Please use rows/columns of consistent length")

        if data_as == 'rows':
            self.capacity = amount or len(rows_or_cols)
            self.cols = list(zip(*rows_or_cols))
        else:
            self.cols = rows_or_cols
            self.capacity = len(self.cols)

        self.__send_columns()

    def __fill_col_lists(self) -> None:
        """
        fills the column list information - types, sizes and scales
        """

        self.col_types.clear()
        self.col_sizes.clear()
        self.col_scales.clear()

        for type_tup in self.col_type_tups:
            is_array = 'ftArray' in type_tup
            offset = 0
            _type = type_tup[0]
            if is_array:
                # for array other stuff like scale is shifted in type_tup
                offset = 1
                # Use tuple for ftArray that will be checked
                # only in buffer like 'ftArray' in col_type
                _type = type_tup[0:2]
            self.col_types.append(_type)
            self.col_sizes.append(type_tup[1 + offset] if type_tup[1 + offset] != 0 else TEXT_ITEM_SIZE)
            self.col_scales.append(type_tup[2 + offset])

    def __validate_arrays_usage(self) -> bool:
        """
        Checks if the executing statement uses arrays and if they are allowed.

        Returns:
            bool: False if arrays are not allowed by connection, but used in
              statement, True otherwise.
        """

        if not self.allow_array:
            for col in self.column_list:
                if "ftArray" in col["type"]:
                    return False
        return True

    def __fill_description(self) -> None | List:
        """
        Getting parameters for the cursor's 'description' attribute, even for
        a query that returns no rows. For each column, this includes:
        (name, type_code, display_size, internal_size, precision, scale, null_ok)
        """

        if self.statement_type != 'SELECT':
            self.description = None
            return self.description

        self.description = []
        for col_name, col_nullalbe, col_type_tup in zip(
                self.col_names, self.col_nul, self.col_type_tups):
            type_code = TYPE_MAPPER.get_typecode(col_type_tup[0])  # Convert SQream type to DBAPI identifier
            display_size = internal_size = col_type_tup[
                1]  # Check if other size is available from API
            precision = 38
            scale = col_type_tup[2]

            self.description.append(
                (col_name, type_code, display_size, internal_size, precision,
                 scale, col_nullalbe))

        return self.description

    def __generate_columns_data(self) -> None:
        """
        In order to send data to server in parameterized queries or when we want to fetch data,
        we need to fill all attributes in the list below:
        1) col_names - list of column names
        2) col_tvc - list of `isTrueVarChar` values
        3) col_nul - list of nullable column properties
        4) col_type_tups - list with column types description (type, size, scale)
        5) col_names_map - dictionary with col_name and index (from 0) for every column

        Content could be received from 'queryTypeIn' or 'queryTypeOut' requests
        Server returns a list of columns data that looks like this:
        { "isTrueVarChar": false, "nullable": true, "type": ["ftInt", 4, 0] }
        """

        self.col_names = [col.get("name", "") for col in self.column_list]
        self.col_tvc = [col["isTrueVarChar"] for col in self.column_list]
        self.col_nul = [col["nullable"] for col in self.column_list]
        self.col_type_tups = [col["type"] for col in self.column_list]
        self.col_names_map = {name: idx for idx, name in enumerate(self.col_names)}

    def __send_columns(self) -> None:
        """
        Used for parameterized statements.
        After information about all columns was collected by `_execute_sqream_statement` and
        `_generate_columns_data_for_parameterized_statement` methods

        We need to send these data to server to make it inserts parameters via
        slicing a chunk of columns and pass to _send_column_chunk()
        """

        start_idx = 0
        while self.cols != [()]:
            col_chunk = [col[start_idx:start_idx + self.rows_per_flush] for col in self.cols]
            chunk_len = len(col_chunk[0])
            if chunk_len == 0:
                break
            self.__send_column_chunk(col_chunk, chunk_len)
            start_idx += self.rows_per_flush
            del col_chunk

            if logger.isEnabledFor(logging.INFO):
                logger.info(f'Sent {chunk_len} rows of data')

    def __send_column_chunk(self, cols: List = None, capacity: int = None) -> None:
        """
        Perform parameterized query - "put" json, header, binarized columns. Used by executemany()
        """

        cols = cols or self.cols
        cols = cols if isinstance(cols, (list, tuple, set, dict)) else list(cols)

        capacity = capacity or self.capacity
        # Send columns and metadata to be packed into our buffer
        packed_cols = self.buffer.pack_columns(cols, capacity, self.col_types,
                                               self.col_sizes, self.col_nul,
                                               self.col_tvc, self.col_scales)
        byte_count = functools.reduce(lambda c, n: c + len(n), packed_cols, 0)
        self.client.send_data(capacity, packed_cols, byte_count)

    def __fetch(self):
        """
        sends fetch request to the server, keeps the unsorted data columns list
        """

        fetch_meta = self.client.fetch()
        num_rows_fetched, column_sizes = fetch_meta['rows'], fetch_meta['colSzs']

        if num_rows_fetched == 0:
            self.__close_stmt()
            return num_rows_fetched

        # Get preceding header
        self.client.receive(10)

        # Get data as memoryviews of bytearrays.
        self.unsorted_data_columns = [memoryview(self.client.receive(size)) for idx, size in enumerate(column_sizes)]
        self.unparsed_row_amount = num_rows_fetched

    def __fetch_and_parse(self, requested_row_amount: int, data_as: str = "rows") -> None:
        """
        See if this amount of data is available or a fetch from sqream is required
        -1 - fetch all available data. Used by fetchmany()
        """

        if data_as == 'rows':
            self.buffer.clear()

            self.__fetch()
            self.more_to_fetch = bool(self.unparsed_row_amount)  # _fetch() updates self.unparsed_row_amount

            while (requested_row_amount > len(self.parsed_rows) or requested_row_amount == -1) and self.more_to_fetch:
                unpacked_columns = self.buffer.unpack_columns(
                    unsorted_data_columns=self.unsorted_data_columns,
                    col_types=self.col_types,
                    col_sizes=self.col_sizes,
                    col_nul=self.col_nul,
                    col_tvc=self.col_tvc,
                    col_scales=self.col_scales
                )

                self.parsed_rows.extend(zip(*unpacked_columns))
                self.unparsed_row_amount = 0
                self.__fetch()
                self.more_to_fetch = bool(self.unparsed_row_amount)  # _fetch() updates self.unparsed_row_amount

            self.data_columns.clear()

    def __close_stmt(self) -> None:
        """
        Closes open statement with SQREAM

        Raises:
            ProgrammingError: If server responds with invalid JSON
            ProgrammingError: If server responds with valid JSON,
              but it is not object
            OperationalError: If server responds with "error" key in JSON
        """

        if self.open_statement:
            self.client.close_statement()
            self.open_statement = False
            self.buffer.clear()

            if logger.isEnabledFor(logging.INFO):
                logger.info(f"Done executing statement {self.stmt_id} over connection {self.connection_id}")

from __future__ import annotations

import time
import socket
from typing import Union, List, Dict
from struct import unpack
from pysqream.logger import *
from pysqream.cursor import Cursor
from pysqream.server.sqsocket import SQSocket
from pysqream.server.sqclient import SQClient
from pysqream.server.connection_params import ConnectionParams
from pysqream.utils import NotSupportedError, ProgrammingError, Error, dbapi_method


class Connection:
    """
    Connection class used to interact with SQreamDB.
    The very first connection is called the "base connection".
    For every cursor we open, we create another connection since in sqream every statement should run in its own connection
    This another connection is called "sub connection".
    Every sub connection holds its cursor in cursors dict.
    The base connection holds all sub connections in sub_connections list.
    """

    def __init__(self, conn_params: ConnectionParams, log: bool = False, base_connection: bool = True,
                 reconnect_attempts: int = 3, reconnect_interval: int = 10, allow_array: bool = True):
        self.version: Union[str, None] = None
        self.is_connection_closed: bool = False
        self.connection_id: Union[int, None] = None
        self.connect_to_socket: bool = False
        self.connect_to_database: bool = False
        self.reconnect_attempts: int = reconnect_attempts
        self.reconnect_interval: int = reconnect_interval
        self.base_connection: bool = base_connection
        self.client: Union[SQClient, None] = None
        self.cursors: Dict[int, Cursor] = {}
        self.sub_connections: List[Connection] = []

        # SQreamDB connection parameters attributes
        self.conn_params: ConnectionParams = conn_params
        self.allow_array: bool = allow_array

        self.__validate_attributes()
        self.__open_connection()
        self.__connect_database()

        if log is not False:
            log_and_raise(NotSupportedError, "Logs per Connection are not supported yet")
            # start_logging(None if log is True else log)

    def __enter__(self) -> Connection:
        """
        Implementation for context manager ("with" clause)
        """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Implementation for context manager ("with" clause)
        """

        self.close()

    def __del__(self) -> None:
        """
        Finalizer for connection object. Closes all sub connections and their cursors
        """

        try:
            logger.debug("Try to destroy open connections")
            self.close()
        except Exception as e:
            if "Trying to close a connection that's already closed" not in repr(e):
                log_and_raise(ProgrammingError, e)

    def __iter__(self) -> Connection:
        """
        Implementation for iterating connection in for-in clause
        """

        for sub_conn in self.sub_connections:
            yield sub_conn

    # DB-API Must have methods
    # ------------------------

    @dbapi_method
    def close(self) -> None:
        """
        If we are in base connection - iterate every sub connection and call its close method
        then, for every cursor we have in our connection, we call cursor close method
        """

        if not self.connect_to_database:
            if self.connect_to_socket:
                return self.client.disconnect_socket()
            return

        if self.base_connection:
            for sub_conn in self.sub_connections:
                sub_conn.close()

        for con_id, cursor in self.cursors.items():
            try:
                if not cursor.is_cursor_closed:
                    cursor.is_connection_initiated_close = True
                    cursor.close()
            except Exception as e:
                log_and_raise(Error, f"Can't close connection - {e} for Connection ID {con_id}")

        self.cursors.clear()
        self.sub_connections.clear()
        self.__close_connection()
        self.is_connection_closed = True

    @dbapi_method
    def cursor(self) -> Cursor:
        """
        Create a new sub-connection with the same connection parameters and create a cursor for that sub connection.
        We use a connection as the equivalent of a 'cursor'
        """

        logger.debug("Create cursor")
        self.__verify_con_open()
        sub_conn_params = ConnectionParams(self.conn_params.origin_ip if self.conn_params.clustered else self.conn_params.ip,
                                           self.conn_params.origin_port if self.conn_params.clustered is True else self.conn_params.port,
                                           self.conn_params.database,
                                           self.conn_params.username,
                                           self.conn_params.password,
                                           self.conn_params.clustered,
                                           self.conn_params.use_ssl,
                                           self.conn_params.service)
        sub_conn = Connection(
            sub_conn_params,
            base_connection=False,
            reconnect_attempts=self.reconnect_attempts,
            reconnect_interval=self.reconnect_interval,
            allow_array=self.allow_array
        )
        sub_conn.__verify_con_open()

        cur = Cursor(sub_conn.conn_params, sub_conn.client, sub_conn.connection_id, sub_conn.allow_array)
        sub_conn.cursors[cur.connection_id] = cur

        if self.base_connection:
            self.sub_connections.append(sub_conn)

        return cur

    @dbapi_method
    def commit(self):
        """
        DB-API requires this method, but SQream doesn't support transactions in the traditional sense
        """

        logger.debug("Commit called (not supported for SQreamDB)")

    @dbapi_method
    def rollback(self):
        """
        DB-API requires this method, but SQream doesn't support transactions in the traditional sense
        """

        logger.debug("Rollback called (not supported for SQreamDB)")

    # Internal Methods
    # ----------------
    def __validate_attributes(self):
        if not isinstance(self.reconnect_attempts, int) or self.reconnect_attempts < 0:
            log_and_raise(Exception, f'reconnect attempts should be a positive integer, got : {self.reconnect_attempts}')
        if not isinstance(self.reconnect_interval, int) or self.reconnect_attempts < 0:
            log_and_raise(Exception, f'reconnect interval should be a positive integer, got : {self.reconnect_interval}')

    def __open_connection(self) -> None:
        """
        Get proper ip and port from picker if needed and open a socket to the server. Used at __init__()
        If clustered is true -
         - open a non SSL socker for picker communication
         - Read the first 4 bytes to get readlen and read ip, then read 4 more bytes to get the port

        Then create socket and connect to actual SQreamd server
        """

        if self.conn_params.clustered is True:
            picker_socket = SQSocket(self.conn_params.origin_ip, self.conn_params.origin_port, False)
            self.client = SQClient(picker_socket)
            picker_socket.timeout(5)

            try:
                read_len = unpack('i', self.client.receive(4))[0]
                picker_socket.timeout(None)
                self.conn_params.ip = self.client.receive(read_len)
                self.conn_params.port = unpack('i', self.client.receive(4))[0]
                picker_socket.close()
            except socket.timeout:
                log_and_raise(ProgrammingError, f"Connected with clustered=True, but apparently not a server picker port")

        self.socket = SQSocket(self.conn_params.ip, self.conn_params.port, self.conn_params.use_ssl)
        self.client = SQClient(self.socket)
        self.connect_to_socket = True

    def __connect_database(self) -> None:
        """
        Handle connection to database, with or without server picker
        """

        if self.connect_to_socket:
            try:
                self.connection_id, self.version = self.client.connect_to_socket(self.conn_params.username,
                                                                                 self.conn_params.password,
                                                                                 self.conn_params.database,
                                                                                 self.conn_params.service)
            except KeyError as e:
                log_and_raise(ProgrammingError, str(e))

            if logger.isEnabledFor(logging.INFO):
                logger.info(f'Connection opened to database {self.conn_params.database}. Connection ID: {self.connection_id}')
            self.connect_to_database = True

    def __attempt_reconnect(self) -> bool:
        """
        Attempt to reconnect with exponential backoff
        """

        for attempt in range(self.reconnect_attempts):
            wait_time = self.reconnect_interval * (2 ** attempt)  # Exponential backoff
            logger.info(f"Waiting {wait_time} seconds before reconnect attempt {attempt+1}")
            time.sleep(wait_time)

            try:
                logger.info(f"Reconnect attempt {attempt+1}")
                self.__open_connection()
                self.__connect_database()
                logger.info(f"Reconnection successful on attempt {attempt+1}")
                return True
            except Exception as e:
                logger.error(f"Reconnect attempt {attempt+1} failed: {e}")

        log_and_raise(ConnectionRefusedError, f"All {self.reconnect_attempts} reconnection attempts failed")
        return False

    def __close_connection(self) -> None:
        if self.is_connection_closed:
            log_and_raise(ProgrammingError, f"Trying to close a connection that's already closed for database "
                                            f"{self.conn_params.database} and Connection ID: {self.connection_id}")
        self.client.close_connection()

        if logger.isEnabledFor(logging.INFO):
            logger.info(f'Connection closed to database {self.conn_params.database}. Connection ID: {self.connection_id}')

    def __verify_con_open(self) -> None:
        if self.is_connection_closed:
            log_and_raise(ProgrammingError, "Connection has been closed")

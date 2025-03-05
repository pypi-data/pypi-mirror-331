"""SQream Native Python API"""
import time
from datetime import datetime, date, time as t
from pysqream.connection import Connection
from pysqream.logger import log_and_raise, start_logging, stop_logging
from pysqream.server.connection_params import ConnectionParams


def enable_logs(log_path=None):
    start_logging(None if log_path is True else log_path)


def stop_logs():
    stop_logging()


def connect(host: str, port: int, database: str, username: str, password: str, clustered: bool = False,
            use_ssl: bool = False, service: str = "sqream", log: bool = False, **kwargs):
    """
    Connect to SQream database
    """

    conn_params = ConnectionParams(host, port, database, username, password, clustered, use_ssl, service)
    conn = Connection(conn_params, log=log, base_connection=True, allow_array=kwargs.get("allow_array", True))

    return conn


#  DB-API compatibility
#  -------------------
""" To fully comply to Python's DB-API 2.0 database standard. Ignore when using internally """


class _DBAPITypeObject:
    """DB-API type object which compares equal to all values passed to the constructor.
        https://www.python.org/dev/peps/pep-0249/#implementation-hints-for-module-authors
    """
    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return other in self.values


# Type objects and constructors required by the DB-API 2.0 standard
Binary = memoryview
Date = date
Time = t
Timestamp = datetime


STRING = "STRING"
BINARY = _DBAPITypeObject("BYTES", "RECORD", "STRUCT")
NUMBER = _DBAPITypeObject("INTEGER", "INT64", "FLOAT", "FLOAT64", "NUMERIC",
                          "BOOLEAN", "BOOL")
DATETIME = _DBAPITypeObject("TIMESTAMP", "DATE", "TIME", "DATETIME")
ROWID = "ROWID"


def DateFromTicks(ticks):
    return Date.fromtimestamp(ticks)


def TimeFromTicks(ticks):
    return Time(
        *time.localtime(ticks)[3:6]
    )  # localtime() returns a namedtuple, fields 3-5 are hr/min/sec


def TimestampFromTicks(ticks):
    return Timestamp.fromtimestamp(ticks)


# DB-API global parameters
apilevel = '2.0' 
threadsafety = 1  # Threads can share the module but not a connection
paramstyle = 'qmark'

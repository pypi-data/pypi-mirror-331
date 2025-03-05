"""
Support functions for converting py values to sqream compatible values
and vice versa
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal, getcontext
from math import floor, ceil, pow
from typing import Union
from .globals import SQREAM_OLDEST_DATE_LONG, SQREAM_OLDEST_DATETIME_LONG, SQREAM_OLDEST_DATETIME2, TYPE_MAPPER
from struct import unpack


def pad_dates(num):
    return ('0' if num < 10 else '') + str(num)


def sq_date_to_py_date(sqream_date, is_null=False, date_convert_func=date):

    if is_null:
        return None

    year = (10000 * sqream_date + 14780) // 3652425
    intermed_1 = 365 * year + year // 4 - year // 100 + year // 400
    intermed_2 = sqream_date - intermed_1
    if intermed_2 < 0:
        year = year - 1
        intermed_2 = sqream_date - (365 * year + year // 4 - year // 100 +
                                    year // 400)
    intermed_3 = (100 * intermed_2 + 52) // 3060

    year = year + (intermed_3 + 2) // 12
    month = int((intermed_3 + 2) % 12) + 1
    day = int(intermed_2 - (intermed_3 * 306 + 5) // 10 + 1)

    return date_convert_func(year, month, day)


def sq_datetime_to_py_datetime(sqream_datetime, is_null=False, dt_convert_func=datetime):
    ''' Getting the datetime items involves breaking the long into the date int and time it holds
        The date is extracted in the above, while the time is extracted here  '''

    if is_null:
        return None

    date_part = sqream_datetime >> 32
    time_part = sqream_datetime & 0xffffffff
    date_part = sq_date_to_py_date(date_part, is_null=is_null)

    if date_part is None:
        return None

    msec = time_part % 1000
    sec = (time_part // 1000) % 60
    mins = (time_part // 1000 // 60) % 60
    hour = time_part // 1000 // 60 // 60
    return dt_convert_func(date_part.year, date_part.month, date_part.day,
                           hour, mins, sec, msec * int(pow(10, 3)))  # native python datetime has 6 digits precision (microseconds)
    # while sqream's datetime works with 3 digits precision (milliseconds)


def sq_datetime2_to_numpy_datetime64(datetime2_as_bytes: bytes, is_null: bool = False) -> [Decimal, None]:
    """
    Converts SQream's datetime2 (ftTimestampTz which has nanosecond precision) to numpy's datetime64 (native python datetime supports microseconds, not nanoseconds).
    SQream's datetime2 stores 4 integers (each is 32 bits/4 bytes):
      - 1. date (year, month, day)
      - 2. time (with milliseconds precision)
      - 3. nanoseconds
      - 4. TimeZone

    The strategy is to unpack the 4 integers and construct numpy's datetime64 object which supports nanoseconds precision
    """

    if is_null:
        return None

    utc_offset_seconds, nano_seconds, time_as_int, date_as_int = unpack(TYPE_MAPPER.get_pack_code("ftTimestampTz"), datetime2_as_bytes)

    date_part = sq_date_to_py_date(date_as_int, is_null)
    if date_part is None:
        return None

    time_ns = sq_time_to_ns_since_midnight(time_as_int, nano_seconds)
    date_np = np.datetime64(date_part, 'D')

    datetime_ns = date_np.astype('datetime64[ns]') + np.timedelta64(time_ns, 'ns')
    offset_ns = np.timedelta64(utc_offset_seconds, 's').astype('timedelta64[ns]')

    return datetime_ns + offset_ns


def sq_time_to_ns_since_midnight(time_as_int, nano_seconds):
    """
    Convert SQream integer time and nanoseconds to total nanoseconds since midnight
    """

    hour = time_as_int // (1000 * 60 * 60)
    minutes = (time_as_int // (1000 * 60)) % 60
    seconds = (time_as_int // 1000) % 60
    milliseconds = time_as_int % 1000

    return (
            hour * 3600 * 10**9 +
            minutes * 60 * 10**9 +
            seconds * 10**9 +
            milliseconds * 10**6 +
            nano_seconds
    )


def numpy_datetime64_to_sq_datetime2(np_datetime: Union[np.datetime64, None]) -> tuple[int, int, int, int]:
    """
    Converts numpy's datetime64 to SQream's datetime2 representation as 4 integers that will later on will be packed in bytes.
    The output should contain 4 integers (each 4 bytes):
    - UTC offset in seconds
    - Nanoseconds (only the sub-millisecond part)
    - Time as int (including milliseconds)
    - Date as int
    """

    if np_datetime is None:
        return SQREAM_OLDEST_DATETIME2

    ts = pd.Timestamp(np_datetime)
    utc_offset_seconds = 0
    if ts.tzinfo is not None:
        utc_offset_seconds = int(ts.utcoffset().total_seconds())

    np_datetime = np_datetime.astype('datetime64[ns]')  # ensuring nano seconds precision

    date_part = np_datetime.astype('datetime64[D]')
    ns_since_midnight = (np_datetime - date_part).astype('timedelta64[ns]').astype(np.int64)

    total_milliseconds = ns_since_midnight // 1_000_000
    nano_seconds = int(ns_since_midnight % 1_000_000)  # keeps only sub-millisecond part (nanoseconds precision has 9 digits, we hold here the last 6)

    time_as_int = int(total_milliseconds)  # including milliseconds

    date_as_int = date_to_int(date_part.astype(datetime))

    return utc_offset_seconds, nano_seconds, time_as_int, date_as_int


def _get_date_int(year: int, month: int, day: int) -> int:
    """Convert year, month and day to integer compatible with SQREAM"""
    month: int = (month + 9) % 12
    year: int = year - month // 10
    return (
        365 * year + year // 4 - year // 100 + year // 400
        + (month * 306 + 5) // 10 + (day - 1)
    )


def date_to_int(dat: date) -> int:
    """Convert datetime.date to integer compatible with SQREAM interface"""
    # datetime is also supported because it is descendant of date
    # date_to_int(date(1900, 1, 1)) is 693901 which is the oldest date that
    # sqream supports, so for None use the same
    return SQREAM_OLDEST_DATE_LONG if dat is None else _get_date_int(*dat.timetuple()[:3])


def datetime_to_long(dat: datetime) -> int:
    """Convert datetime.datetime to integer (LONG) compatible with SQREAM"""
    if dat is None:
        # datetime_to_long(datetime(1900, 1, 1)) is 2980282101661696 which is
        # the oldest date that sqream supports, so for None use the same
        return SQREAM_OLDEST_DATETIME_LONG
    year, month, day, hour, minute, second = dat.timetuple()[:6]
    msec = dat.microsecond

    date_int: int = _get_date_int(year, month, day)
    time_int: int = 1000 * (hour * 3600 + minute * 60 + second) + round(msec / 1000)

    return (date_int << 32) + time_int


tenth = Decimal("0.1")
if getcontext().prec < 38:
    getcontext().prec = 38


def sq_numeric_to_decimal(bigint_as_bytes: bytes, scale: int, is_null=False) -> [Decimal, None]:
    if is_null:
        return None

    getcontext().prec = 38
    c = memoryview(bigint_as_bytes).cast('i')
    bigint = ((c[3] << 96) + ((c[2] & 0xffffffff) << 64) + ((c[1] & 0xffffffff) << 32) + (c[0] & 0xffffffff))

    return Decimal(bigint) * (tenth ** scale)


def decimal_to_sq_numeric(dec: Decimal, scale: int) -> int:  # returns bigint
    if getcontext().prec < 38:
        getcontext().prec = 38
    res = dec * (10 ** scale)
    return ceil(res) if res > 0 else floor(res)


def lengths_to_pairs(nvarc_lengths):
    ''' Accumulative sum generator, used for parsing nvarchar columns '''

    idx = new_idx = 0
    for length in nvarc_lengths:
        new_idx += length
        yield idx, new_idx
        idx = new_idx


def arr_lengths_to_pairs(text_lengths):
    """Generator for parsing ARRAY TEXT columns' data"""
    start = 0
    for length in text_lengths:
        yield start, length
        start = length + (8 - length % 8) % 8


def numpy_datetime_str_to_tup(numpy_dt):
    ''' '1970-01-01T00:00:00.699148800' '''

    numpy_dt = repr(numpy_dt).split("'")[1]
    date_part, time_part = numpy_dt.split('T')
    year, month, day = date_part.split('-')
    hms, ns = time_part.split('.')
    hour, mins, sec = hms.split(':')
    return year, month, day, hour, mins, sec, ns


def numpy_datetime_str_to_tup2(numpy_dt):
    ''' '1970-01-01T00:00:00.699148800' '''

    ts = (numpy_dt - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    dt = datetime.utcfromtimestamp(ts)

    return dt.year, dt.month, dt.day

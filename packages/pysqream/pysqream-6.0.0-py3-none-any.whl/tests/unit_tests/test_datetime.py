import pytest
import struct
import numpy as np
from pysqream import casting
from datetime import datetime
from tests.test_base import TestBaseWithoutBeforeAfter


class TestDatetimeUnitTest(TestBaseWithoutBeforeAfter):

    def test_zero_date(self):
        with pytest.raises(Exception, match="year 0 is out of range"):
            casting.sq_date_to_py_date(0, is_null=False)

    def test_zero_datetime(self):
        with pytest.raises(Exception, match="year 0 is out of range"):
            casting.sq_datetime_to_py_datetime(0, is_null=False)

    def test_negative_date(self):
        with pytest.raises(Exception, match="year -9 is out of range"):
            casting.sq_date_to_py_date(-3000, is_null=False)

    def test_negative_datetime(self):
        with pytest.raises(Exception, match="year 0 is out of range"):
            casting.sq_datetime_to_py_datetime(-3000, is_null=False)

    def test_null_date(self):
        res = casting.sq_date_to_py_date(-3000, is_null=True)
        assert res is None, f"Excepted to get None, but got [{res}]"

    def test_null_datetime(self):
        res = casting.sq_datetime_to_py_datetime(-3000, is_null=True)
        assert res is None, f"Excepted to get None, but got [{res}]"

    insert_data = [
        datetime(2015, 12, 24, 13, 11, 23, 0),
        datetime(2015, 12, 31, 23, 59, 59, 999),
        datetime(2015, 12, 24, 13, 11, 23, 1000),
        datetime(2015, 12, 24, 13, 11, 23, 1500),
        datetime(2015, 12, 31, 23, 59, 59, 2000),
    ]
    expected_result = [
        datetime(2015, 12, 24, 13, 11, 23),
        datetime(2015, 12, 31, 23, 59, 59, 1000),
        datetime(2015, 12, 24, 13, 11, 23, 1000),
        datetime(2015, 12, 24, 13, 11, 23, 2000),
        datetime(2015, 12, 31, 23, 59, 59, 2000),
    ]

    @pytest.mark.parametrize("input_datetime, expected_result", zip(insert_data, expected_result))
    def test_datetime_milliseconds_round(self, input_datetime, expected_result):
        """test case for SQ-13969"""

        dt_as_long = casting.datetime_to_long(input_datetime)
        long_as_dt = casting.sq_datetime_to_py_datetime(dt_as_long)

        assert long_as_dt == expected_result


class TestDatetime2UnitTest(TestBaseWithoutBeforeAfter):
    def test_sq_time_to_ns_since_midnight(self):
        # Test cases with different time components
        test_cases = [
            # time_as_int, nano_seconds, expected_ns
            (0, 0, 0),  # midnight, no nanos
            (1000, 456789, 1_000_456_789),  # 1 second + nanos
            (86399123, 456789, 86399123_000_000 + 456789),  # 23:59:59.123 + nanos
        ]

        for time_as_int, nano_seconds, expected_ns in test_cases:
            result = casting.sq_time_to_ns_since_midnight(time_as_int, nano_seconds)
            assert result == expected_ns

    def test_numpy_datetime64_to_sq_datetime2(self):
        # Test regular datetime conversion
        dt = np.datetime64('1997-12-31T23:59:59.123456789', 'ns')
        utc_offset, nanos, time_int, date_int = casting.numpy_datetime64_to_sq_datetime2(dt)

        assert utc_offset == 0
        assert nanos == 456789  # Only sub-millisecond part
        assert time_int == 86399123  # 23:59:59.123
        assert date_int == 729694  # 1997-12-31

        # Test None input
        result = casting.numpy_datetime64_to_sq_datetime2(None)
        assert result == casting.SQREAM_OLDEST_DATETIME2

        # Test midnight
        dt = np.datetime64('2000-01-01T00:00:00', 'ns')
        utc_offset, nanos, time_int, date_int = casting.numpy_datetime64_to_sq_datetime2(dt)
        assert time_int == 0
        assert nanos == 0

    def test_sq_datetime2_to_numpy_datetime64(self):
        # Test case using example bytes
        example_bytes = b'\x00\x00\x00\x00U\xf8\x06\x00\x93X&\x05^"\x0b\x00'
        result = casting.sq_datetime2_to_numpy_datetime64(example_bytes, False)

        # Convert back to verify
        components = casting.numpy_datetime64_to_sq_datetime2(result)
        datetime2_bytes = struct.pack('<iiii', *components)
        assert datetime2_bytes == example_bytes

        # Test null case
        assert casting.sq_datetime2_to_numpy_datetime64(example_bytes, True) is None

    def test_roundtrip_conversion(self):
        """Test that converting to SQream format and back gives the same datetime"""
        original_dt = np.datetime64('1997-12-31T23:59:59.123456789', 'ns')

        # Convert to SQream format
        components = casting.numpy_datetime64_to_sq_datetime2(original_dt)
        datetime2_bytes = struct.pack('<iiii', *components)

        # Convert back
        result_dt = casting.sq_datetime2_to_numpy_datetime64(datetime2_bytes, False)

        assert str(original_dt) == str(result_dt)

    def test_datetime2_timezone_conversions(self):
        """
        checking UTC time, Positive time zone offsets and Negative time zone offsets
        Verifies timezone information is preserved through conversion
        """
        test_cases = [
            np.datetime64('1970-01-17T18:56:04.205739Z', 'ns'),

            np.datetime64('1970-01-17T18:56:04.205739+02:00', 'ns'),
            np.datetime64('1970-01-17T18:56:04.205739+05:30', 'ns'),

            np.datetime64('1970-01-17T18:56:04.205739-05:00', 'ns'),
            np.datetime64('1970-01-17T18:56:04.205739-08:00', 'ns')
        ]

        for dt in test_cases:
            components = casting.numpy_datetime64_to_sq_datetime2(dt)
            datetime2_bytes = struct.pack('<iiii', *components)
            result_dt = casting.sq_datetime2_to_numpy_datetime64(datetime2_bytes, False)

            assert str(dt) == str(result_dt)

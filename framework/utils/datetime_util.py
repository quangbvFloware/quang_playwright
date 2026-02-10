import datetime
import functools
import math
import operator
import time
from typing import Final

from framework.core.config import ProjConfig
from framework.utils.logging_util import logger

# logger = logging.getLogger(PYTHON_CONFIG_LOG)

"""
Documentation
-------------
- Basic date and time types [https://docs.python.org/3/library/datetime.html]

"""

DATE_TIME_FMT_YMD_HMS_FZ = "%Y-%m-%dT%H:%M:%S.%f%z"

_MODIFIED_OFFSET_VAL: Final[float] = 0.0001


def timestamp(digit=0, /, output_ms=False):
    """
    Get current timestamp number in either seconds or milliseconds.
    :param digit: Number of floating point digits
    :param output_ms: Should the output be converted to milliseconds or not.
    """
    if output_ms:
        return math.floor(time.time() * 1000)
    return round(time.time(), ndigits=digit)


def current_date(*, by_format=None):
    """
    Documentation
    -------------
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    :param by_format:
    :return:
    """
    current = datetime.datetime.now()
    if by_format:
        return current.strftime(by_format)
    return current


def move_date_by_number_of_days(days_, /, *, start_date=None, move_back=False, mid_night=False, time_stamp=False):
    op = operator.sub if move_back else operator.add
    _current_date = datetime.datetime.now()
    if start_date:
        _current_date = datetime.datetime.fromisoformat(start_date)

    result = op(_current_date, datetime.timedelta(days=days_))

    if mid_night:
        dict_mid_night = mid_night if isinstance(mid_night, dict) else dict(hour=0, minute=0, second=0, microsecond=0)
        result = result.replace(**dict_mid_night)

    if time_stamp:
        result = result.timestamp()

    return result


def get_current_date(time_format=None, timezone=None):
    date_time = datetime.datetime.now() if not timezone else datetime.datetime.now(timezone)
    return date_time.strftime("%Y%m%d") if time_format is None else date_time.strftime(time_format)


def pretty_time(seconds):
    sign_string = "-" if seconds < 0 else ""
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return "%s%dd %dh %dm %ds" % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return "%s%dh %dm %ds" % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return "%s%dm %ds" % (sign_string, minutes, seconds)
    else:
        return "%s%ds" % (sign_string, seconds)


def format_datetime_now(output_format="%-d/%b/%Y - %H:%M:%S"):
    return datetime.datetime.now().strftime(output_format)


def dav_datetime_now(delta_days=0, delta_hours=0, delta_minutes=0, delta_seconds=0, output_format="%Y%m%dT%H%M%SZ", is_utc=True):
    target_date = datetime.datetime.now() + datetime.timedelta(
        days=delta_days,
        hours=delta_hours,
        minutes=delta_minutes,
        seconds=delta_seconds,
    )
    if is_utc:
        target_date = target_date.astimezone(datetime.timezone.utc)
    return target_date.strftime(output_format)


def format_date_now(output_format="%-d/%b/%Y"):
    return datetime.datetime.now().strftime(output_format)


def format_time_now(output_format="%H:%M:%S"):
    return datetime.datetime.now().strftime(output_format)


def format_time_from_timestamp(time_obj, in_second=True, output_format="%H:%M:%S"):
    timestamp_in_seconds = time_obj if in_second else time_obj / 1000  # Convert from milliseconds to seconds
    get_time = datetime.datetime.fromtimestamp(timestamp_in_seconds).time()

    return get_time.strftime(output_format)


# convert timestamp to local datetime format "%H:%M:%S"
def convert_timestamp_to_local_time(timestamp, timezone=None, output_format="%H:%M:%S") -> str:
    return datetime.datetime.fromtimestamp(timestamp, timezone).strftime(output_format)


def parse_date_time(input_dt_str: str = None, input_dt_fmt: str = DATE_TIME_FMT_YMD_HMS_FZ) -> datetime.datetime:
    """
    Parse datetime string with specified format into datetime object
    :param input_dt_str: The datetime string to be parsed. Put None or empty to return date for timestamp of `0`.
    :param input_dt_fmt: The date format for the input string.
    """
    if not input_dt_str:
        return datetime.datetime.fromtimestamp(0)

    return datetime.datetime.strptime(input_dt_str, input_dt_fmt)


def generate_action_time(*, float_digits: int = 3, loop_iter: int = 1):
    """
    Generate `action_time` number to be placed into payload data.
    :param float_digits: Number of (maximum) floating point digits behind decimal part. Defaults to 3.
    :param loop_iter: Loop iteration number which is added to make unique `action_time` values for each item.
        This param is meaningful only when being placed inside a loop. Defaults to 1.
    """
    iter_float_val: float = loop_iter / (10**float_digits)
    action_time_val: float = timestamp() + iter_float_val
    return round(action_time_val, ndigits=float_digits)


def calc_offset_modified(updated_date: float, /, *, offset_val: float = _MODIFIED_OFFSET_VAL) -> float:
    """
    Calculate a `modified_timestamp` to use for `modified_gte` and `modified_lt` params,
    which helps to limit the data range when dev team reproduces the request.
    Basically, it adds a tiny value to the input updated_date
    """
    return updated_date + offset_val


def calc_offset_modified_by_list(
    data_list: list[dict],
    /,
    *,
    offset_val: float = _MODIFIED_OFFSET_VAL,
    sort_data=None,
    get_period=False,
) -> float | dict:
    """
    Calculate a `modified_timestamp` to use for `modified_gte` and `modified_lt` params,
    which helps to limit the data range when dev team reproduces the request.
    Basically, it adds a tiny value to the last item `updated_date` field.

    :param data_list: The `data[]` list consists of one/many items having `updated_date` field.
    :param offset_val: The TINY_OFFSET value which is added (default is _MODIFIED_OFFSET_VAL)
    :param sort_data: None = not sort; True = sort ASC; False = sort DESC
    :param get_period: Return both modified_gte and modified_lt
    :return: Last item's `updated_date` + TINY_OFFSET for general cases, or zero for any value missing issue.
    """
    # Value '0' is ignored in the GET request, so, it does not break the flow
    default_return: float = 0
    if not data_list:
        return default_return

    if sort_data is not None:
        data_list = sorted(
            data_list,
            key=lambda k: k.get("updated_date", default_return),
            reverse=not sort_data,
        )

    last_item_updated: float = data_list[-1].get("updated_date", default_return)
    added_offset = 0 if last_item_updated == default_return else offset_val

    if get_period:
        first_item_updated = data_list[0].get("updated_date", default_return)
        return dict(
            modified_gte=first_item_updated,
            modified_lt=last_item_updated + added_offset,
        )

    return last_item_updated + added_offset


def wait_for_worker(sleep=None, current_try=1, retries=None, message="for worker in"):
    sleep = sleep or ProjConfig.get_config("sleep") or 5
    retries = retries or ProjConfig.get_config("retries") or 3
    if current_try != retries:
        logger.info(f". . . [Waiting] {message} in " f"{int(sleep) if float(sleep).is_integer() else sleep}s ({current_try})")
        time.sleep(sleep)  # Waiting for worker


def __get_timestamp_delta_from_now__(ops, **kwargs):
    return int(datetime.datetime.timestamp(ops(datetime.datetime.now(), datetime.timedelta(**kwargs))))


get_timestamp_add_delta_from_now = functools.partial(__get_timestamp_delta_from_now__, ops=operator.add)
get_timestamp_sub_delta_from_now = functools.partial(__get_timestamp_delta_from_now__, ops=operator.sub)

del __get_timestamp_delta_from_now__


def convert_date_to_timestamp_in_secs(day_str, date_format=None):
    """
     Converts a date string to a Unix timestamp in seconds.
     @param day_str: The day in string format (e.g., '01-01-2024')
    @param date_format: The format of the input day string:
         Supports two formats:
         - "%d-%m-%Y"
         - "%d-%m-%Y %I:%M:%S %p"
     @return: Unix timestamp in seconds
    """
    supported_formats = [
        "%d-%m-%Y",
        "%d-%m-%Y %I:%M:%S %p",
    ]

    formats_to_try = [date_format] if date_format else supported_formats

    for fmt in formats_to_try:
        try:
            dt = datetime.datetime.strptime(day_str, fmt)
            return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            continue

    raise ValueError(f"Invalid date '{day_str}'. Supported formats are: {supported_formats}")


def convert_iso_to_timestamp(date_str: str, iso_format='%Y%m%dT%H%M%SZ') -> float:
    """Convert a ISO 8601 datetime string (e.g., '20250603T164037Z') to a Unix timestamp."""
    if not date_str:
        return 0
    dt = datetime.datetime.strptime(date_str, iso_format)
    return dt.timestamp()


def convert_utc_iso_to_timestamp(date_str: str, iso_format='%Y%m%dT%H%M%SZ') -> float:
    """Convert a UTC ISO 8601 datetime string (e.g., '20250603T164037Z') to a Unix timestamp."""
    if not date_str:
        return 0
    dt = datetime.datetime.strptime(date_str, iso_format)
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()


def get_timestamp_end_of_today():
    now = datetime.datetime.now()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return int(end_of_day.timestamp())

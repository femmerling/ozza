from datetime import datetime, timedelta


def get_unix_millis(original_timestamp=None):
    """
    Returns unix time in millisecond for a given timestamp.
    If timestamp is not given will use current time
    Args:
        original_timestamp: Datetime object, if None will use current timestamp
    Returns:
        Integer of unixtime in millisecond
    """
    timestamp = original_timestamp if original_timestamp else datetime.utcnow()
    epoch = datetime.utcfromtimestamp(0)
    return int((timestamp - epoch).total_seconds() * 1000)


def get_expiry_time(seconds, created_time):
    """
    Returns expiry time in unix time in millisecond for a given minute and
    Args:
        seconds: Int, expiry time in second
        created_time: Datetime, object to compare for expiry time
    Returns:
        Integer of unixtime in millisecond
    """
    time_to_expire = timedelta(seconds=seconds)
    return get_unix_millis(created_time + time_to_expire)


def current_utctime():
    """
    Returns current utc Datetime object for standardization purposes
    """
    return datetime.utcnow()

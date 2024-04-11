import datetime
import pytz

def get_local_datetime(timestamp, timezone):
    dt = datetime.datetime.fromtimestamp(timestamp)
    tz = pytz.timezone(timezone)
    return tz.localize(dt)

def to_local_minute(timestamp, timezone='America/Los_Angeles'):
    return get_local_datetime(timestamp, timezone).strftime('%Y-%m-%d %H:%M')

def to_local_full_format(timestamp, timezone='America/Los_Angeles'):
    return get_local_datetime(timestamp, timezone).strftime("%Y-%m-%d %H:%M:%S")

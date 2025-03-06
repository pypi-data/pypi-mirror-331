"""
Simple module holding a global commodity function for generating the current timestamp
"""

from datetime import datetime, timezone
from typing import Union


def utcnow() -> int:
    """Return the current UTC timestamp"""
    # TODO: look into this, since apparently we should be using aware
    #   objects, but they give malformed timestamps with .timestamp()
    ts = datetime.now(timezone.utc).replace(tzinfo=None).timestamp()
    return int(ts)


def local_ts_to_utc(ts: Union[int, float]) -> int:
    """convert a local timestamp to a utc one"""

    local_tz = datetime.fromtimestamp(ts).astimezone().tzinfo
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)

    return int(dt.replace(tzinfo=local_tz).timestamp())

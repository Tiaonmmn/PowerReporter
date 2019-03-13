__author__ = "Tiaonmmn.ZMZ"

import struct

from datetime import datetime, timedelta


def filetimeParse(timestamp_bytes) -> datetime:
    '''Thanks to https://stackoverflow.com/questions/10884946/ms-timestamp-parsing-python.
    (in)timestamp_bytes:a byte to parse
    (output)return a datetime object.
    '''
    quadword = struct.unpack('<Q', timestamp_bytes)[0]
    us = quadword // 10 - 11644473600000000
    return datetime(1970, 1, 1) + timedelta(microseconds=us)

#
# tz_datetime.py
#
# A replacement for datetime.py using something like the POSIX TZ environment
# to setup standard and DST timezones.
#
# Usage:
#   import time
#   import tz_datetime as datetime
#   datetime.TZ("MEZ-1MES,M3.5.0,M10.5.0")
#   lt = datetime.localtime(time.time())
#
# Details:
#   see https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
#   https://docs.python.org/3/library/datetime.html
#

import datetime
from datetime import datetime as DT, timedelta as TimeDelta

_TZ = 'MEZ-1MES,M3.5.0,M10.5.0' # Middle Europe

class _DstSwitch:
    def __init__(self, month, week, day):
        self._m = month
        self._w = week
        self._d = day
    def month(self):
        return self._m
    def day(self):
        return self._d
    def week(self):
        return self._w

"""
datetime.tzinfo:
    This is an abstract base class, meaning that this class should not be instantiated directly. Define a subclass of tzinfo to capture information about a particular time zone.
    An instance of (a concrete subclass of) tzinfo can be passed to the constructors for datetime and time objects. The latter objects view their attributes as being in local time, and the tzinfo object supports methods revealing offset of local time from UTC, the name of the time zone, and DST offset, all relative to a date or time object passed to them.
    You need to derive a concrete subclass, and (at least) supply implementations of the standard tzinfo methods needed by the datetime methods you use. The datetime module provides timezone, a simple concrete subclass of tzinfo which can represent timezones with fixed offset from UTC such as UTC itself or North American EST and EDT.
    Special requirement for pickling: A tzinfo subclass must have an __init__() method that can be called with no arguments, otherwise it can be pickled but possibly not unpickled again. This is a technical requirement that may be relaxed in the future.
"""
class tzinfo(datetime.tzinfo):
    def __init__(self, TZ=None):
        # super(TZ_timezone, self).__init__()
        self._std_name = None
        self._dst_name = None
        self._std_offset = None
        self._dst_offset = None
        self._dst_start = None
        self._dst_end = None

    def utcoffset(self, dt):
        """
        Return offset of local time from UTC, as a timedelta object that is positive east of UTC. If local time is west of UTC, this should be negative.
        """
        return TimeDelta(hour = -self._std_offset)

    def dst(self, dt):
        """
        Return the daylight saving time (DST) adjustment, as a timedelta object or None if DST information isn’t known.
        """
        return TimeDelta(hour = -self._dst_offset)

    def tzname(self, dt):
        """
        Return the time zone name corresponding to the datetime object dt, as a string
        """
        if self._std_name is None:
            return "UTC"
    def _is_dst(self, dt):
        st = DT(dt)
        en = DT(dt)
        # simple case. check month only
        st_month = self._dst_start[0]
        en_month = self._dst_end[0]
        if st_month < en_month:
            if dt.month > st_month and dt.month < en_month:
                return True
            elsif dt.month < st_month or dt.month > en_month:
                return True
        else:
            if dt.month > st_month:
                return True
            elsif dt.month < en_month:
                return True
            elsif dt.month > en_month and dt.month < st_month:
                return true

        pass

    def _parse_tz(self, str):

        def parse_change_date(s):
            type = s[0]
            s = s[1:]
            if type == 'J':
                raise NotImplementedError
            if type != 'M':
                raise ValueError
            m,w,d = s.split('.')
            if d is None:
                d = 0
            if w is None:
                w = 5
            return m, w, d

        zones, on_s, off_s = str.split(',')
        if on_s:
            self._dst_start = parse_change_date(on_s)
        if off_s:
            self._dst_end = parse_change_date(off_s)

        # zones = "MEZ-1MES"
        stat = 0
        std_tz = ""
        dst_tz = ""
        std_offset = ""
        dst_offset = ""
        for v in zones:
            numeric = v == '-' or v == '+' or (v >= '0' and v <= '9')
            if stat == 0:
                if numeric:
                    std_offset += v
                    stat = 1
                else:
                    std_tz += v
            elif stat == 1:
                if numeric:
                    std_offset += v
                else:
                    stat = 2
                    dst_tz += v
            elif stat == 2:
                if numeric:
                    dst_offset += v
                    stat = 3
                else:
                    dst_tz += v
            else: # stat == 3
                if numeric:
                    dst_offset += v
                else:
                    raise ValueError
        if not (std_tz and std_offset):
            # no need to use this without SOME information.
            raise ValueError
        self._std_name = std_tz
        self._std_offset = int(std_offset)
        if dst_tz:
            self._dst_name = dst_tz
            if dst_offset:
                self._dst_offset = int(dst_offset)
            else:
                self._dst_offset = self._std_offset - 1



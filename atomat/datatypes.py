import datetime, time
from formless import annotate

class DateTime(annotate.String):
    def __init__(self, *a, **kw):
        super(DateTime, self).__init__(*a, **kw)

    def _datetime(self, t):
        r = datetime.datetime(year=t.tm_year,
                              month=t.tm_mon,
                              day=t.tm_mday,
                              hour=t.tm_hour,
                              minute=t.tm_min,
                              second=t.tm_sec)
        return r

    def _date(self, t):
        r = datetime.date(year=t.tm_year,
                          month=t.tm_mon,
                          day=t.tm_mday)
        return r

    def _parse(self, s):
        FORMATS = [
            # ISO (-inspired)
            ('%Y-%m-%dT%H:%M:%SZ', self._datetime),
            ('%Y-%m-%dT%H:%M:%S', self._datetime),
            ('%Y-%m-%dT%H:%M', self._datetime),
            ('%Y-%m-%d %H:%M:%S', self._datetime),
            ('%Y-%m-%d %H:%M', self._datetime),
            ('%Y-%m-%d', self._date),

            # Finnish
            ('%d.%m.%Y %H:%M:%S', self._datetime),
            ('%d.%m.%Y %H:%M', self._datetime),
            ('%d.%m.%Y', self._date),
            ]

        for fmt, mangle in FORMATS:
            try:
                when = time.strptime(s, fmt)
            except:
                pass
            else:
                r = mangle(when)
                return r
        raise annotate.InputError, 'Unknown time format.' #TODO i18n

    def coerce(self, *a, **kw):
        s = annotate.String.coerce(self, *a, **kw)
        r = self._parse(s)
        return r

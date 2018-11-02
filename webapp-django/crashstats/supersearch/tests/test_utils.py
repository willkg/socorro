import datetime

from django.utils.timezone import utc

from crashstats.topcrashers.views import get_date_boundaries


class TestDateBoundaries(object):
    def test_get_date_boundaries(self):
        # Simple test.
        start, end = get_date_boundaries({
            'date': [
                '>2010-03-01T12:12:12',
                '<=2010-03-10T00:00:00',
            ]
        })
        assert start == datetime.datetime(2010, 3, 1, 12, 12, 12).replace(tzinfo=utc)
        assert end == datetime.datetime(2010, 3, 10).replace(tzinfo=utc)

        # Test with messy dates.
        start, end = get_date_boundaries({
            'date': [
                '>2010-03-01T12:12:12',
                '>2009-01-01T12:12:12',
                '<2010-03-11T00:00:00',
                '<=2010-03-10T00:00:00',
            ]
        })
        assert start == datetime.datetime(2009, 1, 1, 12, 12, 12).replace(tzinfo=utc)
        assert end == datetime.datetime(2010, 3, 11).replace(tzinfo=utc)

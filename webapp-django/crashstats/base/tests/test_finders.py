import copy

import pytest

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command


class TestLeftoverPipelineFinder(object):
    """Test our custom staticfiles finder class."""

    def test_missing_css_source_file(self, settings):
        busted_pipeline = copy.deepcopy(settings.PIPELINE)
        # Doesn't matter which key we chose to bust, so let's just
        # pick the first one.
        key = busted_pipeline['STYLESHEETS'].keys()[0]
        filenames = busted_pipeline['STYLESHEETS'][key]['source_filenames']

        # add a junk one
        filenames += ('neverheardof.css',)
        busted_pipeline['STYLESHEETS'][key]['source_filenames'] = filenames

        settings.PIPELINE = busted_pipeline

        with pytest.raises(ImproperlyConfigured):
            call_command('collectstatic', '--noinput', interactive=False)

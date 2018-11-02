import mock

from django.core.urlresolvers import reverse

from crashstats.sources.views import ALLOWED_SOURCE_HOSTS
from crashstats.crashstats.tests.test_models import Response


class SourcesTestViews(object):
    @mock.patch('requests.get')
    def test_highlight_url(self, client, rget):
        def mocked_get(url, **params):
            if url.endswith('404.h'):
                return Response('Nada', status_code=404)
            return Response("""
//
// Automatically generated by ipdlc.
// Edit at your own risk
//


#include "mozilla/layers/PCompositorBridgeChild.h"
            """)

        rget.side_effect = mocked_get

        url = reverse('sources:highlight_url')

        # No url provided and empty url
        response = client.get(url)
        assert response.status_code == 400
        response = client.get(url, {'url': ''})
        assert response.status_code == 400

        # Bad host
        response = client.get(url, {'url': 'https://example.com/404.h'})
        assert response.status_code == 403

        ok_netloc = ALLOWED_SOURCE_HOSTS[0]

        # Correct host, but bad scheme
        response = client.get(url, {'url': 'ftp://{}/404.h'.format(ok_netloc)})
        assert response.status_code == 403

        # Correct host, but missing page
        response = client.get(url, {'url': 'https://{}/404.h'.format(ok_netloc)})
        assert response.status_code == 404

        # Correct host and correct page
        response = client.get(url, {'url': 'https://{}/200.h'.format(ok_netloc)})
        assert response.status_code == 200

        # Make sure it's really an HTML page.
        assert '</html>' in response.content
        assert response['content-type'] == 'text/html'

        # Our security headers should still be set.
        # Just making sure it gets set. Other tests assert their values.
        assert response['x-frame-options']
        assert response['content-security-policy']

        # Do it also for a file called *.cpp
        response = client.get(url, {'url': 'https://{}/200.cpp'.format(ok_netloc)})
        assert response.status_code == 200

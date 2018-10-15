""" API Tests """
from __future__ import unicode_literals

import unittest

from httmock import HTTMock, all_requests
from wordpress.transport import API_Requests_Wrapper


class TransportTestcases(unittest.TestCase):
    def setUp(self):
        self.requester = API_Requests_Wrapper(
            url='https://woo.test:8888/',
            api='wp-json',
            api_version='wp/v2'
        )

    def test_api_url(self):
        self.assertEqual(
            'https://woo.test:8888/wp-json',
            self.requester.api_url
        )

    def test_endpoint_url(self):
        self.assertEqual(
            'https://woo.test:8888/wp-json/wp/v2/posts',
            self.requester.endpoint_url('posts')
        )

    def test_request(self):
        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 200,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            response = self.requester.request(
                "GET", "https://woo.test:8888/wp-json/wp/v2/posts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.url,
                         'https://woo.test:8888/wp-json/wp/v2/posts')

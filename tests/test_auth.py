""" API Tests """
from __future__ import unicode_literals

import random
import unittest
from collections import OrderedDict
from copy import copy
from tempfile import mkstemp

from httmock import HTTMock, urlmatch
from six import text_type
from six.moves.urllib.parse import parse_qsl, urlparse
from wordpress.api import API
from wordpress.auth import OAuth
from wordpress.helpers import StrUtils, UrlUtils


class BasicAuthTestcases(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8888/wp-api/"
        self.api_name = 'wc-api'
        self.api_ver = 'v3'
        self.endpoint = 'products/26'
        self.signature_method = "HMAC-SHA1"

        self.consumer_key = "ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.consumer_secret = "cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.api_params = dict(
            url=self.base_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            basic_auth=True,
            api=self.api_name,
            version=self.api_ver,
            query_string_auth=False,
        )

    def test_endpoint_url(self):
        api = API(
            **self.api_params
        )
        endpoint_url = api.requester.endpoint_url(self.endpoint)
        endpoint_url = api.auth.get_auth_url(endpoint_url, 'GET')
        self.assertEqual(
            endpoint_url,
            UrlUtils.join_components([
                self.base_url, self.api_name, self.api_ver, self.endpoint
            ])
        )

    def test_query_string_endpoint_url(self):
        query_string_api_params = dict(**self.api_params)
        query_string_api_params.update(dict(query_string_auth=True))
        api = API(
            **query_string_api_params
        )
        endpoint_url = api.requester.endpoint_url(self.endpoint)
        endpoint_url = api.auth.get_auth_url(endpoint_url, 'GET')
        expected_endpoint_url = '%s?consumer_key=%s&consumer_secret=%s' % (
            self.endpoint, self.consumer_key, self.consumer_secret)
        expected_endpoint_url = UrlUtils.join_components(
            [self.base_url, self.api_name, self.api_ver, expected_endpoint_url]
        )
        self.assertEqual(
            endpoint_url,
            expected_endpoint_url
        )
        endpoint_url = api.requester.endpoint_url(self.endpoint)
        endpoint_url = api.auth.get_auth_url(endpoint_url, 'GET')


class OAuthTestcases(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://localhost:8888/wordpress/"
        self.api_name = 'wc-api'
        self.api_ver = 'v3'
        self.endpoint = 'products/99'
        self.signature_method = "HMAC-SHA1"
        self.consumer_key = "ck_681c2be361e415519dce4b65ee981682cda78bc6"
        self.consumer_secret = "cs_b11f652c39a0afd3752fc7bb0c56d60d58da5877"

        self.wcapi = API(
            url=self.base_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            api=self.api_name,
            version=self.api_ver,
            signature_method=self.signature_method
        )

        self.rfc1_api_url = 'https://photos.example.net/'
        self.rfc1_consumer_key = 'dpf43f3p2l4k3l03'
        self.rfc1_consumer_secret = 'kd94hf93k423kf44'
        self.rfc1_oauth_token = 'hh5s93j4hdidpola'
        self.rfc1_signature_method = 'HMAC-SHA1'
        self.rfc1_callback = 'http://printer.example.com/ready'
        self.rfc1_api = API(
            url=self.rfc1_api_url,
            consumer_key=self.rfc1_consumer_key,
            consumer_secret=self.rfc1_consumer_secret,
            api='',
            version='',
            callback=self.rfc1_callback,
            wp_user='',
            wp_pass='',
            oauth1a_3leg=True
        )
        self.rfc1_request_method = 'POST'
        self.rfc1_request_target_url = 'https://photos.example.net/initiate'
        self.rfc1_request_timestamp = '137131200'
        self.rfc1_request_nonce = 'wIjqoS'
        self.rfc1_request_params = [
            ('oauth_consumer_key', self.rfc1_consumer_key),
            ('oauth_signature_method', self.rfc1_signature_method),
            ('oauth_timestamp', self.rfc1_request_timestamp),
            ('oauth_nonce', self.rfc1_request_nonce),
            ('oauth_callback', self.rfc1_callback),
        ]
        self.rfc1_request_signature = b'74KNZJeDHnMBp0EMJ9ZHt/XKycU='

        self.twitter_api_url = "https://api.twitter.com/"
        self.twitter_consumer_secret = \
            "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw"
        self.twitter_consumer_key = "xvz1evFS4wEEPTGEFPHBog"
        self.twitter_signature_method = "HMAC-SHA1"
        self.twitter_api = API(
            url=self.twitter_api_url,
            consumer_key=self.twitter_consumer_key,
            consumer_secret=self.twitter_consumer_secret,
            api='',
            version='1',
            signature_method=self.twitter_signature_method,
        )

        self.twitter_method = "POST"
        self.twitter_target_url = (
            "https://api.twitter.com/1/statuses/update.json?"
            "include_entities=true"
        )
        self.twitter_params_raw = [
            ("status", "Hello Ladies + Gentlemen, a signed OAuth request!"),
            ("include_entities", "true"),
            ("oauth_consumer_key", self.twitter_consumer_key),
            ("oauth_nonce", "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg"),
            ("oauth_signature_method", self.twitter_signature_method),
            ("oauth_timestamp", "1318622958"),
            ("oauth_token",
             "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb"),
            ("oauth_version", "1.0"),
        ]
        self.twitter_param_string = (
            r"include_entities=true&"
            r"oauth_consumer_key=xvz1evFS4wEEPTGEFPHBog&"
            r"oauth_nonce=kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg&"
            r"oauth_signature_method=HMAC-SHA1&"
            r"oauth_timestamp=1318622958&"
            r"oauth_token=370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb&"
            r"oauth_version=1.0&"
            r"status=Hello%20Ladies%20%2B%20Gentlemen%2C%20a%20"
            r"signed%20OAuth%20request%21"
        )
        self.twitter_signature_base_string = (
            r"POST&"
            r"https%3A%2F%2Fapi.twitter.com%2F1%2Fstatuses%2Fupdate.json&"
            r"include_entities%3Dtrue%26"
            r"oauth_consumer_key%3Dxvz1evFS4wEEPTGEFPHBog%26"
            r"oauth_nonce%3DkYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg%26"
            r"oauth_signature_method%3DHMAC-SHA1%26"
            r"oauth_timestamp%3D1318622958%26"
            r"oauth_token%3D370773112-"
            r"GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb%26"
            r"oauth_version%3D1.0%26"
            r"status%3DHello%2520Ladies%2520%252B%2520Gentlemen%252C%2520"
            r"a%2520signed%2520OAuth%2520request%2521"
        )
        self.twitter_token_secret = 'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'
        self.twitter_signing_key = (
            'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&'
            'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'
        )
        self.twitter_oauth_signature = b'tnnArxj06cWHq44gCs1OSKk/jLY='

        self.lexev_consumer_key = 'your_app_key'
        self.lexev_consumer_secret = 'your_app_secret'
        self.lexev_callback = 'http://127.0.0.1/oauth1_callback'
        self.lexev_signature_method = 'HMAC-SHA1'
        self.lexev_version = '1.0'
        self.lexev_api = API(
            url='https://bitbucket.org/',
            api='api',
            version='1.0',
            consumer_key=self.lexev_consumer_key,
            consumer_secret=self.lexev_consumer_secret,
            signature_method=self.lexev_signature_method,
            callback=self.lexev_callback,
            wp_user='',
            wp_pass='',
            oauth1a_3leg=True
        )
        self.lexev_request_method = 'POST'
        self.lexev_request_url = \
            'https://bitbucket.org/api/1.0/oauth/request_token'
        self.lexev_request_nonce = '27718007815082439851427366369'
        self.lexev_request_timestamp = '1427366369'
        self.lexev_request_params = [
            ('oauth_callback', self.lexev_callback),
            ('oauth_consumer_key', self.lexev_consumer_key),
            ('oauth_nonce', self.lexev_request_nonce),
            ('oauth_signature_method', self.lexev_signature_method),
            ('oauth_timestamp', self.lexev_request_timestamp),
            ('oauth_version', self.lexev_version),
        ]
        self.lexev_request_signature = b"iPdHNIu4NGOjuXZ+YCdPWaRwvJY="
        self.lexev_resource_url = (
            'https://api.bitbucket.org/1.0/repositories/st4lk/'
            'django-articles-transmeta/branches'
        )

    def test_get_sign_key(self):
        self.assertEqual(
            StrUtils.to_binary(
                self.wcapi.auth.get_sign_key(self.consumer_secret)),
            StrUtils.to_binary("%s&" % self.consumer_secret)
        )

        self.assertEqual(
            StrUtils.to_binary(self.wcapi.auth.get_sign_key(
                self.twitter_consumer_secret, self.twitter_token_secret)),
            StrUtils.to_binary(self.twitter_signing_key)
        )

    def test_flatten_params(self):
        self.assertEqual(
            StrUtils.to_binary(UrlUtils.flatten_params(
                self.twitter_params_raw)),
            StrUtils.to_binary(self.twitter_param_string)
        )

    def test_sorted_params(self):
        # Example given in oauth.net:
        oauthnet_example_sorted = [
            ('a', '1'),
            ('c', 'hi%%20there'),
            ('f', '25'),
            ('f', '50'),
            ('f', 'a'),
            ('z', 'p'),
            ('z', 't')
        ]

        oauthnet_example = copy(oauthnet_example_sorted)
        random.shuffle(oauthnet_example)

        self.assertEqual(
            UrlUtils.sorted_params(oauthnet_example),
            oauthnet_example_sorted
        )

    def test_get_signature_base_string(self):
        twitter_param_string = OAuth.get_signature_base_string(
            self.twitter_method,
            self.twitter_params_raw,
            self.twitter_target_url
        )
        self.assertEqual(
            twitter_param_string,
            self.twitter_signature_base_string
        )

    def test_generate_oauth_signature(self):

        rfc1_request_signature = self.rfc1_api.auth.generate_oauth_signature(
            self.rfc1_request_method,
            self.rfc1_request_params,
            self.rfc1_request_target_url,
            '%s&' % self.rfc1_consumer_secret
        )
        self.assertEqual(
            text_type(rfc1_request_signature),
            text_type(self.rfc1_request_signature)
        )

        # TEST WITH RFC EXAMPLE 3 DATA

        # TEST WITH TWITTER DATA

        twitter_signature = self.twitter_api.auth.generate_oauth_signature(
            self.twitter_method,
            self.twitter_params_raw,
            self.twitter_target_url,
            self.twitter_signing_key
        )
        self.assertEqual(twitter_signature, self.twitter_oauth_signature)

        # TEST WITH LEXEV DATA

        lexev_request_signature = self.lexev_api.auth.generate_oauth_signature(
            method=self.lexev_request_method,
            params=self.lexev_request_params,
            url=self.lexev_request_url
        )
        self.assertEqual(lexev_request_signature, self.lexev_request_signature)

    def test_add_params_sign(self):
        endpoint_url = self.wcapi.requester.endpoint_url('products?page=2')

        params = OrderedDict()
        params["oauth_consumer_key"] = self.consumer_key
        params["oauth_timestamp"] = "1477041328"
        params["oauth_nonce"] = "166182658461433445531477041328"
        params["oauth_signature_method"] = self.signature_method
        params["oauth_version"] = "1.0"
        params["oauth_callback"] = 'localhost:8888/wordpress'

        signed_url = self.wcapi.auth.add_params_sign(
            "GET", endpoint_url, params)

        signed_url_params = parse_qsl(urlparse(signed_url).query)
        # self.assertEqual('page', signed_url_params[-1][0])
        self.assertIn('page', dict(signed_url_params))


class OAuth3LegTestcases(unittest.TestCase):
    def setUp(self):
        self.consumer_key = "ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.consumer_secret = "cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.api = API(
            url="http://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            oauth1a_3leg=True,
            wp_user='test_user',
            wp_pass='test_pass',
            callback='http://127.0.0.1/oauth1_callback'
        )

    @urlmatch(path=r'.*wp-json.*')
    def woo_api_mock(*args, **kwargs):
        """ URL Mock """
        return {
            'status_code': 200,
            'content': b"""
                {
                    "name": "Wordpress",
                    "description": "Just another WordPress site",
                    "url": "http://localhost:8888/wordpress",
                    "home": "http://localhost:8888/wordpress",
                    "namespaces": [
                        "wp/v2",
                        "oembed/1.0",
                        "wc/v1"
                    ],
                    "authentication": {
                        "oauth1": {
                            "request":
                            "http://localhost:8888/wordpress/oauth1/request",
                            "authorize":
                            "http://localhost:8888/wordpress/oauth1/authorize",
                            "access":
                            "http://localhost:8888/wordpress/oauth1/access",
                            "version": "0.1"
                        }
                    }
                }
            """
        }

    @urlmatch(path=r'.*oauth.*')
    def woo_authentication_mock(*args, **kwargs):
        """ URL Mock """
        return {
            'status_code': 200,
            'content':
            b"""oauth_token=XXXXXXXXXXXX&oauth_token_secret=YYYYYYYYYYYY"""
        }

    def test_get_sign_key(self):
        oauth_token_secret = "PNW9j1yBki3e7M7EqB5qZxbe9n5tR6bIIefSMQ9M2pdyRI9g"

        key = self.api.auth.get_sign_key(
            self.consumer_secret, oauth_token_secret)
        self.assertEqual(
            StrUtils.to_binary(key),
            StrUtils.to_binary("%s&%s" %
                               (self.consumer_secret, oauth_token_secret))
        )

    def test_auth_discovery(self):

        with HTTMock(self.woo_api_mock):
            # call requests
            authentication = self.api.auth.authentication
        self.assertEquals(
            authentication,
            {
                "oauth1": {
                    "request":
                    "http://localhost:8888/wordpress/oauth1/request",
                    "authorize":
                    "http://localhost:8888/wordpress/oauth1/authorize",
                    "access":
                    "http://localhost:8888/wordpress/oauth1/access",
                    "version": "0.1"
                }
            }
        )

    def test_get_request_token(self):

        with HTTMock(self.woo_api_mock):
            authentication = self.api.auth.authentication
            self.assertTrue(authentication)

        with HTTMock(self.woo_authentication_mock):
            request_token, request_token_secret = \
                self.api.auth.get_request_token()
            self.assertEquals(request_token, 'XXXXXXXXXXXX')
            self.assertEquals(request_token_secret, 'YYYYYYYYYYYY')

    def test_store_access_creds(self):
        _, creds_store_path = mkstemp(
            "wp-api-python-test-store-access-creds.json")
        api = API(
            url="http://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            oauth1a_3leg=True,
            wp_user='test_user',
            wp_pass='test_pass',
            callback='http://127.0.0.1/oauth1_callback',
            access_token='XXXXXXXXXXXX',
            access_token_secret='YYYYYYYYYYYY',
            creds_store=creds_store_path
        )
        api.auth.store_access_creds()

        with open(creds_store_path) as creds_store_file:
            self.assertEqual(
                creds_store_file.read(),
                ('{"access_token": "XXXXXXXXXXXX", '
                 '"access_token_secret": "YYYYYYYYYYYY"}')
            )

    def test_retrieve_access_creds(self):
        _, creds_store_path = mkstemp(
            "wp-api-python-test-store-access-creds.json")
        with open(creds_store_path, 'w+') as creds_store_file:
            creds_store_file.write(
                ('{"access_token": "XXXXXXXXXXXX", '
                 '"access_token_secret": "YYYYYYYYYYYY"}'))

        api = API(
            url="http://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            oauth1a_3leg=True,
            wp_user='test_user',
            wp_pass='test_pass',
            callback='http://127.0.0.1/oauth1_callback',
            creds_store=creds_store_path
        )

        api.auth.retrieve_access_creds()

        self.assertEqual(
            api.auth.access_token,
            'XXXXXXXXXXXX'
        )

        self.assertEqual(
            api.auth.access_token_secret,
            'YYYYYYYYYYYY'
        )


if __name__ == '__main__':
    unittest.main()

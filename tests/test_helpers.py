""" API Tests """
from __future__ import unicode_literals

import unittest

from six import text_type
from wordpress.helpers import SeqUtils, StrUtils, UrlUtils


class HelperTestcase(unittest.TestCase):
    def setUp(self):
        self.test_url = (
            "http://ich.local:8888/woocommerce/wc-api/v3/products?"
            "filter%5Blimit%5D=2&"
            "oauth_consumer_key=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&"
            "oauth_nonce=c4f2920b0213c43f2e8d3d3333168ec4a22222d1&"
            "oauth_signature=3ibOjMuhj6JGnI43BQZGniigHh8%3D&"
            "oauth_signature_method=HMAC-SHA1&"
            "oauth_timestamp=1481601370&page=2"
        )

    def test_url_is_ssl(self):
        self.assertTrue(UrlUtils.is_ssl("https://woo.test:8888"))
        self.assertFalse(UrlUtils.is_ssl("http://woo.test:8888"))

    def test_url_substitute_query(self):
        self.assertEqual(
            UrlUtils.substitute_query(
                "https://woo.test:8888/sdf?param=value", "newparam=newvalue"),
            "https://woo.test:8888/sdf?newparam=newvalue"
        )
        self.assertEqual(
            UrlUtils.substitute_query("https://woo.test:8888/sdf?param=value"),
            "https://woo.test:8888/sdf"
        )
        self.assertEqual(
            UrlUtils.substitute_query(
                "https://woo.test:8888/sdf?param=value",
                "newparam=newvalue&othernewparam=othernewvalue"
            ),
            (
                "https://woo.test:8888/sdf?newparam=newvalue&"
                "othernewparam=othernewvalue"
            )
        )
        self.assertEqual(
            UrlUtils.substitute_query(
                "https://woo.test:8888/sdf?param=value",
                "newparam=newvalue&othernewparam=othernewvalue"
            ),
            (
                "https://woo.test:8888/sdf?newparam=newvalue&"
                "othernewparam=othernewvalue"
            )
        )

    def test_url_add_query(self):
        self.assertEqual(
            "https://woo.test:8888/sdf?param=value&newparam=newvalue",
            UrlUtils.add_query(
                "https://woo.test:8888/sdf?param=value", 'newparam', 'newvalue'
            )
        )

    def test_url_join_components(self):
        self.assertEqual(
            'https://woo.test:8888/wp-json',
            UrlUtils.join_components(['https://woo.test:8888/', '', 'wp-json'])
        )
        self.assertEqual(
            'https://woo.test:8888/wp-json/wp/v2',
            UrlUtils.join_components(
                ['https://woo.test:8888/', 'wp-json', 'wp/v2'])
        )

    def test_url_get_php_value(self):
        self.assertEqual(
            '1',
            UrlUtils.get_value_like_as_php(True)
        )
        self.assertEqual(
            '',
            UrlUtils.get_value_like_as_php(False)
        )
        self.assertEqual(
            'asd',
            UrlUtils.get_value_like_as_php('asd')
        )
        self.assertEqual(
            '1',
            UrlUtils.get_value_like_as_php(1)
        )
        self.assertEqual(
            '1',
            UrlUtils.get_value_like_as_php(1.0)
        )
        self.assertEqual(
            '1.1',
            UrlUtils.get_value_like_as_php(1.1)
        )

    def test_url_get_query_dict_singular(self):
        result = UrlUtils.get_query_dict_singular(self.test_url)
        self.assertEquals(
            result,
            {
                'filter[limit]': '2',
                'oauth_nonce': 'c4f2920b0213c43f2e8d3d3333168ec4a22222d1',
                'oauth_timestamp': '1481601370',
                'oauth_consumer_key':
                    'ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_signature': '3ibOjMuhj6JGnI43BQZGniigHh8=',
                'page': '2'
            }
        )

    def test_url_get_query_singular(self):
        result = UrlUtils.get_query_singular(
            self.test_url, 'oauth_consumer_key')
        self.assertEqual(
            result,
            'ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        )
        result = UrlUtils.get_query_singular(self.test_url, 'filter[limit]')
        self.assertEqual(
            text_type(result),
            text_type(2)
        )

    def test_url_set_query_singular(self):
        result = UrlUtils.set_query_singular(self.test_url, 'filter[limit]', 3)
        expected = (
            "http://ich.local:8888/woocommerce/wc-api/v3/products?"
            "filter%5Blimit%5D=3&"
            "oauth_consumer_key=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&"
            "oauth_nonce=c4f2920b0213c43f2e8d3d3333168ec4a22222d1&"
            "oauth_signature=3ibOjMuhj6JGnI43BQZGniigHh8%3D&"
            "oauth_signature_method=HMAC-SHA1&oauth_timestamp=1481601370&"
            "page=2"
        )
        self.assertEqual(result, expected)

    def test_url_del_query_singular(self):
        result = UrlUtils.del_query_singular(self.test_url, 'filter[limit]')
        expected = (
            "http://ich.local:8888/woocommerce/wc-api/v3/products?"
            "oauth_consumer_key=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&"
            "oauth_nonce=c4f2920b0213c43f2e8d3d3333168ec4a22222d1&"
            "oauth_signature=3ibOjMuhj6JGnI43BQZGniigHh8%3D&"
            "oauth_signature_method=HMAC-SHA1&"
            "oauth_timestamp=1481601370&"
            "page=2"
        )
        self.assertEqual(result, expected)

    def test_url_remove_default_port(self):
        self.assertEqual(
            UrlUtils.remove_default_port('http://www.gooogle.com:80/'),
            'http://www.gooogle.com/'
        )
        self.assertEqual(
            UrlUtils.remove_default_port('http://www.gooogle.com:18080/'),
            'http://www.gooogle.com:18080/'
        )

    def test_seq_filter_true(self):
        self.assertEquals(
            ['a', 'b', 'c', 'd'],
            SeqUtils.filter_true([None, 'a', False, 'b', 'c', 'd'])
        )

    def test_str_remove_tail(self):
        self.assertEqual(
            'sdf',
            StrUtils.remove_tail('sdf/', '/')
        )

    def test_str_remove_head(self):
        self.assertEqual(
            'sdf',
            StrUtils.remove_head('/sdf', '/')
        )

        self.assertEqual(
            'sdf',
            StrUtils.decapitate('sdf', '/')
        )

""" API Tests """
from __future__ import unicode_literals

import os
import random
import unittest

import requests

import six
import wordpress
from httmock import HTTMock, all_requests
from six import text_type
from wordpress import __default_api__, __default_api_version__, auth
from wordpress.api import API
from wordpress.auth import Auth
from wordpress.helpers import StrUtils, UrlUtils

from . import CURRENT_TIMESTAMP, SHITTY_NONCE


class WordpressTestCase(unittest.TestCase):
    """Test case for the mocked client methods."""

    def setUp(self):
        self.consumer_key = "ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.consumer_secret = "cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.api = wordpress.API(
            url="http://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )

    def test_api(self):
        """ Test default API """
        api = wordpress.API(
            url="https://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )

        self.assertEqual(api.namespace, __default_api__)

    def test_version(self):
        """ Test default version """
        api = wordpress.API(
            url="https://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )

        self.assertEqual(api.version, __default_api_version__)

    def test_non_ssl(self):
        """ Test non-ssl """
        api = wordpress.API(
            url="http://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )
        self.assertFalse(api.is_ssl)

    def test_with_ssl(self):
        """ Test non-ssl """
        api = wordpress.API(
            url="https://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret
        )
        self.assertTrue(api.is_ssl, True)

    def test_with_timeout(self):
        """ Test non-ssl """
        api = wordpress.API(
            url="https://woo.test",
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            timeout=10,
        )
        self.assertEqual(api.timeout, 10)

        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 200,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            status = api.get("products").status_code
        self.assertEqual(status, 200)

    def test_get(self):
        """ Test GET requests """
        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 200,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            status = self.api.get("products").status_code
        self.assertEqual(status, 200)

    def test_post(self):
        """ Test POST requests """
        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 201,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            status = self.api.post("products", {}).status_code
        self.assertEqual(status, 201)

    def test_put(self):
        """ Test PUT requests """
        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 200,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            status = self.api.put("products", {}).status_code
        self.assertEqual(status, 200)

    def test_delete(self):
        """ Test DELETE requests """
        @all_requests
        def woo_test_mock(*args, **kwargs):
            """ URL Mock """
            return {'status_code': 200,
                    'content': b'OK'}

        with HTTMock(woo_test_mock):
            # call requests
            status = self.api.delete("products").status_code
        self.assertEqual(status, 200)

    # @unittest.skip("going by RRC 5849 sorting instead")
    def test_oauth_sorted_params(self):
        """ Test order of parameters for OAuth signature """
        def check_sorted(keys, expected):
            params = auth.OrderedDict()
            for key in keys:
                params[key] = ''

            params = UrlUtils.sorted_params(params)
            ordered = [key for key, value in params]
            self.assertEqual(ordered, expected)

        check_sorted(['a', 'b'], ['a', 'b'])
        check_sorted(['b', 'a'], ['a', 'b'])
        check_sorted(['a', 'b[a]', 'b[b]', 'b[c]', 'c'],
                     ['a', 'b[a]', 'b[b]', 'b[c]', 'c'])
        check_sorted(['a', 'b[c]', 'b[a]', 'b[b]', 'c'],
                     ['a', 'b[c]', 'b[a]', 'b[b]', 'c'])
        check_sorted(['d', 'b[c]', 'b[a]', 'b[b]', 'c'],
                     ['b[c]', 'b[a]', 'b[b]', 'c', 'd'])
        check_sorted(['a1', 'b[c]', 'b[a]', 'b[b]', 'a2'],
                     ['a1', 'a2', 'b[c]', 'b[a]', 'b[b]'])


class WCApiTestCasesBase(unittest.TestCase):
    """ Base class for WC API Test cases """

    def setUp(self):
        Auth.force_timestamp = CURRENT_TIMESTAMP
        Auth.force_nonce = SHITTY_NONCE
        self.api_params = {
            'url': 'http://localhost:8083/',
            'api': 'wc-api',
            'version': 'v3',
            'consumer_key': 'ck_659f6994ae88fed68897f9977298b0e19947979a',
            'consumer_secret': 'cs_9421d39290f966172fef64ae18784a2dc7b20976',
        }


class WCApiTestCasesLegacy(WCApiTestCasesBase):
    """ Tests for WC API V3 """

    def setUp(self):
        super(WCApiTestCasesLegacy, self).setUp()
        self.api_params['version'] = 'v3'
        self.api_params['api'] = 'wc-api'

    def test_APIGet(self):
        wcapi = API(**self.api_params)
        response = wcapi.get('products')
        # print UrlUtils.beautify_response(response)
        self.assertIn(response.status_code, [200, 201])
        response_obj = response.json()
        self.assertIn('products', response_obj)
        self.assertEqual(len(response_obj['products']), 10)
        # print "test_APIGet", response_obj

    def test_APIGetWithSimpleQuery(self):
        wcapi = API(**self.api_params)
        response = wcapi.get('products?page=2')
        # print UrlUtils.beautify_response(response)
        self.assertIn(response.status_code, [200, 201])

        response_obj = response.json()
        self.assertIn('products', response_obj)
        self.assertEqual(len(response_obj['products']), 8)
        # print "test_ApiGenWithSimpleQuery", response_obj

    def test_APIGetWithComplexQuery(self):
        wcapi = API(**self.api_params)
        response = wcapi.get('products?page=2&filter%5Blimit%5D=2')
        self.assertIn(response.status_code, [200, 201])
        response_obj = response.json()
        self.assertIn('products', response_obj)
        self.assertEqual(len(response_obj['products']), 2)

        response = wcapi.get(
            'products?'
            'oauth_consumer_key=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&'
            'oauth_nonce=037470f3b08c9232b0888f52cb9d4685b44d8fd1&'
            'oauth_signature=wrKfuIjbwi%2BTHynAlTP4AssoPS0%3D&'
            'oauth_signature_method=HMAC-SHA1&'
            'oauth_timestamp=1481606275&'
            'filter%5Blimit%5D=3'
        )
        self.assertIn(response.status_code, [200, 201])
        response_obj = response.json()
        self.assertIn('products', response_obj)
        self.assertEqual(len(response_obj['products']), 3)

    def test_APIPutWithSimpleQuery(self):
        wcapi = API(**self.api_params)
        response = wcapi.get('products')
        first_product = (response.json())['products'][0]
        original_title = first_product['title']
        product_id = first_product['id']

        nonce = b"%f" % (random.random())
        response = wcapi.put('products/%s?filter%%5Blimit%%5D=5' %
                             (product_id),
                             {"product": {"title": text_type(nonce)}})
        request_params = UrlUtils.get_query_dict_singular(response.request.url)
        response_obj = response.json()
        self.assertEqual(response_obj['product']['title'], text_type(nonce))
        self.assertEqual(request_params['filter[limit]'], text_type(5))

        wcapi.put('products/%s' % (product_id),
                  {"product": {"title": original_title}})


class WCApiTestCases(WCApiTestCasesBase):
    oauth1a_3leg = False
    """ Tests for New wp-json/wc/v2 API """

    def setUp(self):
        super(WCApiTestCases, self).setUp()
        self.api_params['version'] = 'wc/v2'
        self.api_params['api'] = 'wp-json'
        self.api_params['callback'] = 'http://127.0.0.1/oauth1_callback'
        if self.oauth1a_3leg:
            self.api_params['oauth1a_3leg'] = True

    # @debug_on()
    def test_APIGet(self):
        wcapi = API(**self.api_params)
        per_page = 10
        response = wcapi.get('products?per_page=%d' % per_page)
        self.assertIn(response.status_code, [200, 201])
        response_obj = response.json()
        self.assertEqual(len(response_obj), per_page)

    def test_APIPutWithSimpleQuery(self):
        wcapi = API(**self.api_params)
        response = wcapi.get('products')
        first_product = (response.json())[0]
        # from pprint import pformat
        # print "first product %s" % pformat(response.json())
        original_title = first_product['name']
        product_id = first_product['id']

        nonce = b"%f" % (random.random())
        response = wcapi.put('products/%s?page=2&per_page=5' %
                             (product_id), {"name": text_type(nonce)})
        request_params = UrlUtils.get_query_dict_singular(response.request.url)
        response_obj = response.json()
        self.assertEqual(response_obj['name'], text_type(nonce))
        self.assertEqual(request_params['per_page'], '5')

        wcapi.put('products/%s' % (product_id), {"name": original_title})

    @unittest.skipIf(six.PY2, "non-utf8 bytes not supported in python2")
    def test_APIPostWithBytesQuery(self):
        wcapi = API(**self.api_params)
        nonce = b"%f\xff" % random.random()

        data = {
            "name": nonce,
            "type": "simple",
        }

        response = wcapi.post('products', data)
        response_obj = response.json()
        product_id = response_obj.get('id')

        expected = StrUtils.to_text(nonce, encoding='ascii', errors='replace')

        self.assertEqual(
            response_obj.get('name'),
            expected,
        )
        wcapi.delete('products/%s' % product_id)

    @unittest.skipIf(six.PY2, "non-utf8 bytes not supported in python2")
    def test_APIPostWithLatin1Query(self):
        wcapi = API(**self.api_params)
        nonce = "%f\u00ae" % random.random()

        data = {
            "name": nonce.encode('latin-1'),
            "type": "simple",
        }

        response = wcapi.post('products', data)
        response_obj = response.json()
        product_id = response_obj.get('id')

        expected = StrUtils.to_text(
            StrUtils.to_binary(nonce, encoding='latin-1'),
            encoding='ascii', errors='replace'
        )

        self.assertEqual(
            response_obj.get('name'),
            expected
        )
        wcapi.delete('products/%s' % product_id)

    def test_APIPostWithUTF8Query(self):
        wcapi = API(**self.api_params)
        nonce = "%f\u00ae" % random.random()

        data = {
            "name": nonce.encode('utf8'),
            "type": "simple",
        }

        response = wcapi.post('products', data)
        response_obj = response.json()
        product_id = response_obj.get('id')
        self.assertEqual(response_obj.get('name'), nonce)
        wcapi.delete('products/%s' % product_id)

    def test_APIPostWithUnicodeQuery(self):
        wcapi = API(**self.api_params)
        nonce = "%f\u00ae" % random.random()

        data = {
            "name": nonce,
            "type": "simple",
        }

        response = wcapi.post('products', data)
        response_obj = response.json()
        product_id = response_obj.get('id')
        self.assertEqual(response_obj.get('name'), nonce)
        wcapi.delete('products/%s' % product_id)


@unittest.skip("these simply don't work for some reason")
class WCApiTestCases3Leg(WCApiTestCases):
    """ Tests for New wp-json/wc/v2 API with 3-leg """
    oauth1a_3leg = True


class WPAPITestCasesBase(unittest.TestCase):
    api_params = {
        'url': 'http://localhost:8083/',
        'api': 'wp-json',
        'version': 'wp/v2',
        'consumer_key': 'tYG1tAoqjBEM',
        'consumer_secret': 's91fvylVrqChwzzDbEJHEWyySYtAmlIsqqYdjka1KyVDdAyB',
        'callback': 'http://127.0.0.1/oauth1_callback',
        'wp_user': 'admin',
        'wp_pass': 'admin',
        'oauth1a_3leg': True,
    }

    def setUp(self):
        Auth.force_timestamp = CURRENT_TIMESTAMP
        Auth.force_nonce = SHITTY_NONCE
        self.wpapi = API(**self.api_params)

    # @debug_on()
    def test_APIGet(self):
        response = self.wpapi.get('users/me')
        self.assertIn(response.status_code, [200, 201])
        response_obj = response.json()
        self.assertEqual(response_obj['name'], self.api_params['wp_user'])

    def test_APIGetWithSimpleQuery(self):
        response = self.wpapi.get('pages?page=2&per_page=2')
        self.assertIn(response.status_code, [200, 201])

        response_obj = response.json()
        self.assertEqual(len(response_obj), 2)

    def test_APIPostData(self):
        nonce = "%f\u00ae" % random.random()

        content = "api test post"

        data = {
            "title": nonce,
            "content": content,
            "excerpt": content
        }

        response = self.wpapi.post('posts', data)
        response_obj = response.json()
        post_id = response_obj.get('id')
        self.assertEqual(response_obj.get('title').get('raw'), nonce)
        self.wpapi.delete('posts/%s' % post_id)

    def test_APIPostBadData(self):
        """
        No excerpt so should fail to be created.
        """
        nonce = "%f\u00ae" % random.random()

        data = {
            'a': nonce
        }

        with self.assertRaises(UserWarning):
            self.wpapi.post('posts', data)

    def test_APIPostMedia(self):
        img_path = 'tests/data/test.jpg'
        with open(img_path, 'rb') as test_file:
            img_data = test_file.read()
        img_name = os.path.basename(img_path)

        res = self.wpapi.post(
            'media',
            data=img_data,
            headers={
                'Content-Type': 'image/jpg',
                'Content-Disposition' : 'attachment; filename=%s'% img_name
            }
        )

        self.assertEqual(res.status_code, 201)
        res_obj = res.json()
        created_id = res_obj.get('id')
        self.assertTrue(created_id)
        uploaded_res = requests.get(res_obj.get('source_url'))

        # check for bug where image bytestream was quoted
        self.assertNotEqual(StrUtils.to_binary(uploaded_res.text[0]), b'"')

        self.wpapi.delete('media/%s?force=True' % created_id)

    # def test_APIPostMediaBadCreds(self):
    #     """
    #     TODO: make sure the warning is "ensure login and basic auth is installed"
    #     """
    #     img_path = 'tests/data/test.jpg'
    #     with open(img_path, 'rb') as test_file:
    #         img_data = test_file.read()
    #     img_name = os.path.basename(img_path)
    #     res = self.wpapi.post(
    #         'media',
    #         data=img_data,
    #         headers={
    #             'Content-Type': 'image/jpg',
    #             'Content-Disposition' : 'attachment; filename=%s'% img_name
    #         }
    #     )


class WPAPITestCasesBasic(WPAPITestCasesBase):
    api_params = dict(**WPAPITestCasesBase.api_params)
    api_params.update({
        'user_auth': True,
        'basic_auth': True,
        'query_string_auth': False,
    })


class WPAPITestCases3leg(WPAPITestCasesBase):

    api_params = dict(**WPAPITestCasesBase.api_params)
    api_params.update({
        'creds_store': '~/wc-api-creds-test.json',
    })

    def setUp(self):
        super(WPAPITestCases3leg, self).setUp()
        self.wpapi.auth.clear_stored_creds()

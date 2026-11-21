import base64
import io
import json
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request
from unittest.mock import patch

from nvoip import NvoipClient
from nvoip.client import NvoipError, _SameOriginRedirectHandler

class ClientTests(unittest.TestCase):
    def record(self, action):
        with patch('nvoip.client.build_opener') as build_opener:
            request = build_opener.return_value.open
            response = request.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b'{}'
            action()
            self.assertIsInstance(build_opener.call_args.args[0], _SameOriginRedirectHandler)
        return request.call_args.args[0]

    def test_client_credentials_form_and_special_characters(self):
        client = NvoipClient(oauth_client_id='client: &+á', oauth_client_secret='dummy: &+é')
        sent = self.record(client.create_client_credentials_token)
        self.assertEqual(sent.full_url, 'https://api.nvoip.com.br/auth/oauth2/token')
        self.assertEqual(sent.get_header('User-agent'), 'Nvoip-Python/3.0.1')
        self.assertEqual(sent.get_header('Content-type'), 'application/x-www-form-urlencoded')
        self.assertEqual(parse_qs(sent.data.decode()), {'grant_type': ['client_credentials']})
        actual = base64.b64decode(sent.get_header('Authorization')[6:]).decode()
        self.assertEqual(actual, quote_plus('client: &+á') + ':' + quote_plus('dummy: &+é'))

    def test_refresh_form_round_trip(self):
        client = NvoipClient(oauth_client_id='client', oauth_client_secret='dummy')
        sent = self.record(lambda: client.refresh_access_token('dummy&+á'))
        self.assertEqual(sent.full_url, 'https://api.nvoip.com.br/auth/oauth2/token')
        self.assertEqual(parse_qs(sent.data.decode())['refresh_token'], ['dummy&+á'])

    def test_balance_and_otp_confirmation_have_bearer(self):
        client = NvoipClient()
        sent = self.record(lambda: client.get_balance('dummy'))
        self.assertEqual(sent.full_url, 'https://api.nvoip.com.br/v3/balance')
        self.assertEqual(sent.get_header('Authorization'), 'Bearer dummy')
        sent = self.record(lambda: client.check_otp('001122', 'key&+á', 'dummy'))
        self.assertEqual(parse_qs(urlparse(sent.full_url).query)['key'], ['key&+á'])
        self.assertNotIn('napikey', sent.full_url)
        self.assertEqual(sent.get_header('Authorization'), 'Bearer dummy')

    def test_otp_payload_and_http_error(self):
        client = NvoipClient()
        payload = {'phoneNumber': '11999990000', 'methods': {'sms': True}}
        sent = self.record(lambda: client.send_otp(payload, 'dummy'))
        self.assertEqual(json.loads(sent.data), payload)
        with patch('nvoip.client.build_opener') as build_opener:
            build_opener.return_value.open.side_effect = HTTPError(
                'https://example.invalid', 401, 'denied', {}, io.BytesIO(b'{"error":"denied"}')
            )
            with self.assertRaises(NvoipError) as error: client.get_balance('dummy')
        self.assertEqual(error.exception.status, 401)

    def test_missing_client_credentials_fail_before_transport(self):
        with patch('nvoip.client.build_opener') as build_opener:
            with self.assertRaises(RuntimeError): NvoipClient().create_client_credentials_token()
            build_opener.assert_not_called()

    def test_redirect_keeps_authorization_within_origin(self):
        handler = _SameOriginRedirectHandler()
        request = Request('https://api.example.invalid/v3/balance', headers={'Authorization': 'Bearer dummy'})
        updated = handler.redirect_request(request, None, 302, '', {}, 'https://api.example.invalid:443/result')
        self.assertEqual(updated.get_header('Authorization'), 'Bearer dummy')

    def test_redirect_rejects_different_origins(self):
        handler = _SameOriginRedirectHandler()
        request = Request('https://api.example.invalid/v3/balance')
        for target in (
            'https://other.example.invalid/result',
            'https://api.example.invalid:444/result',
            'http://api.example.invalid/result',
            'ftp://api.example.invalid/result',
            'https://user@api.example.invalid/result',
        ):
            with self.subTest(target=target):
                self.assertIsNone(handler.redirect_request(request, None, 302, '', {}, target))

    def test_unfollowed_redirect_is_reported_as_an_error(self):
        with patch('nvoip.client.build_opener') as build_opener:
            build_opener.return_value.open.side_effect = HTTPError(
                'https://api.example.invalid', 302, 'redirect', {}, io.BytesIO(b'')
            )
            with self.assertRaises(NvoipError) as error:
                NvoipClient().get_balance('dummy')
        self.assertEqual(error.exception.status, 302)

if __name__ == '__main__': unittest.main()

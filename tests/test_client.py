import base64
import io
import json
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, quote_plus, urlparse
from unittest.mock import patch

from nvoip import NvoipClient
from nvoip.client import NvoipError

class ClientTests(unittest.TestCase):
    def record(self, action):
        with patch('nvoip.client.urlopen') as request:
            response = request.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b'{}'
            action()
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
        with patch('nvoip.client.urlopen', side_effect=HTTPError('https://example.invalid', 401, 'denied', {}, io.BytesIO(b'{"error":"denied"}'))):
            with self.assertRaises(NvoipError) as error: client.get_balance('dummy')
        self.assertEqual(error.exception.status, 401)

    def test_missing_client_credentials_fail_before_transport(self):
        with patch('nvoip.client.urlopen') as request:
            with self.assertRaises(RuntimeError): NvoipClient().create_client_credentials_token()
            request.assert_not_called()

if __name__ == '__main__': unittest.main()

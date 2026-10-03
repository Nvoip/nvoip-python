import unittest
from unittest.mock import patch

from nvoip import NvoipClient


class ClientTests(unittest.TestCase):
    def test_client_credentials_uses_auth_server_and_basic_auth(self):
        client = NvoipClient(oauth_client_id="client", oauth_client_secret="secret")
        with patch("nvoip.client.urlopen") as request:
            response = request.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b'{"access_token":"token"}'
            client.create_client_credentials_token()

        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, "https://api.nvoip.com.br/auth/oauth2/token")
        self.assertEqual(sent.get_header("Authorization"), "Basic Y2xpZW50OnNlY3JldA==")
        self.assertEqual(sent.data, b"grant_type=client_credentials")

    def test_v3_resource_uses_bearer_without_napikey(self):
        client = NvoipClient()
        with patch("nvoip.client.urlopen") as request:
            response = request.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b"{}"
            client.send_sms("11999999999", "template-approved", access_token="token")

        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, "https://api.nvoip.com.br/v3/sms")
        self.assertEqual(sent.get_header("Authorization"), "Bearer token")


if __name__ == "__main__":
    unittest.main()

from unittest.mock import (
    patch,
    Mock,
)

from django.test import SimpleTestCase

from app import secrets


MOCK_GCP_PROJECT = 'test-project'


@patch.dict(
    'os.environ', {
        'GOOGLE_CLOUD_PROJECT': MOCK_GCP_PROJECT,
        'GAE_APPLICATION': 'yes',
    }
)
@patch('app.secrets.SecretManagerServiceClient')
class SecretManagerTests(SimpleTestCase):
    def test_retrieve_secret(self, mock_sm):
        mock_client = Mock()
        mock_sm.return_value = mock_client
        mock_version_res = Mock()
        secret = 'samplesecret123'
        secret_bytes = bytes(secret, 'utf-8')
        mock_version_res.payload.data = secret_bytes
        mock_client.access_secret_version.return_value = mock_version_res

        name = 'SampleSecretName'
        ret = secrets.get(name)
        exp_path = (
            f'projects/{MOCK_GCP_PROJECT}/secrets/'
            f'{name}/versions/latest'
        )
        mock_client.access_secret_version.assert_called_once_with(
            request={'name': exp_path}
        )
        self.assertEqual(ret, secret)


class LocalDevModeTests(SimpleTestCase):

    @patch('app.secrets.SecretManagerServiceClient')
    def test_retrieve_from_env_var(self, mock_sm):
        secret = 'SampleSecret123'
        name = 'secretname'
        with patch.dict('os.environ', {name: secret}):
            val = secrets.get(name)

        self.assertEqual(val, secret)
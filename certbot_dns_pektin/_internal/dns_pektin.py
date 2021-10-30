"""DNS Authenticator for Pektin."""
import logging
import requests

from certbot import errors
from certbot.plugins import dns_common
from json import dumps as json_dumps

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Pektin
    This Authenticator uses the Pektin API to fulfill a dns-01 challenge.
    """

    description = ('Obtain certificates using a DNS TXT record.')
    ttl = 120

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super().add_parser_arguments(add)
        add('credentials', help='Pektin credentials INI file.')

    def more_info(self):  # pylint: disable=missing-function-docstring
        return 'This plugin configures a DNS TXT record to respond to a dns-01 challenge using ' + \
               'the Pektin API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'Pektin credentials INI file',
            {'username': 'The credentials file must contain a username.',
            'password': 'The credentials file must contain a password.',
            'vaultEndpoint': 'The credentials file must contain the vault endpoint.'},
            None
        )
        username = self.credentials.conf('username')
        password = self.credentials.conf('password')
        vaultEndpoint = self.credentials.conf('vaultEndpoint')
        self._pektin_client = _PektinClient(username, password, vaultEndpoint)

    def _perform(self, domain, validation_name, validation):
        self._pektin_client.add_txt_record(
            domain, validation_name, validation, self.ttl)

    def _cleanup(self, domain, validation_name, validation):
        self._pektin_client.del_txt_record(
            domain, validation_name, validation)


class _PektinClient:
    """
    Encapsulates all communication with the Pektin API.
    """

    def __init__(self, username, password, vault_endpoint):
        logger.debug('Obtaining token from vault...')
        vault_login_uri = f'{vault_endpoint}/v1/auth/userpass/login/{username}'
        r = requests.post(vault_login_uri, data={'password': password})
        if r.status_code != 200:
            raise errors.PluginError('Error obtaining token from vault.')
        json = r.json()
        if not 'auth' in json:
            raise errors.PluginError('JSON response from vault is invalid (no auth field).')
        elif not 'client_token' in json['auth']:
            raise errors.PluginError('JSON response from vault is invalid (no auth.client_token field).')
        self.vault_token = json['auth']['client_token']
        logger.debug('Successfully obtained token from vault.')

        logger.debug('Obtaining Pektin config from vault...')
        vault_config_uri = f'{vault_endpoint}/v1/pektin-kv/data/pektin-config'
        r = requests.get(vault_config_uri, headers={'X-Vault-Token': self.vault_token})
        if r.status_code != 200:
            raise errors.PluginError('Error obtaining Pektin config from vault.')
        json = r.json()
        if not 'data' in json:
            raise errors.PluginError('JSON response from vault is invalid (no data field).')
        elif not 'data' in json['data']:
            raise errors.PluginError('JSON response from vault is invalid (no data.data field).')
        pektin_config = json['data']['data']
        if not 'domain' in pektin_config:
            raise errors.PluginError('JSON response from vault is invalid (no data field).')
        elif not 'apiSubDomain' in pektin_config:
            raise errors.PluginError('JSON response from vault is invalid (no data.data field).')
        # TODO
        # self.pektin_api_uri = f'http://{pektin_config["apiSubDomain"]}.{pektin_config["domain"]}'
        self.pektin_api_uri = 'http://65.108.88.212:3001'
        logger.debug('Successfully obtained Pektin config from vault.')

        logger.debug('Obtaining Pektin API token from vault...')
        vault_token_uri = f'{vault_endpoint}/v1/pektin-kv/data/gss_token'
        r = requests.get(vault_token_uri, headers={'X-Vault-Token': self.vault_token})
        if r.status_code != 200:
            raise errors.PluginError('Error obtaining Pektin API token from vault.')
        json = r.json()
        if not 'data' in json:
            raise errors.PluginError('JSON response from vault is invalid (no data field).')
        elif not 'data' in json['data']:
            raise errors.PluginError('JSON response from vault is invalid (no data.data field).')
        self.pektin_api_token = json['data']['data']['token']
        logger.debug('Successfully obtained Pektin API token from vault.')

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.
        :param str domain: The domain to use to look up the Pektin zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs communicating with the Pektin API
        """

        logger.debug(f'Attempting to add record to domain {domain}: {record_name}')
        uri = f'{self.pektin_api_uri}/set'
        logger.debug(record_content)
        txt = {'txt_data': [[b for b in record_content.encode("utf-8")]]}
        rr_set = [{'ttl': record_ttl, 'value': {'TXT': txt}}]
        redis_entries = [{'name': f'{record_name}.:TXT', 'rr_set': rr_set}]
        data = json_dumps({'token': self.pektin_api_token, 'records': redis_entries})
        logger.debug(data)
        headers = {'content-type': 'application/json'}
        r = requests.post(uri, data=data, headers=headers)

        if r.status_code != 200:
            raise errors.PluginError(f'Error setting record: {r.status_code} {r.text}')
        json = r.json()
        if not 'error' in json:
            raise errors.PluginError('JSON response from Pektin API is invalid (no error field).')
        if json['error']:
            raise errors.PluginError(f'Pektin API response indicates an error: {json.get("message")}')
        logger.debug('Successfully added record.')

    def del_txt_record(self, domain, record_name, record_content):
        """
        Delete a TXT record using the supplied information.
        Note that both the record's name and content are used to ensure that similar records
        created concurrently (e.g., due to concurrent invocations of this plugin) are not deleted.
        Failures are logged, but not raised.
        :param str domain: The domain to use to look up the Pektin zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        """

        logger.debug(f'Deleting record from domain {domain}.')
        uri = f'{self.pektin_api_uri}/delete'
        key = f'{record_name}.:TXT'
        data = json_dumps({'token': self.pektin_api_token, 'keys': [key]})
        headers = {'content-type': 'application/json'}
        r = requests.post(uri, data=data, headers=headers)
        if r.status_code != 200:
            logger.warning(f'Could not delete record: {r.status_code} {r.text}')
        else:
          logger.debug('Successfully deleted record.')

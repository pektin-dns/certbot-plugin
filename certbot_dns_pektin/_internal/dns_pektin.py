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
            {
                'username': 'The credentials file must contain a username.',
                'confidant_password': 'The credentials file must contain a confidantPassword.',
                'api_endpoint':'The credentials file must contain the vault endpoint.'
            },
            None
        )
        username = self.credentials.conf('username')
        confidantPassword = self.credentials.conf('confidant_password')
        pektinApiEndpoint = self.credentials.conf('api_endpoint')
        self._pektin_client = _PektinClient(username, confidantPassword, pektinApiEndpoint)

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

    def __init__(self, username, confidantPassword, pektinApiEndpoint):
        self.username=username
        self.confidantPassword=confidantPassword
        self.pektinApiEndpoint=pektinApiEndpoint
        self.domain_rr_sets = {}
        

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
        uri = f'{self.pektinApiEndpoint}/set'
        logger.debug(record_content)

        if not domain in self.domain_rr_sets:
            self.domain_rr_sets[domain] = []
        self.domain_rr_sets[domain] += [{ 'value': record_content}]

        record_name = record_name if record_name.endswith('.') else f'{record_name}.'
        records = [{'name': record_name, 'ttl': record_ttl, 'rr_set': self.domain_rr_sets[domain], 'rr_type': 'TXT'}]
        data = json_dumps({'client_username': self.username, 'confidant_password': self.confidantPassword, 'records': records})
        logger.debug(data)
        headers = {'content-type': 'application/json'}
        r = requests.post(uri, data=data, headers=headers)

        if r.status_code != 200:
            raise errors.PluginError(f'Error setting record: {r.status_code} {r.text}')
        json = r.json()
        if not 'type' in json:
            raise errors.PluginError('JSON response from Pektin API is invalid (no type field).')
        if json['type'] != 'success':
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
        uri = f'{self.pektinApiEndpoint}/delete'
        record_name = record_name if record_name.endswith('.') else f'{record_name}.'
        key = {'name': record_name, 'rr_type': 'TXT'}
        data = json_dumps({'client_username': self.username, 'confidant_password': self.confidantPassword, 'records': [key]})
        headers = {'content-type': 'application/json'}
        r = requests.post(uri, data=data, headers=headers)
        if r.status_code != 200:
            logger.warning(f'Could not delete record: {r.status_code} {r.text}')
        else:
          logger.debug('Successfully deleted record.')

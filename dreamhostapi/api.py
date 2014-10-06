import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import uuid

from dreamhostapi.module import Module


class SSL3HTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_SSLv3
        )


class DreamHostAPI(object):
    API_URL = 'https://api.dreamhost.com'

    def __init__(self, key):
        self.key = key
        self.session = requests.Session()
        self.session.mount(self.API_URL, SSL3HTTPAdapter())

    def __getattr__(self, module_name):
        if module_name.startswith('__'):
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, module_name))

        module = Module(module_name, self._call)

        setattr(self, module_name, module)

        return module

    def _call(self, command, params=None):
        if params is None:
            params = {}

        params.update({
            'key': self.key,
            'cmd': command,
            'unique_id': str(uuid.uuid1()),
            'format': 'json',
        })

        http_response = self.session.get(self.API_URL, params=params)

        # Something's very wrong if we don't get a 200 OK
        if http_response.status_code != requests.codes.ok:
            http_response.raise_for_status()

        return http_response.json()

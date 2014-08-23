import requests
import os.path
import getpass
from seplis.utils import json_dumps
from urllib.parse import urljoin
from seplis.indexer.show.tvrage import Tvrage
from seplis.indexer.show.thetvdb import Thetvdb
from seplis.config import config
from seplis import Client

class Show_indexer(object):

    token = None

    def get_indexer(self, external_name):
        obj = getattr(self, 'external_{}'.format(external_name))
        if not obj:
            raise Exception('No indexer found for external name: {}'.format(external_name))
        return obj

    @property
    def external_tvrage(self):
        return Tvrage

    @property
    def external_thetvdb(self):
        return Thetvdb(config['client']['thetvdb'])

    def base_api_url(self, req):
        return urljoin(config['api']['url'], '/1/{}'.format(req))

    def login(self):
        try:
           with open('filename'):
               pass
        except IOError:
            print('No valid token was found.')

    def new(self, external_name, external_id):
        '''
        Creates a show.
        '''
        indexer = self.get_indexer(external_name)
        show_data = indexer.get_show(external_id)
        if not show_data:
            return None
        show_data['index'] = {}
        show_data['index']['info'] = external_name
        show_data['index']['episodes'] = external_name
        response = requests.get(
            '{base}/externals/{external_name}/{id}'.format(
                base=self.base_api_url('shows'), 
                external_name=external_name,
                id=external_id,
            ),
        )
        if response.status_code == 404:
            response = requests.post(self.base_api_url('shows'),
                data=json_dumps(show_data),
                headers={
                    'Authorization': 'Bearer {}'.format(self.token),
                },
            )
            return response.json()
        elif response.status_code == 200:
            response = requests.put(
                '{}/{}'.format(self.base_api_url('shows'), response.json()['id']),
                data=json_dumps(show_data),
                headers={
                    'Authorization': 'Bearer {}'.format(self.token),
                },
            )
            return response.json()
        return None
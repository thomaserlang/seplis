import os.path
import getpass
from seplis.utils import json_dumps
from urllib.parse import urljoin
from seplis.indexer.show.tvrage import Tvrage
from seplis.indexer.show.thetvdb import Thetvdb
from seplis.config import config
from seplis import Client

class Show_indexer(Client):

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

    def login(self):
        try:
           with open('filename'):
               pass
        except IOError:
            print('No valid token was found.')

    def new(self, external_name, external_id, get_episodes=True):
        '''
        Creates a show.
        '''
        indexer = self.get_indexer(external_name)
        show_data = indexer.get_show(external_id)
        print(show_data)
        if not get_episodes:
            show_data.pop('episodes')
        if not show_data:
            raise Exception('the external show was not found')
        show_data['indices'] = {}
        show_data['indices']['info'] = external_name
        if get_episodes:
            show_data['indices']['episodes'] = external_name
        show = self.get(
            '/shows/externals/{external_name}/{id}'.format(
                external_name=external_name,
                id=external_id,
            ),
        )
        if not show:
            show = self.post('/shows',
                body=show_data,
            )
            return show
        show = self.put('/shows/{}'.format(show['id']),
            body=show_data,
        )
        return show
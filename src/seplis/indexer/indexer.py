import os.path
import getpass
import logging
from seplis.utils import json_dumps
from urllib.parse import urljoin
from seplis.indexer.show.tvrage import Tvrage
from seplis.indexer.show.thetvdb import Thetvdb
from seplis.config import config
from seplis import Client, schemas

class Show_indexer(Client):

    def get_indexer(self, external_name):
        obj = getattr(self, 'external_{}'.format(external_name))
        if not obj:
            raise Exception('No indexer found for external name: {}'.format(external_name))
        return obj

    @property
    def external_tvrage(self):
        return Tvrage()

    @property
    def external_thetvdb(self):
        return Thetvdb(config['client']['thetvdb'])

    def update(self):
        external_names = [
            'tvrage', 
            'thetvdb',
        ]
        logging.info('Checking for updates from external sources...')
        updated_shows = {}
        for name in external_names:
            logging.info('Checking external source: {}'.format(name))
            indexer = self.get_indexer(name)
            ids = indexer.get_updates()
            if not ids: 
                continue
            for id_ in ids:
                logging.info('Looking for a external show: {} with id: {}'.format(
                    name,
                    id_
                ))
                show = self.get('/shows/externals/{name}/{id}'.format( 
                    name=name,
                    id=id_,
                ))
                if not show:
                    logging.info('Nothing found for external show: {} with id: {}'.format(
                        name,
                        id_
                    ))
                    continue
                logging.info('External source: {} with id: {} has a relation to show id: {}'.format(
                    name,
                    id_,
                    show['id'],
                ))
                show_data = {}
                if 'indices' in show:
                    if show['indices']['info'] == name:
                        show_data = indexer.get_show(id_)
                        if show_data:
                            show_data = show_info_changes(show, show_data)
                    if show['indices']['episodes'] == name:
                        episodes = indexer.get_episodes(id_)
                        if episodes: 
                            current_episodes = self.get(
                                'shows/{}/episodes?per_page=100'.format(show['id'])
                            ).all()
                            show_data['episodes'] = show_episode_changes(
                                current_episodes,
                                episodes,
                            )
                    self.patch('shows/{}'.format(show['id']), show_data)
                    updated_shows[show['id']] = show_data
        return updated_shows

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

def show_info_changes(show, show_new):
    changes = {}
    for s in schemas.Show_schema:
        if not isinstance(s, str) or \
            s == 'externals' or \
            s == 'indices':
            continue
        if s in show and s in show_new:
            if show[s] != show_new[s]:
                changes[s] = show_new[s]
        elif s not in show and s in show_new:
            changes[s] = show_new[s]
    return changes

def show_episode_changes(episodes, episodes_new):
    changes = []
    prev = {episode['number']: episode for episode in episodes}
    for episode in episodes_new:
        data = {}
        prev_episode = prev[episode['number']] if episode['number'] in prev else episode 
        if episode['number'] not in prev:
            changes.append(episode)
            continue
        for s in schemas.Episode_schema:
            s = str(s)
            if s == 'number':
                data[s] = episode[s]
                continue
            if s in episode and s in prev_episode:
                if episode[s] != prev_episode[s]:
                    data[s] = episode[s]
            elif s not in prev_episode and s in episode:
                data[s] = episode[s]
        if data != {} and len(data) > 1:
            changes.append(data)
    return changes
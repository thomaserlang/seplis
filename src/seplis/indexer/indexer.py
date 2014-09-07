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
        obj = getattr(self, 'external_{}'.format(external_name), None)
        if not obj:
            return None
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
            if not indexer:
                continue
            ids = indexer.get_updates()
            if not ids: 
                logging.info('No updates from external source: {}'.format(name))
                continue

            logging.info('Found {} updates from external source: {}'.format(len(ids), name))
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
                show_data = self._update_show(
                    show,
                    update_episodes=True,
                )
                updated_shows[str(id_)] = show_data
            indexer.set_latest_update_timestamp()
        return updated_shows

    def login(self):
        try:
           with open('filename'):
               pass
        except IOError:
            print('No valid token was found.')

    def update_show(self, show_id):
        show = self.get('/shows/{}'.format(show_id))
        if not show:
            raise Exception('Show not found')
        show_data = self._update_show(
            show,
            update_episodes=True,
        )
        return show_data

    def _update_show(self, show, update_episodes=True):
        '''

        :param show: dict
        :param update_episodes: bool
        '''
        if 'indices' not in show:
            return None
        show_data = {}
        show_indexer = self.get_indexer(show['indices'].get('info', ''))
        if show_indexer:               
            external_show = show_indexer.get_show(
                show['externals'][show['indices']['info']]
            )
            if external_show:
                show_data = show_info_changes(
                    show, 
                    external_show,
                )
        episode_indexer = self.get_indexer(show['indices'].get('episodes'))
        if episode_indexer and update_episodes:
            external_episodes = show_indexer.get_episodes(
                show['externals'][show['indices']['episodes']]
            )
            if external_episodes:
                episodes = self.get(
                    '/shows/{}/episodes?per_page=500'.format(show['id'])
                ).all()
                if not episodes:
                    episodes = []
                show_data['episodes'] = show_episode_changes(
                    episodes,
                    external_episodes,
                )
        if show_data == {'episodes': []}:
            show_data = {}
        if show_data:
            show = self.patch(
                'shows/{}'.format(show['id']), 
                show_data,
                timeout=120
            )
        return show_data

    def new(self, external_name, external_id, get_episodes=True):
        '''
        Creates a show.
        '''
        indexer = self.get_indexer(external_name)
        show_data = indexer.get_show(external_id)
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
            if show[s] == None and isinstance(show_new[s], dict):
                continue
            if show[s] != show_new[s]:
                changes[s] = show_new[s]
        elif s not in show and s in show_new:
            changes[s] = show_new[s]
    return changes

def show_episode_changes(episodes, episodes_new):
    changes = []
    current = {episode['number']: episode for episode in episodes}
    for episode in episodes_new:
        data = {}
        current_episode = current[episode['number']] if episode['number'] in current else episode 
        if episode['number'] not in current:
            changes.append(episode)
            continue
        for s in schemas.Episode_schema:
            s = str(s)
            if s == 'number':
                data[s] = episode[s]
                continue
            if s in episode and s in current_episode:
                if episode[s] == None and isinstance(current_episode[s], dict):
                    continue
                if episode[s] != current_episode[s]:
                    data[s] = episode[s]
            elif s not in current_episode and s in episode:
                data[s] = episode[s]
        if data != {} and len(data) > 1:
            changes.append(data)
    return changes
import os.path
import getpass
import logging
import time
import io
import requests
from seplis.utils import json_dumps
from urllib.parse import urljoin
from seplis.indexer.show.tvrage import Tvrage
from seplis.indexer.show.thetvdb import Thetvdb
from seplis.api import constants
from seplis.config import config
from seplis import Client, schemas, API_error
from retrying import retry

def _can_retry_update_show(exception):
    if isinstance(exception, KeyboardInterrupt):
        return False    
    if isinstance(exception, API_error):
        if exception.code == 1009:
            # not authenticated, let's get out of here.
            return False
    return True

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
        external_names = (
            'tvrage',
            'thetvdb',
        )
        logging.info('Checking for updates from external sources...')
        updated_shows = {}
        for name in external_names:
            logging.info('Checking external source: {}'.format(name))
            indexer = self.get_indexer(name)
            if not indexer:
                continue
            start_time = time.time()
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
                try:
                    show_data = self._update_show(
                        show,
                        update_episodes=True,
                    )
                    updated_shows[str(id_)] = show_data
                except:
                    logging.exception('update')
            indexer.set_latest_update_timestamp(start_time)
        logging.info('Done updating.')
        return updated_shows

    def login(self):
        try:
           with open('filename'):
               pass
        except IOError:
            print('No valid token was found.')

    def update_show(self, show_id):
        try:
            logging.info('Updating show: {}'.format(show_id))
            show = self.get('/shows/{}'.format(show_id))
            if not show:
                raise Exception('Show not found')
            show_data = self._update_show(
                show,
                update_episodes=True,
            )
            return show_data
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            logging.exception('update_show')

    @retry(
        stop_max_attempt_number=5,
        retry_on_exception=_can_retry_update_show,
        wrap_exception=True
    )
    def _update_show(self, show, update_episodes=True, 
        update_images=True):
        '''

        :param show: dict
        :param update_episodes: bool
        '''
        if 'indices' not in show:
            return None
        show_data = {}
        
        # show info
        show_updates = self._get_show_updates(show)
        if show_updates:
            show_data = show_updates

        # show episodes
        if update_episodes:
            episodes = self._get_episode_updates(show)
            if episodes:
                show_data['episodes'] = episodes

        if show_data:
            self.patch(
                'shows/{}'.format(show['id']), 
                show_data,
                timeout=120
            )
        # show images
        if update_images and not config['api']['storitch']:
            logging.warning('Missing url for storitch in the config')
        if update_images and config['api']['storitch']:
            images = self._update_images(show)
            show_data['images'] = images
        return show_data

    def _get_show_updates(self, show):
        show_indexer = self.get_indexer(show['indices'].get('info', ''))
        if not show_indexer: 
            return              
        external_show = show_indexer.get_show(
            show['externals'][show['indices']['info']]
        )
        if external_show:
            return show_info_changes(
                show, 
                external_show,
            )

    def _get_episode_updates(self, show):
        episode_indexer = self.get_indexer(show['indices'].get('episodes', ''))
        if not episode_indexer:
            return
        external_episodes = episode_indexer.get_episodes(
            show['externals'][show['indices']['episodes']]
        )
        if not external_episodes:
            return
        episodes = self.get(
            '/shows/{}/episodes?per_page=500'.format(show['id'])
        ).all()
        if not episodes:
            episodes = []
        return show_episode_changes(
            episodes,
            external_episodes,
        )

    def _update_images(self, show):
        '''
        Retrives images from the external source.
        If an image with the external name and id does not exist 
        the image will be uploaded.
        '''
        image_indexer = self.get_indexer(show['indices'].get('images', ''))
        if not image_indexer:
            return
        external_name = show['indices']['images']
        external_images = image_indexer.get_images(
            show['externals'][external_name]
        )
        logging.info('_update_images:{}:{}: Found: {} external images'.format(
            show['id'], 
            external_name, 
            len(external_images)
        ))
        images = self.get(
            '/shows/{}/images?q=external_name:{}&per_page=500'.format(
                show['id'],
                show['indices']['images'],
            ),
        ).all()
        images_lookup = {image['external_id']: image for image in images}
        new_images = []
        updated_images = []
        for ex_image in external_images:
            # check if the image already exists on the server
            if ex_image['external_id'] in images_lookup:
                image = images_lookup[ex_image['external_id']]
                # if it exists check that an image has been assigned
                if not image['hash']:            
                    logging.info('_update_images:{}:{}: Found image without an image assigned: {}'.format(
                        show['id'], 
                        external_name,
                        image['id'],
                    ))
                    # if not upload the image and continue
                    updated_image = self._upload_show_image(
                        show,
                        image,
                    )
                    if updated_image:
                        updated_images.append(image)
                continue
            logging.info('_update_images:{}:{}: New image'.format(
                show['id'], 
                external_name,
            ))
            image = self.post('/shows/{}/images'.format(show['id']),
                ex_image,
            )
            updated_image = self._upload_show_image(
                show,
                image,
            ) 
            if updated_image:
                logging.info('_update_images:{}:{}: Image created and uploaded: {}'.format(
                    show['id'], 
                    external_name,
                    image['id']
                ))
                updated_images.append(image)
            else:
                logging.info('_update_images:{}:{}: The image could not be created or uploaded'.format(
                    show['id'], 
                    external_name,
                ))
        # If the show has no image set, then we will set one
        if updated_images and ('poster_image' in show) and not show['poster_image']:
            for img in updated_images:
                if img['type'] == constants.IMAGE_TYPE_POSTER:
                    self.patch('shows/{}'.format(show['id']), {
                        'poster_image_id': img['id'],
                    })
                    break
        return updated_images

    def _upload_show_image(self, show, image):
        return self._upload_image(
            '/shows/{}/images/{}/data'.format(
                show['id'], 
                image['id']
            ),
            image['source_url'],
        )

    def _upload_image(self, uri, image_url):
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r = requests.put(self.url+uri,
                files={
                    'image': r.raw,
                },
                headers={
                    'Authorization': 'Bearer {}'.format(self.access_token)
                }
            )
            return r.status_code == 200

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
            s == 'indices' or \
            s == 'episodes':
            continue
        if s in show and s in show_new:
            if show[s] == None and isinstance(show_new[s], dict):
                continue
            if show[s] != show_new[s]:
                if isinstance(show[s], list):
                    changes[s] = list(set(show_new[s]) - set(show[s]))
                    if not changes[s]:
                        changes.pop(s)
                else:
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
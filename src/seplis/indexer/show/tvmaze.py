import requests
import logging
import re
from seplis.api import constants
from dateutil import parser
from seplis.indexer.show.base import Show_indexer_base

class Tvmaze(Show_indexer_base):
    _url = 'http://api.tvmaze.com/shows/{show_id}'
    _url_episodes = 'http://api.tvmaze.com/shows/{show_id}/episodes'
    _url_update = 'http://api.tvmaze.com/updates/shows'

    def __init__(self, apikey=None):
        super().__init__('tvmaze', apikey=apikey)

    def get_show(self, show_id):
        r = requests.get(self._url.format(show_id=show_id))
        if r.status_code != 200:
            return
        show = r.json()
        description = None
        if show['summary']:
            description = {
                'text': re.sub('<[^>]*>', '', show['summary']),
                'title': 'TVmaze',
                'url': show['url'],
            }
        externals = {key: str(show['externals'][key]) for key in show['externals']}
        externals['tvmaze'] = str(show['id'])
        return {
            'title': show['name'],
            'description': description,
            'ended': None,
            'externals': externals,
            'status': self.parse_status(show['status']),
            'runtime': show['runtime'],
            'genres': show['genres'],
        }

    def parse_status(self, status_str):
        if status_str.lower() == 'ended':
            return 2
        return 1

    def get_images(self, show_id):
        r = requests.get(self._url.format(show_id=show_id))
        if r.status_code != 200:
            return
        data = r.json()
        if not data['image']:
            return
        if 'original' not in data['image']:
            return
        if not data['image']['original']:
            return
        return [{
            'external_name': 'tvmaze',
            'external_id': str(data['id']),
            'source_url': data['image']['original'],
            'source_title': 'TVmaze',
            'type': constants.IMAGE_TYPE_POSTER,
        }]

    def get_episodes(self, show_id):
        r = requests.get(self._url_episodes.format(show_id=show_id))
        if r.status_code != 200:
            return
        data = r.json()
        episodes = []
        for i, episode in enumerate(data):
            episodes.append({
                'number': i,
                'title': episode['name'],
                'season': episode['season'],
                'episode': episode['number'],
                'air_date': episode['airdate'] if episode['airdate'] else None,
                'description': None if not episode['summary'] else {
                    'text': re.sub('<[^>]*>', '', episode['summary']),
                    'title': 'TVmaze',
                    'url': episode['url'],
                },
            })
        return episodes

    def get_updates(self):
        timestamp = self.get_latest_update_timestamp()
        r = requests.get(self._url_update)
        if r.status_code != 200:
            return
        shows = r.json()
        ids = []
        for key in shows:
            if shows[key] < timestamp:
                continue
            ids.append(key)
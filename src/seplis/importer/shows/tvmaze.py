import requests
import logging
import re
import time, aniso8601
from dateutil import tz
from seplis.api import constants
from dateutil import parser
from .base import Show_importer_base, register_importer

class Tvmaze(Show_importer_base):
    display_name = 'TVmaze'
    external_name = 'tvmaze'
    supported = (
        'info',
        'episodes',
        'images',
    )
    
    _url = 'http://api.tvmaze.com/shows/{show_id}'
    _url_episodes = 'http://api.tvmaze.com/shows/{show_id}/episodes'
    _url_update = 'http://api.tvmaze.com/updates/shows'

    def info(self, show_id):
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
        externals = {key: str(show['externals'][key]) for key in show['externals'] if show['externals'][key]}
        externals[self.external_name] = str(show['id'])
        return {
            'title': show['name'],
            'description': description,
            'ended': None,
            'externals': externals,
            'status': self.parse_status(show['status']),
            'runtime': show['runtime'],
            'genres': show['genres'],
            'premiered': show['premiered'],
            'language': show['language'],
        }

    @staticmethod
    def parse_status(status_str):
        if status_str.lower() == 'ended':
            return 2
        return 1

    def images(self, show_id):
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

    def episodes(self, show_id):
        r = requests.get(self._url_episodes.format(show_id=show_id))
        if r.status_code != 200:
            return
        data = r.json()
        episodes = []
        i = 0
        for episode in data:
            if episode['season'] == 0:
                continue
            if episode['number'] == 0:
                continue
            i += 1
            if episode['airstamp']:
                episode['airstamp'] = aniso8601.parse_datetime(episode['airstamp'])
                if episode['airstamp'].tzinfo:
                    episode['airstamp'] = episode['airstamp'].astimezone(tz.tzutc())
            episodes.append({
                'number': i,
                'title': episode['name'],
                'season': episode['season'],
                'episode': episode['number'],
                'air_date': episode['airstamp'].date().isoformat() if episode['airstamp'] else None,
                'air_time': episode['airstamp'].time().isoformat() if episode['airstamp'] else None,
                'description': None if not episode['summary'] else {
                    'text': re.sub('<[^>]*>', '', episode['summary']),
                    'title': 'TVmaze',
                    'url': episode['url'],
                },
            })
        return episodes

    def incremental_updates(self):
        last_timestamp = self.last_update_timestamp()
        r = requests.get(self._url_update)
        if r.status_code != 200:
            return []
        current_timestamp = time.time()
        shows = r.json()
        ids = []
        for key in shows:
            if shows[key] < last_timestamp:
                continue
            ids.append(key)
        return ids

register_importer(Tvmaze())
import requests, json
import logging
from dateutil import parser
from seplis.api import constants
from seplis import config
from .base import Show_importer_base, register_importer

class Thetvdb(Show_importer_base):
    display_name = 'TheTVDB'
    external_name = 'thetvdb'
    supported = (
        'info',
        'episodes',
        'images',
    )
    _url = 'https://api.thetvdb.com'

    def __init__(self, apikey=None):
        super().__init__()
        self.apikey = apikey
        if not apikey:
            self.apikey = config['client']['thetvdb']

    def login_headers(self):
        headers = {
            'Accept-Language': 'en',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        r = requests.post(self._url+'/login', data=json.dumps({'apikey': self.apikey}), headers=headers)
        if r.status_code == 401:
            raise Exception(r.content)
        if r.status_code == 200:
            headers['Authorization'] = 'Bearer {}'.format(r.json()['token'])
            return headers
        raise Exception('Unknown status code from thetvdb: {} {}'.format(r.status_code, r.content))

    def info(self, show_id):
        r = requests.get(
            self._url+'/series/{}'.format(show_id),
            headers=self.login_headers(),
        )
        if r.status_code == 200:
            data = r.json()['data']
            description = None
            if data['overview']:
                description = {
                    'text': data['overview'],
                    'title': 'TheTVDB',
                    'url': 'http://thetvdb.com/?tab=series&id={}'.format(show_id), 
                }
            externals = {
                'thetvdb': str(show_id),
            }
            if data['imdbId']:
                externals['imdb'] = data['imdbId']

            return {
                'title': data['seriesName'],
                'description': description,
                'premiered': self.parse_date(data['firstAired']),
                'ended': None,
                'externals': externals,
                'status': self.parse_status(data['status']),
                'runtime': int(data['runtime']) if data['runtime'] else None,
                'genres': data['genre'],
            }

    def episodes(self, show_id):
        headers = self.login_headers()
        episodes = []
        data = {'links': { 'next': 1 } }
        while data['links']['next']:
            r = requests.get(
                self._url+'/series/{}/episodes?page={}'.format(show_id, data['links']['next']),
                headers=headers,
            )
            if r.status_code == 200:
                data = r.json()
                if data['data']:
                    episodes.extend(
                        self.parse_episodes(data['data'])
                    )
            else:
                break
        episodes = sorted(episodes, key=lambda k: (k['season'], k['episode']))
        for i, e in enumerate(episodes):
            e['number'] = i + 1
        return episodes if episodes else None

    def images(self, show_id):        
        r = requests.get(
            self._url+'/series/{}/images/query'.format(show_id),
            params={
                'keyType': 'poster',
                'resolution': '680x1000',
            },
            headers=self.login_headers(),
        )
        images = []
        if r.status_code == 200:
            data = r.json()['data']
            if not data:
                return images
            for image in sorted(data, reverse=True, key=lambda img: float(img['ratingsInfo']['average'])):
                images.append({
                    'external_name': 'thetvdb',
                    'external_id': str(image['id']),
                    'source_url': 'http://thetvdb.com/banners/{}'.format(image['fileName']),
                    'source_title': 'TheTVDB',
                    'type': constants.IMAGE_TYPE_POSTER,
                })
        return images

    def incremental_updates(self):
        timestamp = self.last_update_timestamp()
        r = requests.get(
            self._url+'/updated/query',
            params={'fromTime': timestamp},
            headers=self.login_headers(),
        )
        if r.status_code != 200:
            return
        data = r.json()['data']
        if not data:
            return
        return [str(s['id']) for s in data]

    def parse_status(self, status_str):
        if status_str == 'Ended':
            return 2
        elif status_str == 'Continuing':
            return 1
        return 1

    def parse_episodes(self, episodes):
        _episodes = []
        for episode in episodes:
            try:
                if episode['airedSeason'] == 0:
                    continue
                if episode['airedEpisodeNumber'] == 0:
                    continue
                _episodes.append(self.parse_episode(episode))
            except ValueError as e:
                logging.exception('Parsing episode "{}" faild with error: {}'.format(date))
        return _episodes

    def parse_episode(self, episode):
        description = None
        if episode['overview']:
            description = {
                'text': episode['overview'],
                'title': 'TheTVDB',
                'url': 'http://thetvdb.com',
            }
        d = self.parse_date(episode['firstAired']) if episode['firstAired'] else None
        return {
            'title': episode['episodeName'],
            'description': description,
            'number': episode['absoluteNumber'],
            'season': episode['airedSeason'],
            'episode': episode['airedEpisodeNumber'],
            'air_date': d,
            'air_datetime': f'{d}T00:00:00Z' if d else None,
        }

    def parse_date(self, date):
        if not date:
            return None
        if date == '0000-00-00':
            return None
        try:
            return parser.parse(date).date().isoformat()
        except ValueError as e:
            logging.exception('Parsing date "{}"'.format(date))
        return None
        
register_importer(Thetvdb())
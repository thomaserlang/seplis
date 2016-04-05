import requests
import xmltodict
import logging
from dateutil import parser
from seplis.api import constants
from seplis import config
from .base import Show_importer_base, register_importer

class Thetvdb(Show_importer_base):
    name = 'TheTVDB'
    id = 'thetvdb'
    supported = (
        'info',
        'episodes',
        'images',
    )

    _url = 'http://thetvdb.com/api/{apikey}/series/{id}/{type}'
    _source_url = 'http://thetvdb.com/?tab=series&id={id}'
    _url_updates = 'http://thetvdb.com/api/Updates.php?type=all&time={}'
    _url_episode = 'http://thetvdb.com/api/{apikey}/episodes/{id}/en.xml'

    def __init__(self, apikey=None):
        super().__init__()
        self.apikey = apikey
        if not apikey:
            self.apikey = config['client']['thetvdb']

    def info(self, show_id):
        r = requests.get(
            self._url.format(
                apikey=self.apikey,
                id=show_id,
                type='en.xml',
            )
        )
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            if not data['Data']:
                return
            if isinstance(data['Data']['Series'], list):
                data['Data']['Series'] = data['Data']['Series'][0]
            description = None
            if 'Overview' in data['Data']['Series'] and data['Data']['Series']['Overview']:
                description = {
                    'text': data['Data']['Series']['Overview'],
                    'title': 'TheTVDB',
                    'url': self._source_url.format(id=show_id), 
                }
            externals = {
                'thetvdb': str(show_id),
            }
            if 'IMDB_ID' in data['Data']['Series'] and data['Data']['Series']['IMDB_ID']:
                externals['imdb'] = data['Data']['Series']['IMDB_ID']

            return {
                'title': data['Data']['Series']['SeriesName'],
                'description': description,
                'premiered': self.parse_date(data['Data']['Series']['FirstAired']),
                'ended': None,               
                'externals': externals,
                'status': self.parse_status(data['Data']['Series']['Status']),
                'runtime': int(data['Data']['Series']['Runtime']) if data['Data']['Series']['Runtime'] else None,
                'genres': self.parse_genres(data['Data']['Series']['Genre']),
            }

    def episodes(self, show_id):
        r = requests.get(
            self._url.format(
                apikey=self.apikey,
                id=show_id,
                type='all/en.xml',
            )
        )
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            episodes = []
            if 'Episode' in data['Data']:
                episodes = self.parse_episodes(data['Data']['Episode'])
            return episodes

    def images(self, show_id):        
        r = requests.get(
            self._url.format(
                apikey=self.apikey,
                id=show_id,
                type='banners.xml',
            )
        )
        images = []
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            if not data or not ('Banners' in data) or not data['Banners']:
                return images
            if not isinstance(data['Banners']['Banner'], list):
                data['Banners']['Banner'] = [data['Banners']['Banner']]
            banners = [banner for banner in data['Banners']['Banner'] \
                if 'Rating' in banner]
            for banner in sorted(banners, reverse=True, key=lambda banner: float(banner['Rating']) \
                    if banner['Rating'] else float(0)):
                if banner['BannerType'] != 'poster':
                    continue
                images.append({
                    'external_name': 'thetvdb',
                    'external_id': str(banner['id']),
                    'source_url': 'http://thetvdb.com/banners/{}'.format(banner['BannerPath']),
                    'source_title': 'TheTVDB',
                    'type': constants.IMAGE_TYPE_POSTER,
                })
        return images

    def incremental_updates(self):
        data = self.get_update_data()
        if not data:
            return
        ids = []
        for id_ in data['Series']:
            ids.append(id_)
        for id_ in data['Episode']:
            try:
                logging.info('tvrage show id from episode id lookup: {}'.format(id_))
                show_id = self.episode_id_to_show_id(
                    id_,
                )
                if not show_id:
                    continue
                ids.append(show_id)
            except:
                logging.exception('tvrage get_updates')
        return ids

    def get_update_data(self):
        timestamp = self.last_update_timestamp()
        r = requests.get(
            self._url_updates.format(
                timestamp,
            )
        )
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            result = {
                'Series': [],
                'Episode': [],
            }
            for t in ['Series', 'Episode']:
                if t not in data['Items']:
                    continue
                if not isinstance(data['Items'][t], list):
                    data['Items'][t] = [int(data['Items'][t])]
                for id_ in data['Items'][t]:
                    result[t].append(int(id_))
            return result

    def episode_id_to_show_id(self, episode_id):
        r = requests.get(
            self._url_episode.format(
                apikey=self.apikey,
                id=episode_id,
            )
        )
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            return int(data['Data']['Episode']['seriesid'])

    def parse_status(self, status_str):
        if status_str == 'Ended':
            return 2
        elif status_str == 'Continuing':
            return 1
        return 1

    def parse_episodes(self, episodes):
        _episodes = []
        if not isinstance(episodes, list):
            episodes = [episodes]
        logging.debug('Multiple episodes')
        number = 0
        for episode in episodes:
            try:
                if (int(episode['SeasonNumber']) == 0):
                    continue
                number += 1
                _episodes.append(self.parse_episode(episode, number))
            except ValueError as e:
                logging.exception('Parsing episode "{}" faild with error: {}'.format(date))
        return _episodes

    def parse_episode(self, episode, number):
        description = None
        if 'Overview' in episode and episode['Overview']:
            description = {
                'text': episode['Overview'],
                'title': 'TheTVDB',
                'url': self._source_url.format(id=episode['seriesid']),
            }
        return {
            'title': episode['EpisodeName'],
            'description': description,
            'number': number,
            'season': int(episode['SeasonNumber']),
            'episode': int(episode['EpisodeNumber']),
            'air_date': self.parse_date(episode['FirstAired']) if episode['FirstAired'] else None,
        }

    def parse_genres(self, genres):
        if genres:
            return [genre for genre in genres.split('|') if genre]
        return []

    def parse_date(self, date):
        if not date:
            return None
        if date == '0000-00-00':
            return None
        try:
            return parser.parse(date).strftime('%Y-%m-%d')
        except ValueError as e:
            logging.exception('Parsing date "{}"'.format(date))
        return None

    def get_show_description(self, show_id):
        '''
        Returns the shows description in the format:
            {
                text: 'Some text',
                title: 'TheTVDB',
                source_url: 'http://...'
            }
        :returns: dict
        '''
        r = requests.get(
            self._url.format(
                apikey=self.apikey,
                id=show_id,
                type='en.xml',
            )
        )
        if r.status_code == 200:
            data = xmltodict.parse(r.content)

            show = data['Data']['Series']
            if show.get('Overview'):
                return {
                    'text': show['Overview'],
                    'title': 'TheTVDB',
                    'url': self._source_url.format(id=show_id),
                }
        return None
        
register_importer(Thetvdb())
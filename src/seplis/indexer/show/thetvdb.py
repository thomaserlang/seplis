import requests
import xmltodict
import logging
from dateutil import parser
from seplis.indexer.show.base import Show_indexer_base

class Thetvdb(Show_indexer_base):
    _url = 'http://thetvdb.com/api/{apikey}/series/{id}/{type}'
    _source_url = 'http://thetvdb.com/?tab=series&id={id}'
    _url_updates = 'http://thetvdb.com/api/Updates.php?type=all&time={}'
    _url_episode = 'http://thetvdb.com/api/{apikey}/episodes/{id}/en.xml'

    def __init__(self, apikey):
        super().__init__('thetvdb', apikey=apikey)

    def get_show(self, show_id):
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
            return {
                'title': data['Data']['Series']['SeriesName'],
                'description': description,
                'premiered': self.parse_date(data['Data']['Series']['FirstAired']),
                'ended': None,               
                'externals': {
                    'thetvdb': str(show_id),
                },
                'status': self.parse_status(data['Data']['Series']['Status']),
            }

    def get_episodes(self, show_id):
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

    def get_updates(self):
        data = self.get_update_data()
        if not data:
            return
        ids = []
        for id_ in data['Series']:
            ids.append(id_)
        for id_ in data['Episode']:
            ids.append(
                self.episode_id_to_show_id(
                    id_,
                )
            )
        return ids

    def get_update_data(self):
        timestamp = self.get_latest_update_timestamp()
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

    def parse_date(self, date):
        if not date:
            return None
        try:
            return parser.parse(date).strftime('%Y-%m-%d')
        except ValueError as e:
            logging.exception('Parsing date "{}" faild with error: {}'.format(date))
        return None

    def get_show_photos_urls(self, show_id):
        '''
        :returns: list of urls
        '''
        r = requests.get(
            self._url.format(
                apikey=self.apikey,
                id=show_id,
                type='banners.xml',
            )
        )
        banners = []
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            if isinstance(data['Banners']['Banner'], list):
                for banner in data['Banners']['Banner']:
                    banners.append('http://thetvdb.com/banners/{}'.format(banner['BannerPath']))
            else:
                banners.append('http://thetvdb.com/banners/{}'.format(data['Banners']['Banner']['BannerPath']))
        return banners

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
        
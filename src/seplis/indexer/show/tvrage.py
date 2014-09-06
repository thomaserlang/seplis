import requests
import xmltodict
import unittest
import sys
import dateutil
import re
import logging
from dateutil import parser, tz
from datetime import timedelta, datetime
from xmltodict import OrderedDict
from seplis.indexer.show.base import Show_indexer_base

class Tvrage(Show_indexer_base):
    _url_show_info = 'http://services.tvrage.com/feeds/showinfo.php?sid={show_id}'
    _url_episode_list = 'http://services.tvrage.com/feeds/episode_list.php?sid={show_id}'
    _url_updates = 'http://services.tvrage.com/feeds/last_updates.php?since={}'

    def __init__(self, apikey=None):
        super().__init__('tvrage', apikey=apikey)

    def get_show(self, show_id):
        logging.debug('({}) Retrieving show info.'.format(show_id))
        r = requests.get(
            url=self._url_show_info.format(show_id=show_id)
        )
        if r.status_code == 200:
            show_info = xmltodict.parse(
                r.content
            )
            logging.debug('({}) Show XML parsed successfully.'.format(show_id))
            logging.debug('({}) Creating ShowIndexed object.'.format(show_id))
            show_info = show_info['Showinfo']
            ended = self.parse_date(show_info.get('ended'))
            return {
                'title': show_info.get('showname'),
                'premiered': self.parse_date(show_info.get('startdate')),
                'ended': ended,
                'externals': {
                    'tvrage': str(show_id),
                },
                'description': None,
                'status': 1 if not ended else 2,
            }
        return None

    def get_episodes(self, show_id):
        logging.debug('({}) Retrieving episode info.'.format(show_id))
        episode_list = xmltodict.parse(
            requests.get(
                url=self._url_episode_list.format(show_id=show_id)
            ).content
        )
        logging.debug('({}) Episode XML parsed successfully.'.format(show_id))
        return self.parse_episode_list(
            show_id, 
            episode_list,
        )

    def get_updates(self, store_latest_timestamp=True):
        timestamp = self.get_latest_update_timestamp()        
        r = requests.get(
            self._url_updates.format(
                timestamp,
            )
        )
        show_ids = []
        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            if 'updates' in data and \
                'show' in data['updates']:
                if not isinstance(data['updates']['show'], list):
                    data['updates']['show'] = [data['updates']['show']]
                for show in data['updates']['show']:
                    show_ids.append(
                        int(show['id'])
                    )
        if store_latest_timestamp:
            self.set_latest_update_timestamp()
        return show_ids


    def parse_episode_list(self, show_id, episode_list):
        logging.debug('({}) Episode indexing started.'.format(show_id))
        episodes = []

        def parse_season(season_info):
            season = season_info['@no']
            logging.debug('({}) Parsing season {}.'.format(show_id, season))
            if season:
                try:
                    if isinstance(season_info['episode'], list):
                        for episode in season_info['episode']:
                            episodes.append(self.parse_episode(show_id, season, episode))
                    else:
                        episodes.append(self.parse_episode(show_id, season, season_info['episode']))
                except Exception as e:
                    logging.error('({}) Parsing season {} failed with error: {}.'.format(show_id, season, e))
        if not episode_list['Show'].get('Episodelist'):
            return []
        if not episode_list['Show']['Episodelist'].get('Season'):
            return []
        if isinstance(episode_list['Show']['Episodelist']['Season'], list):
            for season_info in episode_list['Show']['Episodelist']['Season']:
                parse_season(season_info)
        else:
            parse_season(episode_list['Show']['Episodelist']['Season'])
        return episodes
        
    def parse_network(self, show_info):
        if show_info.get('network'):
            if show_info['network'].get('#text'):
                return {'name': show_info['network']['#text']}
        return None

    def parse_episode(self, show_id, season, episode):
        logging.debug('({}) Parsing episode. Season {}, episode: {}.'.format(show_id, season, episode))
        try:
            return dict(
                title=episode['title'],
                air_date=self.parse_date(episode['airdate']),
                number=int(episode['epnum']),
                season=int(season),
                episode=int(episode['seasonnum']),
            )
        except Exception as e:
            logging.exception('({}) Parsing Season {}, episode: {} failed with error.'.format(show_id, season, episode))
            raise
    
    def parse_airday(self, airday):
        try:
            return int(datetime.strptime(airday, '%A').strftime('%w'))
        except:
            if airday == 'Weekdays':
                return 8 #Mon, tue, wed, thu,
            elif airday == 'Daily':
                return 9
            if airday == None:
                return None
            raise Exception('Unknown airday: %s' % airday)

    def parse_date(self, date):
        if date:
            if date[-2:] == '00':
                return None
            if date[5:-3] == '00':
                return None
            if date.count('/') == 1:
                date = '01/'+date
            if date == '0000-00-00':
                return None
            try:
                return parser.parse(date).strftime('%Y-%m-%d')
            except ValueError as e:
                logging.exception('Parsing failed for date "{}"'.format(date))
                raise
        return None

    def parse_genres(self, show):
        if show:
            if 'genres' in show:
                return show['genres']['genre']
        return []

    def parse_airtime(self, airtime, timezone):
        if not airtime:
            return None
        offset = self.parse_timezone(timezone)
        time = parser.parse(airtime) + timedelta(hours=offset)
        return time.strftime('%H:%M:%S')

    def parse_timezone(self, timezone):
        if not timezone:
            return 0
        m = re.match('GMT([0-9\-+]+) ([+\-]DST)', timezone)
        offset = 0
        if m:
            offset = int(m.group(1))
            if offset < 0:
                offset = abs(offset)
            elif offset > 0:
                offset = -offset
        return offset
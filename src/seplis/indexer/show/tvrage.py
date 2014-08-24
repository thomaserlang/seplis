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

class Tvrage:
    _url_show_info = 'http://services.tvrage.com/feeds/showinfo.php?sid={show_id}'
    _url_episode_list = 'http://services.tvrage.com/feeds/episode_list.php?sid={show_id}'

    @classmethod
    def get_show(cls, show_id):
        logging.debug('({}) Retrieving show info.'.format(show_id))
        r = requests.get(
            url=cls._url_show_info.format(show_id=show_id)
        )
        if r.status_code == 200:
            show_info = xmltodict.parse(
                r.content
            )
            show_info = show_info['Showinfo']
            logging.debug('({}) Show XML parsed successfully.'.format(show_id))
            logging.debug('({}) Creating ShowIndexed object.'.format(show_id))
            ended = cls.parse_date(show_info.get('ended'))
            return {
                'title': show_info.get('showname'),
                'premiered': cls.parse_date(show_info.get('startdate')),
                'ended': ended,
                'externals': {
                    'tvrage': str(show_id),
                },
                'description': None,
                'status': 1 if not ended else 2,
            }
        return None

    @classmethod
    def get_episodes(cls, show_id):
        logging.debug('({}) Retrieving episode info.'.format(show_id))
        episode_list = xmltodict.parse(
            requests.get(
                url=cls._url_episode_list.format(show_id=show_id)
            ).content
        )
        logging.debug('({}) Episode XML parsed successfully.'.format(show_id))
        return cls.parse_episode_list(
            show_id, 
            episode_list,
        )

    @classmethod
    def parse_episode_list(cls, show_id, episode_list):
        logging.debug('({}) Episode indexing started.'.format(show_id))
        episodes = []

        def parse_season(season_info):
            season = season_info['@no']
            logging.debug('({}) Parsing season {}.'.format(show_id, season))
            if season:
                try:
                    if isinstance(season_info['episode'], list):
                        for episode in season_info['episode']:
                            episodes.append(cls.parse_episode(show_id, season, episode))
                    else:
                        episodes.append(cls.parse_episode(show_id, season, season_info['episode']))
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

    """
    @classmethod
    def parse(cls, show_info):
        show = {}
        show_info = show_info['Showinfo']
        show['name'] = show_info.get('showname')
        show['premiered'] = cls.parse_date(show_info.get('startdate'))
        show['ended'] = cls.parse_date(show_info.get('ended'))
        show['genres_names'] = cls.parse_genres(show_info)
        #show['airday'] = cls.parse_airday(show_info.get('airday'))
        show['airtime'] = cls.parse_airtime(show_info.get('airtime'), show_info.get('timezone'))
        show['runtime'] = int(show_info.get('runtime', 0))
        show['tv_channel'] = cls.parse_network(show_info)
        #show['country'] = show_info.get('origin_country')
        return show
    """

    @classmethod
    def parse_network(cls, show_info):
        if show_info.get('network'):
            if show_info['network'].get('#text'):
                return {'name': show_info['network']['#text']}
        return None

    @classmethod
    def parse_episode(cls, show_id, season, episode):
        logging.debug('({}) Parsing episode. Season {}, episode: {}.'.format(show_id, season, episode))
        try:
            return dict(
                title=episode['title'],
                air_date=cls.parse_date(episode['airdate']),
                number=int(episode['epnum']),
                season=int(season),
                episode=int(episode['seasonnum']),
            )
        except Exception as e:
            logging.exception('({}) Parsing Season {}, episode: {} failed with error.'.format(show_id, season, episode))
            raise

    @classmethod    
    def parse_airday(cls, airday):
        try:
            return int(datetime.strptime(airday, "%A").strftime('%w'))
        except:
            if airday == 'Weekdays':
                return 8 #Mon, tue, wed, thu,
            elif airday == 'Daily':
                return 9
            if airday == None:
                return None
            raise Exception('Unknown airday: %s' % airday)

    @classmethod
    def parse_date(cls, date):
        if date:
            if date[-2:] == '00':
                return date[:-3]
            try:
                return parser.parse(date).strftime('%Y-%m-%d')
            except ValueError as e:
                logging.exception('Parsing failed for date "{}"'.format(date))
                raise
        return None

    @classmethod
    def parse_genres(cls, show):
        if show:
            if 'genres' in show:
                return show['genres']['genre']
        return []

    @classmethod
    def parse_airtime(cls, airtime, timezone):
        if not airtime:
            return None
        offset = cls.parse_timezone(timezone)
        time = parser.parse(airtime) + timedelta(hours=offset)
        return time.strftime('%H:%M:%S')

    @classmethod
    def parse_timezone(cls, timezone):
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

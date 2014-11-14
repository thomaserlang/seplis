import os, os.path
import re
import logging
from datetime import datetime
from seplis import config, Client
from seplis.play import constants, models
from seplis.play.decorators import new_session

SCAN_TYPES = (
    'shows',
)

class Parsed_episode(object):

    def __init__(self):
        self.show_id = None
        self.number = None

class Parsed_episode_season(Parsed_episode):

    def __init__(self, show_title, season, episode, path):
        super().__init__()
        self.lookup_type = 1
        self.show_title = show_title
        self.season = season
        self.episode = episode
        self.path = path

class Parsed_episode_airdate(Parsed_episode):

    def __init__(self, show_title, airdate, path):
        super().__init__()
        self.lookup_type = 2
        self.show_title = show_title
        self.airdate = airdate
        self.path = path

class Parsed_episode_number(Parsed_episode):

    def __init__(self, show_title, number, path):
        super().__init__()
        self.show_title = show_title
        self.number = number
        self.path = path

class Play_scan(object):

    def __init__(self, scan_path, type_='shows'):
        if not scan_path:
            raise Exception('scan_path is missing')
        if not os.path.exists(scan_path):
            raise Exception('scan_path "{}" does not exist'.format(scan_path))
        if type_ not in SCAN_TYPES:
            raise Exception('scan type: "{}" is not supported'.format(type_))
        self.scan_path = scan_path
        self.type = type_
        self.client = Client(url=config['client']['api_url'])

    def scan(self):
        files = self.get_files()
        episodes = parse_episodes(files)

    def get_files(self):
        '''
        Looks for files in the `self.scan_path` directory.
        '''
        files = []
        for dirname, dirnames, filenames in os.walk(self.scan_path):
            for file_ in filenames:
                info = os.path.splitext(file_)
                if len(info) != 2:
                    continue

                if info[1][1:] not in config['play']['media_types']:
                    continue
                files.append(
                    os.path.join(dirname, file_)
                )
        return files

    def episode_show_lookup(self, episodes):
        with new_session() as session:
            for episode in episodes:
                show_id = show_id_lookup(episode.show_title)
                if show_id:
                    episode.show_id = show_id

    def show_id_lookup(self, show_title):
        '''

        :param show_title: str
        :returns: int
        '''
        show_id = self.show_id_db_lookup(show_title)
        if show_id:
            return show_id
        shows = self.shows_web_lookup(show_title)
        if not shows:
            return
        show_id = shows[0]['id']
        with new_session() as session:
            show = models.Show_id_lookup(
                show_title=show_title,
                show_id=show_id,
                updated=datetime.utcnow(),
            )
            session.add(show)
            session.commit()
        return show_id

    def show_id_db_lookup(self, show_title):        
        '''

        :param show_title: str
        :returns: int
        '''
        with new_session() as session:
            show = session.query(
                models.Show_id_lookup
            ).filter(
                models.Show_id_lookup.show_title == show_title,
            ).first()
            if not show:
                return
            print(show.show_title)
            return show.show_id

    def shows_web_lookup(self, show_title):
        '''

        :param show_title: str
        :returns: list of dict
            [
                {
                    'id': 1,
                    'title': 'Show...'
                }
            ]
        '''
        shows = self.client.get('/shows', {
            'q': 'title:"{show_title}" alternative_titles:"{show_title}"'.format(
                show_title=show_title,
            ),
            'fields': 'id, title',
        })
        return shows

    def episode_number_lookup(self, episode):
        if isinstance(episode, Parsed_episode_number):
            return episode.number
        pass

    def episode_number_db_lookup(self, episode):
        with new_session() as session:
            value = ''
            if isinstance(episode, Parsed_episode_season):
                value = '{}-{}'.format(
                    episode.season,
                    episode.episode,
                )
            elif isinstance(episode, Parsed_episode_airdate):
                value = '{}'.format(
                    episode.airdate,
                )
            else:
                raise Exception('Unknown parsed episode object')
            e = session.query(
                models.Episode_lookup.number
            ).filter(
                models.Episode_number_lookup.show_id == episode.show_id,
                models.Episode_number_lookup.lookup_type == episode.lookup_type,
                models.Episode_number_lookup.lookup_value == value,
            ).first()
            if not e:
                return
            return e.number

    def episode_number_web_lookup(self, episode):
        if isinstance(episode, Parsed_episode_season):
            query = 'season:{} AND episode:{}'.format(
                episode.season,
                episode.episode,
            )
        elif isinstance(episode, Parsed_episode_airdate):
            query = 'airdate:{}'.format(
                episode.airdate,
            )
        else:
            raise Exception('Unknown parsed episode object')
        episode = self.client.get('/shows/{}/episodes'.format(episode.show_id), {
            'q': query,
        })

    def save_episodes(self, episodes):
        with new_session() as session:
            for episode in episodes:
                if not episode.show_id:
                    continue
                e = models.Episode(
                    show_id=episode.show_id,
                    number=0
                )

def parse_episodes(files):
    episodes = []
    for file_ in files:
        e = parse_episode(file_)
        if e:
            episodes.append(e)
    return episodes

def parse_episode(file_):
    for pattern in constants.FILENAME_PATTERNS:
        try:
            match = re.match(
                pattern, 
                os.path.basename(file_), 
                re.VERBOSE
            )
            if not match:
                continue
            return _parse_episode_info_from_file(
                file_=file_, 
                match=match,
            )
        except re.error as error:
            logging.exception('episode parse re error: {}'.format(error))
        except:
            logging.exception('episode parse pattern: {}'.format(pattern))


def _parse_episode_info_from_file(file_, match):
    fields = match.groupdict().keys()
    season = None
    if 'show_title' not in fields:
        return None
    show_title = match.group('show_title').strip().replace('.', ' ')

    season = None
    if 'season' in fields:
        season = int(match.group('season'))

    number = None
    if 'number' in fields:
        number = match.group('number')
    elif 'number1' in fields:
        number = match.group('number1')
    elif 'numberstart' in fields:
        number = match.group('numberstart')
    if number:
        number = int(number)

    date = None
    if 'year' in fields and 'month' in fields and 'day' in fields:
        airdate = '{}-{}-{}'.format(
            match.group('year'),
            match.group('month'),
            match.group('day'),
        )

    if season and number:
        return Parsed_episode_season(
            show_title=show_title,
            season=season,
            episode=number,
            path=file_,
        )
    elif not season and number:
        return Parsed_episode_number(
            show_title=show_title,
            number=number,
            path=file_,
        )
    elif airdate:
        return Parsed_episode_airdate(
            show_title=show_title,
            airdate=airdate,
            path=file_,
        )

def main():
    pass
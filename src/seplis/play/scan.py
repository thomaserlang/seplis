import os, os.path
import re
import logging
import time
import subprocess
from datetime import datetime
from seplis import config, Client, utils
from seplis.play import constants, models
from seplis.play.decorators import new_session

SCAN_TYPES = (
    'shows',
)

class Parsed_episode(object):

    def __init__(self):
        self.lookup_type = 0
        self.show_id = None
        self.number = None

class Parsed_episode_season(Parsed_episode):

    def __init__(self, show_title, season, episode, path, show_id=None, number=None):
        super().__init__()
        self.lookup_type = 1
        self.show_title = show_title
        self.season = season
        self.episode = episode
        self.path = path
        self.show_id = show_id
        self.number = number

class Parsed_episode_air_date(Parsed_episode):

    def __init__(self, show_title, air_date, path, show_id=None, number=None):
        super().__init__()
        self.lookup_type = 2
        self.show_title = show_title
        self.air_date = air_date
        self.path = path
        self.show_id = show_id
        self.number = number

class Parsed_episode_number(Parsed_episode):

    def __init__(self, show_title, number, path, show_id=None):
        super().__init__()
        self.show_title = show_title
        self.number = number
        self.path = path
        self.show_id = show_id

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

    def get_metadata(self, path):
        '''
        :returns: dict
            metadata is a `dict` taken from the result of ffprobe.
        '''
        logging.info('Retrieving metadata from "{}"'.format(
            path,
        ))
        if not os.path.exists(path):
            raise Exception('Path "{}" does not exists'.format(path))
        ffprobe = os.path.join(config['play']['ffmpeg_folder'], 'ffprobe')
        if not os.path.exists(ffprobe):
            raise Exception('ffprobe not found in "{}"'.format(
                config['play']['ffmpeg_folder'],
            ))
        cmd = [
            ffprobe,
            '-show_streams',
            '-show_format',
            '-loglevel', 'quiet',
            '-print_format', 'json',
            path,
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        data = process.stdout.read()
        if not data:
            return
        if isinstance(data, bytes):
            data = data.decode('utf-8')        
        logging.info('Metadata retrieved from "{}"'.format(
            path,
        ))
        return utils.json_loads(data)

    def get_file_modified_time(self, path):
        return datetime.utcfromtimestamp(
            os.path.getmtime(path)
        )

class Shows_scan(Play_scan):

    def __init__(self, scan_path):
        super().__init__(
            scan_path=scan_path,
            type_='shows',
        )
        self.show_id = Show_id(
            scanner=self,
        )
        self.episode_number = Episode_number(
            scanner=self
        )

    def scan(self):
        episodes = self.get_episodes()
        if not episodes:
            return
        for episode in episodes:
            if not self.episode_show_id_lookup(episode):
                continue
            if not self.episode_number_lookup(episode):
                continue
            self.save_episode(episode)

    def get_episodes(self):
        files = self.get_files()
        episodes = parse_episodes(files)
        logging.info('Found {} episodes in path "{}"'.format(
            len(episodes),
            self.scan_path,
        ))
        print(len(episodes))
        return episodes

    def episode_show_id_lookup(self, episode):
        '''

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        logging.info('Looking for a show with title: "{}"'.format(
            episode.show_title
        ))
        show_id = self.show_id.lookup(episode.show_title)
        if show_id:
            logging.info('Found show: "{}" with show id: "{}"'.format(
                episode.show_title,
                show_id,
            ))
            episode.show_id = show_id
            return True
        else:
            logging.info('No show found for title: "{}"'.format(
                episode.show_title,
            ))
        return False

    def episode_number_lookup(self, episode):
        '''

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.show_id:
            return
        if isinstance(episode, Parsed_episode_number):
            return
        value = self.episode_number.get_lookup_value(episode)
        logging.info('Looking for episode {} with show_id {}'.format(
            value,
            episode.show_id,
        ))
        number = self.episode_number.lookup(episode)
        if number:                
            logging.info('Found episode {} from {} with show_id {}'.format(
                number,
                value,
                episode.show_id,
            ))
            episode.number = number
            return True
        else:
            logging.info('No episode was found for {} with show_id {}'.format(
                value,
                episode.show_id,
            ))
        return False

    def save_episode(self, episode):
        '''
        If the object has `show_id`, `number` and `path`
        is filled the episode will be saved.

        :param episodes: list of `Parsed_episode()`
        '''
        updated = 0
        with new_session() as session:
            if not episode.show_id or not episode.number:
                return False
            ep = session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == episode.show_id,
                models.Episode.number == episode.number,
            ).first()
            modified_time = self.get_file_modified_time(episode.path)
            if ep and ep.modified_time == modified_time:
                return
            metadata = self.get_metadata(episode.path)
            e = models.Episode(
                show_id=episode.show_id,
                number=episode.number,
                path=episode.path,
                meta_data=metadata,
                modified_time=modified_time,
            )
            session.merge(e)
            session.commit()

class Show_id(object):

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, show_title):
        '''
        Tries to find the show on SEPLIS by it's title.

        :param show_title: str
        :returns: int
        '''
        show_id = self.db_lookup(show_title)
        if show_id:
            return show_id
        shows = self.web_lookup(show_title)
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

    def db_lookup(self, show_title):        
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
            return show.show_id

    def web_lookup(self, show_title):
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
        shows = self.scanner.client.get('/shows', {
            'q': 'title:"{show_title}" alternative_titles:"{show_title}"'.format(
                show_title=show_title,
            ),
            'fields': 'id,title',
        })
        return shows

class Episode_number(object):

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, episode):
        if not episode.show_id:
            raise Exception('show_id must be defined in the episode object')
        if isinstance(episode, Parsed_episode_number):
            return episode.number
        number = self.db_lookup(episode)
        if number:
            return number
        number = self.web_lookup(episode)
        if not number:
            return
        with new_session() as session:
            e = models.Episode_number_lookup(
                show_id=episode.show_id,
                lookup_type=episode.lookup_type,
                lookup_value=self.get_lookup_value(episode),
                number=number,
            )
            session.add(e)
            session.commit()
        return number

    def db_lookup(self, episode):
        with new_session() as session:
            value = self.get_lookup_value(episode)
            e = session.query(
                models.Episode_number_lookup.number
            ).filter(
                models.Episode_number_lookup.show_id == episode.show_id,
                models.Episode_number_lookup.lookup_type == episode.lookup_type,
                models.Episode_number_lookup.lookup_value == value,
            ).first()
            if not e:
                return
            return e.number

    @staticmethod
    def get_lookup_value(episode):
        value = None
        if isinstance(episode, Parsed_episode_season):
            value = '{}-{}'.format(
                episode.season,
                episode.episode,
            )
        elif isinstance(episode, Parsed_episode_air_date):
            value = '{}'.format(
                episode.air_date,
            )
        else:
            raise Exception('''
                Unknown parsed episode object. 
                If the episode already contains a number there is no need 
                to use this method.
            ''')
        return value

    def web_lookup(self, episode):
        if isinstance(episode, Parsed_episode_season):
            query = 'season:{} AND episode:{}'.format(
                episode.season,
                episode.episode,
            )
        elif isinstance(episode, Parsed_episode_air_date):
            query = 'air_date:{}'.format(
                episode.air_date,
            )
        else:
            raise Exception('Unknown parsed episode object')
        episodes = self.scanner.client.get('/shows/{}/episodes'.format(episode.show_id), {
            'q': query,
            'fields': 'number',
        })
        if not episodes:
            return
        return episodes[0]['number']

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
    show_title = match.group('show_title').strip()\
        .replace('.', ' ')\
        .replace('-', ' ')\
        .replace('_', ' ')

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

    air_date = None
    if 'year' in fields and 'month' in fields and 'day' in fields:
        air_date = '{}-{}-{}'.format(
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
    elif air_date:
        return Parsed_episode_air_date(
            show_title=show_title,
            air_date=air_date,
            path=file_,
        )

def upgrade_scan_db():
    import alembic.config
    from alembic import command
    cfg = alembic.config.Config(
        os.path.dirname(
            os.path.abspath(__file__)
        )+'/alembic.ini'
    )
    cfg.set_main_option('script_location', 'seplis.play:migration')
    cfg.set_main_option('url', config['play']['database'])
    command.upgrade(cfg, 'head')

def main():
    pass
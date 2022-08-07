import os, os.path, re, logging, subprocess
from datetime import datetime
from seplis import config, Client, utils
from seplis.play import constants, models
from seplis.play.decorators import new_session
from guessit import guessit


def scan():
    if not config.data.play.scan:
        raise Exception('''
            Nothing to scan. Add a path in the config file.

            Example:

                play:
                    scan:
                        -
                            type: series
                            path: /a/path/to/the/series
            ''')
    for s in config.data.play.scan:    
        try:
            scanner = None
            if s.type == 'series':
                scanner = Series_scan(s.path)
            elif s.type == 'movies':
                scanner = Movie_scan(s.path)
            if not scanner:
                raise Exception(f'Scan type: "{s.type}" is not supported')
            scanner.scan()
        except:        
            logging.exception('play scan')

def cleanup():
    logging.info('Cleanup started')
    cleanup_episodes()
    cleanup_movies()

def cleanup_episodes():
    with new_session() as session:
        episodes = session.query(models.Episode).all()
        deleted_count = 0
        for e in episodes:
            if os.path.exists(e.path):
                continue
            deleted_count += 1
            session.delete(e)
        session.commit()
        logging.info(f'{deleted_count} episodes was deleted from the database')

def cleanup_movies():
    with new_session() as session:
        movies = session.query(models.Movie).all()
        deleted_count = 0
        for m in movies:
            if os.path.exists(m.path):
                continue
            deleted_count += 1
            session.delete(m)
        session.commit()
        logging.info(f'{deleted_count} movies was deleted from the database')

class Play_scan(object):

    def __init__(self, scan_path, type_='series'):
        if not os.path.exists(scan_path):
            raise Exception(f'scan_path "{scan_path}" does not exist')
        self.scan_path = scan_path
        self.type = type_
        self.client = Client(url=config.data.client.api_url)

    def save_item(self, item, path):
        raise NotImplementedError()

    def parse(self, filename):
        raise NotImplementedError()

    def delete_item(self, item, path):
        raise NotImplementedError()

    def get_files(self):
        '''
        Looks for files in the `self.scan_path` directory.
        '''
        files = []
        for dirname, dirnames, filenames in os.walk(self.scan_path):
            for file_ in filenames:
                info = os.path.splitext(file_)
                if file_.startswith('._'):
                    continue
                if len(info) != 2:
                    continue
                if info[1][1:].lower() not in config.data.play.media_types:
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
        logging.info(f'Retrieving metadata from "{path}"')
        if not os.path.exists(path):
            raise Exception(f'Path "{path}" does not exist')
        ffprobe = os.path.join(config.data.play.ffmpeg_folder, 'ffprobe')
        if not os.path.exists(ffprobe):
            raise Exception(f'ffprobe not found in "{config.data.play.ffmpeg_folder}"')
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
        error = process.stderr.read()
        if error:        
            if isinstance(error, bytes):
                error = error.decode('utf-8')   
            raise Exception('FFprobe error: {}'.format(error))
        if not data:
            return
        if isinstance(data, bytes):
            data = data.decode('utf-8')        
        logging.info(f'Metadata retrieved from "{path}"')
        data = utils.json_loads(data)
        return data

    def get_file_modified_time(self, path):
        return datetime.utcfromtimestamp(
            os.path.getmtime(path)
        )

class Movie_scan(Play_scan):

    def __init__(self, scan_path):
        super().__init__(
            scan_path=scan_path,
            type_='movies',
        )

    def scan(self):
        logging.info(f'Scanning: {self.scan_path}')
        files = self.get_files()
        for f in files:
            title = self.parse(f)
            if title:
                self.save_item(title, f)
            else:
                logging.debug(f'"{f}" didn\'t match any pattern')

    def parse(self, filename):
        d = guessit(filename, '-t movie')
        if d and d.get('title'):
            t = d['title']
            if d.get('part'):
                t += f' Part {d["part"]}'
            if d.get('year'):
                t += f" {d['year']}"
            return t        
        logging.info(f'{filename} doesn\'t look like a movie')

    def save_item(self, title: str, path: str):
        movie_id = self.lookup(title)
        if not movie_id:
            return

        with new_session() as session:
            movie = session.query(models.Movie).filter(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ).first()
            modified_time = self.get_file_modified_time(path)
            if movie and (movie.modified_time == modified_time) and movie.meta_data:
                return
            metadata = self.get_metadata(path)
            if not metadata:
                return
            e = models.Movie(
                movie_id=movie_id,
                path=path,
                meta_data=metadata,
                modified_time=modified_time,
            )
            session.merge(e)
            session.commit()
            logging.info(f'Saved movie: {title} (Id: {movie_id}) - Path: {path}')
            return True

    def lookup(self, title: str):
        logging.info(f'Looking for a movie with title: "{title}"')
        with new_session() as session:
            movie = session.query(models.Movie_id_lookup).filter(
                models.Movie_id_lookup.file_title == title,
            ).first()
            if not movie:
                movies = self.client.get('/search', {
                    'title': title,
                    'type': 'movie',
                })
                if not movies:
                    logging.info(f'Didn\'t find a match for movie "{title}"')
                    return
                logging.info(f'Found movie: {movies[0]["title"]} (Id: {movies[0]["id"]})')
                movie = models.Movie_id_lookup(
                    file_title=title,
                    movie_title=movies[0]["title"],
                    movie_id=movies[0]["id"],
                    updated_at=datetime.utcnow(),
                )
                session.merge(movie)
                session.commit()
                return movie.movie_id
            else:                
                logging.info(f'Found movie from cache: {movie.movie_title} (Id: {movie.movie_id})')
                return movie.movie_id

    def delete_item(self, title, path):        
        movie_id = self.lookup(title)
        with new_session() as session:
            m = session.query(
                models.Movie,
            ).filter(
                models.Movie.movie_id == movie_id,
                models.Movie.path == path,
            ).first()
            if m:
                session.delete(m)
                session.commit()
                logging.info(f'Deleted movie: {title} (Id: {movie_id}) - Path: {path}')
                return True
        return False

class Series_scan(Play_scan):

    def __init__(self, scan_path):
        super().__init__(
            scan_path=scan_path,
            type_='series',
        )
        self.series_id = Series_id(scanner=self)
        self.episode_number = Episode_number(scanner=self)
        self.not_found_series = []

    def scan(self):
        logging.info(f'Scanning: {self.scan_path}')
        files = self.get_files()
        for f in files:
            episode = self.parse(f)
            if episode:
                self.save_item(episode, f)
            else:
                logging.debug(f'"{f}" didn\'t match any pattern')

    def parse(self, filename):

        for pattern in constants.SERIES_FILENAME_PATTERNS:
            try:
                match = re.match(
                    pattern, 
                    os.path.basename(filename), 
                    re.VERBOSE | re.IGNORECASE
                )
                if not match:
                    continue
                return self._parse_episode_info_from_file(match=match)
            except re.error as error:
                logging.exception('episode parse re error: {}'.format(error))
            except:
                logging.exception('episode parse pattern: {}'.format(pattern))

    def episode_series_id_lookup(self, episode):
        '''

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if episode.file_title in self.not_found_series:
            return False
        logging.info('Looking for a series with title: "{}"'.format(
            episode.file_title
        ))
        series_id = self.series_id.lookup(episode.file_title)
        if series_id:
            logging.info('Found series: "{}" with series id: {}'.format(
                episode.file_title,
                series_id,
            ))
            episode.series_id = series_id
            return True
        else:
            self.not_found_series.append(episode.file_title)
            logging.info('No series found for title: "{}"'.format(
                episode.file_title,
            ))
        return False

    def episode_number_lookup(self, episode):
        '''
        Tries to lookup the episode number of the episode.
        Sets the number in the episode object if successful.

        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.series_id:
            return
        if isinstance(episode, Parsed_episode_number):
            return True
        value = self.episode_number.get_lookup_value(episode)
        logging.info('Looking for episode {} with series_id {}'.format(
            value,
            episode.series_id,
        ))
        number = self.episode_number.lookup(episode)
        if number:                
            logging.info('Found episode {} from {} with series_id {}'.format(
                number,
                value,
                episode.series_id,
            ))
            episode.number = number
            return True
        else:
            logging.info('No episode was found for {} with series_id {}'.format(
                value,
                episode.series_id,
            ))
        return False

    def save_item(self, episode, path):
        '''
        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.series_id:
            if not self.episode_series_id_lookup(episode):
                return False
        if not episode.number:
            if not self.episode_number_lookup(episode):
                return False
        with new_session() as session:
            ep = session.query(
                models.Episode,
            ).filter(
                models.Episode.series_id == episode.series_id,
                models.Episode.number == episode.number,
            ).first()
            modified_time = self.get_file_modified_time(path)
            if ep and (ep.modified_time == modified_time) and \
                (ep.path == path) and ep.meta_data:
                return
            metadata = self.get_metadata(path)
            e = models.Episode(
                series_id=episode.series_id,
                number=episode.number,
                path=path,
                meta_data=metadata,
                modified_time=modified_time,
            )
            session.merge(e)
            session.commit()
            logging.info('Saved episode: {} {}'.format(
                episode.file_title,
                episode.number
            ))
            return True

    def delete_item(self, episode, path):        
        '''
        :param episode: `Parsed_episode()`
        :returns: bool
        '''
        if not episode.series_id:
            if not self.episode_series_id_lookup(episode):
                return False
        if not episode.number:
            if not self.episode_number_lookup(episode):
                return False
        with new_session() as session:
            ep = session.query(
                models.Episode,
            ).filter(
                models.Episode.series_id == episode.series_id,
                models.Episode.number == episode.number,
            ).first()
            if ep:
                session.delete(ep)
                session.commit()
                logging.info('Deleted episode: {} {}'.format(
                    episode.file_title,
                    episode.number
                ))
                return True
        return False

    def _parse_episode_info_from_file(self, match):
        fields = match.groupdict().keys()
        season = None
        if 'file_title' not in fields:
            return None
        file_title = match.group('file_title').strip().lower()

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
                file_title=file_title,
                season=season,
                episode=number,
            )
        elif not season and number:
            return Parsed_episode_number(
                file_title=file_title,
                number=number,
            )
        elif air_date:
            return Parsed_episode_air_date(
                file_title=file_title,
                air_date=air_date,
            )

class Parsed_episode(object):

    def __init__(self):
        self.lookup_type = 0
        self.series_id = None
        self.number = None

class Parsed_episode_season(Parsed_episode):

    def __init__(self, file_title, season, episode, series_id=None, number=None):
        super().__init__()
        self.lookup_type = 1
        self.file_title = file_title
        self.season = season
        self.episode = episode
        self.series_id = series_id
        self.number = number

class Parsed_episode_air_date(Parsed_episode):

    def __init__(self, file_title, air_date, series_id=None, number=None):
        super().__init__()
        self.lookup_type = 2
        self.file_title = file_title
        self.air_date = air_date
        self.series_id = series_id
        self.number = number

class Parsed_episode_number(Parsed_episode):

    def __init__(self, file_title, number, series_id=None):
        super().__init__()
        self.file_title = file_title
        self.number = number
        self.series_id = series_id

class Series_id(object):
    '''Used to lookup a series id by it's title.
    The result will be cached in the local db.
    '''

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, file_title):
        '''
        Tries to find the series on SEPLIS by it's title.

        :param file_title: str
        :returns: int
        '''
        series_id = self.db_lookup(file_title)
        if series_id:
            return series_id
        series = self.web_lookup(file_title)
        series_id = series[0]['id'] if series else None
        series_title = series[0]['title'] if series else None
        with new_session() as session:
            series = models.Series_id_lookup(
                file_title=file_title,
                series_title=series_title,
                series_id=series_id,
                updated_at=datetime.utcnow(),
            )
            session.merge(series)
            session.commit()
        return series_id

    def db_lookup(self, file_title):        
        '''

        :param file_title: str
        :returns: int
        '''
        with new_session() as session:
            series = session.query(
                models.Series_id_lookup
            ).filter(
                models.Series_id_lookup.file_title == file_title,
            ).first()
            if not series or not series.series_id:
                return
            return series.series_id

    def web_lookup(self, file_title):
        series = self.scanner.client.get('/search', {
            'title': file_title,
            'type': 'series',
        })
        return series

class Episode_number(object):
    '''Used to lookup an episode's number from the season and episode or
    an air date.
    Stores the result in the local db.
    '''

    def __init__(self, scanner):
        self.scanner = scanner

    def lookup(self, episode):
        if not episode.series_id:
            raise Exception('series_id must be defined in the episode object')
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
                series_id=episode.series_id,
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
                models.Episode_number_lookup.series_id == episode.series_id,
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
        episodes = self.scanner.client.get('/series/{}/episodes'.format(episode.series_id), {
            'q': query,
            'fields': 'number',
        })
        if not episodes:
            return
        return episodes[0]['number']


def upgrade_scan_db():
    import alembic.config
    from alembic import command
    cfg = alembic.config.Config(
        os.path.dirname(
            os.path.abspath(__file__)
        )+'/alembic.ini'
    )
    cfg.set_main_option('script_location', 'seplis.play:migration')
    cfg.set_main_option('url', config.data.play.database)
    command.upgrade(cfg, 'head')
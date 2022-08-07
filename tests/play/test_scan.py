import unittest
import mock
from datetime import datetime
from seplis.play.connections import database
from seplis.play.decorators import new_session
from seplis.play.scan import Movie_scan, Play_scan, Series_scan, Parsed_episode_season, \
    Parsed_episode_air_date, Parsed_episode_number
from seplis.play import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Testbase(unittest.TestCase):

    def setUp(self):
        database.engine = create_engine(
            'sqlite://',# memory db
            echo=False, 
        )
        connection = database.engine.connect()
        database.session = sessionmaker(bind=connection)
        models.base.metadata.create_all(database.engine)

class test_scan(Testbase):

    def setUp(self):
        super().setUp()
        self.scanner = Play_scan('/', type_='series')
    
    def test_get_files(self):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = [                
                ('/series', ('NCIS', 'Person of Interest'), ()),
                ('/series/NCIS', ('Season 01', 'Season 02'), ()),
                ('/series/NCIS/Season 01', (), (
                    'NCIS.S01E01.Yankee White.avi',
                    'NCIS.S01E02.Hung Out to Dry.avi',
                )),
                ('/series/NCIS/Season 02', (), (
                    'NCIS.S02E01.See No Evil.avi',
                    'NCIS.S02E02.The Good Wives Club.avi',  
                )),
                ('/series/Person of Interest', ('Season 01'), ()),
                ('/series/Person of Interest/Season 01', (), (
                    'Person of Interest.S01E01.Pilot.mp4',
                    '._Person of Interest.S01E01.Pilot.mp4',
                )),
            ]

            files = self.scanner.get_files()
            self.assertEqual(files, [
                '/series/NCIS/Season 01/NCIS.S01E01.Yankee White.avi',
                '/series/NCIS/Season 01/NCIS.S01E02.Hung Out to Dry.avi',
                '/series/NCIS/Season 02/NCIS.S02E01.See No Evil.avi',
                '/series/NCIS/Season 02/NCIS.S02E02.The Good Wives Club.avi',
                '/series/Person of Interest/Season 01/Person of Interest.S01E01.Pilot.mp4',
            ])

    @mock.patch('subprocess.Popen')
    @mock.patch('os.path.exists')
    def test_get_metadata(self, mock_path_exists, mock_popen):
        mock_path_exists.return_value = True
        mock_popen().stdout.read.return_value = '{"metadata": "test"}'
        mock_popen().stderr.read.return_value = None
        self.assertEqual(
            self.scanner.get_metadata('somefile.mp4'),
            {'metadata': 'test'}
        )

    @mock.patch('os.path.getmtime')
    def test_get_file_modified_time(self, mock_getmtime):
        mock_getmtime.return_value = 1416000358
        self.assertEqual(
            datetime(2014, 11, 14, 21, 25, 58),
            self.scanner.get_file_modified_time('somefile.mp4'),
        )

class Test_movie_scan(Testbase):

    def test(self):
        scanner = Movie_scan('/')

        scanner.get_files = mock.MagicMock(return_value=[
            'Uncharted.mkv',
        ])
        scanner.client.get = mock.MagicMock(return_value=[
            {
                'title': 'Uncharted',
                'id': 1,
            }
        ])
        scanner.get_metadata = mock.MagicMock(return_value={
            'some': 'data',
        })
        scanner.get_file_modified_time = mock.MagicMock(return_value=datetime(2014, 11, 14, 21, 25, 58))

        scanner.scan()
        scanner.client.get.assert_called_with('/search', {
            'title': 'Uncharted',
            'type': 'movie',
        })

        # Scan again to make sure cached items doesn't fail
        scanner.scan()
        scanner.client.get.assert_called_once()

        with new_session() as session:
            r = session.query(models.Movie_id_lookup).first()
            self.assertEqual(r.file_title, 'Uncharted')
            
            r = session.query(models.Movie).first()
            self.assertEqual(r.path, 'Uncharted.mkv')
            self.assertEqual(r.meta_data, { 'some': 'data' })

        scanner.delete_item('Uncharted', 'Uncharted.mkv')
        with new_session() as session:
            r = session.query(models.Movie).first()
            self.assertEqual(r, None)

    def test_parse(self):
        scanner = Movie_scan('/')
        self.assertEqual(
            scanner.parse('Uncharted (2160p BluRay x265 10bit HDR Tigole).mkv'),
            'Uncharted',
        )
        self.assertEqual(
            scanner.parse('Parasite.2019.REPACK.2160p.4K.BluRay.x265.10bit.AAC7.1-[YTS.MX].mkv'),
            'Parasite 2019',
        )

class Test_series_scan(Testbase):

    def setUp(self):
        super().setUp()
        self.scanner = Series_scan('/')

    def test_series_id_lookup(self):
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'id': 1,
                'title': 'Test series',
            }
        ])
        # test that a series we haven't searched for is not in the db
        self.assertEqual(
            None,
            self.scanner.series_id.db_lookup('test series'),
        )
        # search for the series
        self.assertEqual(
            1,
            self.scanner.series_id.lookup('test series')
        )
        # the result should now be stored in the database
        self.assertEqual(
            1,
            self.scanner.series_id.db_lookup('test series'),
        )


    def test_episode_number_lookup(self):
        # test parsed episode season
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'number': 2,
            }
        ])
        episode = Parsed_episode_season(
            series_id=1,
            file_title='NCIS',
            season=1,
            episode=2,
        )
        self.assertEqual(
            None,
            self.scanner.episode_number.db_lookup(episode)
        )
        self.assertEqual(
            2,
            self.scanner.episode_number.lookup(episode)
        )
        self.scanner.client.get.assert_called_with('/series/1/episodes', {
            'q': 'season:1 AND episode:2',
            'fields': 'number',
        })
        self.assertEqual(
            2,
            self.scanner.episode_number.db_lookup(episode)
        )

        # test parsed episode air_date
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'number': 3,
            }
        ])
        episode = Parsed_episode_air_date(
            series_id=1,
            file_title='NCIS',
            air_date='2014-11-14',
        )
        self.assertEqual(
            None,
            self.scanner.episode_number.db_lookup(episode)
        )
        self.assertEqual(
            3,
            self.scanner.episode_number.lookup(episode)
        )
        self.scanner.client.get.assert_called_with('/series/1/episodes', {
            'q': 'air_date:2014-11-14',
            'fields': 'number',
        })
        self.assertEqual(
            3,
            self.scanner.episode_number.db_lookup(episode)
        )

        # test parsed episode number
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'number': 4,
            }
        ])
        episode = Parsed_episode_number(
            series_id=1,
            file_title='NCIS',
            number=4,
        )
        self.assertTrue(self.scanner.episode_number_lookup(episode))
        # there is no reason to have a lookup record for an
        # episode that already contains the episode number.
        self.assertRaises(
            Exception,
            self.scanner.episode_number.db_lookup,
            episode,
        )
        self.assertEqual(
            4,
            self.scanner.episode_number.lookup(episode)
        )

    def test_save_item(self):
        self.scanner.get_file_modified_time = mock.MagicMock()
        self.scanner.get_file_modified_time.return_value = datetime(2014, 11, 14, 21, 25, 58)
        self.scanner.get_metadata = mock.MagicMock()
        self.scanner.get_metadata.return_value = {
            'data': 'test',
        }
        episodes = []
        episodes.append((Parsed_episode_season(
            series_id=1,
            file_title='ncis',
            season=1,
            episode=2,
            number=2,
        ), '/ncis/ncis.s01e02.mp4'))
        episodes.append((Parsed_episode_air_date(
            series_id=1,
            file_title='ncis',
            air_date='2014-11-14',
            number=3,
        ), '/ncis/ncis.2014-11-14.mp4'))
        episodes.append((Parsed_episode_number(
            series_id=1,
            file_title='ncis',
            number=4,
        ), '/ncis/ncis.4.mp4'))
        # episodes saved
        for episode in episodes:
            self.scanner.save_item(episode[0], episode[1])

        # check that metadata was called for all the episodes.
        # if metadata i getting called the episode will be 
        # inserted/updated in the db.
        self.scanner.get_metadata.assert_has_calls([
            mock.call('/ncis/ncis.s01e02.mp4'),
            mock.call('/ncis/ncis.2014-11-14.mp4'),
            mock.call('/ncis/ncis.4.mp4'),
        ])

        # check that calling `save_items` again does not result
        # in a update since the `modified_time` has not changed for
        # any of them.      
        self.scanner.get_metadata.reset_mock()
        for episode in episodes:
            self.scanner.save_item(episode[0], episode[1])
        self.scanner.get_metadata.assert_has_calls([])

        # check that changing the `modified_time` will result in the
        # episode getting updated in the db.        
        self.scanner.get_metadata.reset_mock()
        self.scanner.get_file_modified_time.return_value = datetime(2014, 11, 15, 21, 25, 58)
        self.scanner.save_item(episodes[1][0], episodes[1][1])
        self.scanner.get_metadata.assert_has_calls(
            [mock.call('/ncis/ncis.2014-11-14.mp4')],
        )

        with new_session() as session:
            r = session.query(models.Episode).all()
            self.assertEqual(len(r), 3)

        self.scanner.delete_item(episodes[0][0], episodes[0][1])

        with new_session() as session:
            r = session.query(models.Episode).all()
            self.assertEqual(len(r), 2)
        
    def test_scan(self):
        episodes = [Parsed_episode_number(
            series_id=1,
            file_title='ncis',
            number=4,
        )]
        self.scanner.get_files = mock.MagicMock(return_value=[
            '/ncis/ncis.s01e02.mp4'
        ])
        self.scanner.save_item = mock.MagicMock()
        self.scanner.episode_series_id_lookup = mock.MagicMock()
        self.scanner.episode_number_lookup = mock.MagicMock()

        self.scanner.scan()
        self.scanner.save_item.assert_called()

    def test_parse_episode(self):
        # Normal
        path = '/Alpha House/Alpha.House.S02E01.The.Love.Doctor.720p.AI.WEBRip.DD5.1.x264-NTb.mkv'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_season),
        )
        self.assertEqual(info.file_title, 'alpha.house')
        self.assertEqual(info.season, 2)
        self.assertEqual(info.episode, 1)

        # Anime
        path = '/Naruto/[HorribleSubs] Naruto Shippuuden - 379 [1080p].mkv'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
        )
        self.assertEqual(info.file_title, 'naruto shippuuden')
        self.assertEqual(info.number, 379)

        path = '/Naruto Shippuuden/Naruto Shippuuden.426.720p.mkv'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
        )
        self.assertEqual(info.file_title, 'naruto shippuuden')
        self.assertEqual(info.number, 426)

        # Air date
        path = '/The Daily series/The.Daily.series.2014.06.03.Ricky.Gervais.HDTV.x264-D0NK.mp4'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_air_date),
        )
        self.assertEqual(info.file_title, 'the.daily.series')
        self.assertEqual(info.air_date, '2014-06-03')

        # Double episode
        path = 'Star Wars Resistance.S01E01-E02.720p webdl h264 aac.mkv'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_season),
        )
        self.assertEqual(info.file_title, 'star wars resistance')
        self.assertEqual(info.season, 1)
        self.assertEqual(info.episode, 1)
        
        path = 'Boruto Naruto Next Generations (2017).6.1080p h265.mkv'
        info = self.scanner.parse(path)
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
            type(info)
        )
        self.assertEqual(info.file_title, 'boruto naruto next generations (2017)')
        self.assertEqual(info.number, 6)
    
if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
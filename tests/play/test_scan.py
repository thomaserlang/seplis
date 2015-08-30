import unittest
import nose
import mock
import logging
from datetime import datetime
from seplis.play.connections import database
from seplis.play.decorators import new_session
from seplis.logger import logger
from seplis import config_load, config
from seplis.play.scan import Play_scan, Shows_scan, parse_episode, \
    Parsed_episode_season, Parsed_episode_air_date, Parsed_episode_number
from seplis.play import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Testbase(unittest.TestCase):

    def setUp(self):
        database.engine = create_engine(
            'sqlite://',# memory db
            convert_unicode=True, 
            echo=False, 
        )
        connection = database.engine.connect()
        database.session = sessionmaker(bind=connection)
        models.base.metadata.create_all(database.engine)

class test_scan(Testbase):

    def setUp(self):
        super().setUp()
        self.scanner = Play_scan(
            '/', 
            type_='shows',
        )
    
    def test_get_files(self):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = [                
                ('/shows', ('NCIS', 'Person of Interest'), ()),
                ('/shows/NCIS', ('Season 01', 'Season 02'), ()),
                ('/shows/NCIS/Season 01', (), (
                    'NCIS.S01E01.Yankee White.avi',
                    'NCIS.S01E02.Hung Out to Dry.avi',
                )),
                ('/shows/NCIS/Season 02', (), (
                    'NCIS.S02E01.See No Evil.avi',
                    'NCIS.S02E02.The Good Wives Club.avi',  
                )),
                ('/shows/Person of Interest', ('Season 01'), ()),
                ('/shows/Person of Interest/Season 01', (), (
                    'Person of Interest.S01E01.Pilot.mp4',
                    '._Person of Interest.S01E01.Pilot.mp4',
                )),
            ]

            files = self.scanner.get_files()
            self.assertEqual(files, [
                '/shows/NCIS/Season 01/NCIS.S01E01.Yankee White.avi',
                '/shows/NCIS/Season 01/NCIS.S01E02.Hung Out to Dry.avi',
                '/shows/NCIS/Season 02/NCIS.S02E01.See No Evil.avi',
                '/shows/NCIS/Season 02/NCIS.S02E02.The Good Wives Club.avi',
                '/shows/Person of Interest/Season 01/Person of Interest.S01E01.Pilot.mp4',
            ])

    @mock.patch('subprocess.Popen')
    @mock.patch('os.path.exists')
    def test_get_metadata(self, mock_path_exists, mock_popen):
        mock_path_exists.return_value = True
        mock_popen().stdout.read.return_value= '{"metadata": "test"}'
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

class test_shows_scan(Testbase):

    def setUp(self):
        super().setUp()
        self.scanner = Shows_scan(
            '/',
        )

    def test_show_id_lookup(self):
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'id': 1,
                'title': 'Test show',
            }
        ])
        # test that a show we haven't searched for is not in the db
        self.assertEqual(
            None,
            self.scanner.show_id.db_lookup('test show'),
        )
        # search for the show
        self.assertEqual(
            1,
            self.scanner.show_id.lookup('test show')
        )
        # the result should now be stored in the database
        self.assertEqual(
            1,
            self.scanner.show_id.db_lookup('test show'),
        )


    def test_episode_number_lookup(self):
        # test parsed episode season
        self.scanner.client.get = mock.MagicMock(return_value=[
            {
                'number': 2,
            }
        ])
        episode = Parsed_episode_season(
            show_id=1,
            file_show_title='NCIS',
            season=1,
            episode=2,
            path='/',
        )
        self.assertEqual(
            None,
            self.scanner.episode_number.db_lookup(episode)
        )
        self.assertEqual(
            2,
            self.scanner.episode_number.lookup(episode)
        )
        self.scanner.client.get.assert_called_with('/shows/1/episodes', {
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
            show_id=1,
            file_show_title='NCIS',
            air_date='2014-11-14',
            path='/',
        )
        self.assertEqual(
            None,
            self.scanner.episode_number.db_lookup(episode)
        )
        self.assertEqual(
            3,
            self.scanner.episode_number.lookup(episode)
        )
        self.scanner.client.get.assert_called_with('/shows/1/episodes', {
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
            show_id=1,
            file_show_title='NCIS',
            number=4,
            path='/',
        )
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

    def test_save_episode(self):
        self.scanner.get_file_modified_time = mock.MagicMock()
        self.scanner.get_file_modified_time.return_value = datetime(2014, 11, 14, 21, 25, 58)
        self.scanner.get_metadata = mock.MagicMock()
        self.scanner.get_metadata.return_value = {
            'data': 'test',
        }
        episodes = []
        episodes.append(Parsed_episode_season(
            show_id=1,
            file_show_title='ncis',
            season=1,
            episode=2,
            path='/ncis/ncis.s01e02.mp4',
            number=2,
        ))
        episodes.append(Parsed_episode_air_date(
            show_id=1,
            file_show_title='ncis',
            air_date='2014-11-14',
            path='/ncis/ncis.2014-11-14.mp4',
            number=3,
        ))
        episodes.append(Parsed_episode_number(
            show_id=1,
            file_show_title='ncis',
            number=4,
            path='/ncis/ncis.4.mp4',
        ))
        # episodes saved
        for episode in episodes:
            self.scanner.save_episode(episode)

        # check that metadata was called for all the episodes.
        # if metadata i getting called the episode will be 
        # inserted/updated in the db.
        self.scanner.get_metadata.assert_has_calls([
            mock.call('/ncis/ncis.s01e02.mp4'),
            mock.call('/ncis/ncis.2014-11-14.mp4'),
            mock.call('/ncis/ncis.4.mp4'),
        ])

        # check that calling `save_episodes` again does not result
        # in a update since the `modified_time` has not changed for
        # any of them.      
        self.scanner.get_metadata.reset_mock()
        for episode in episodes:
            self.scanner.save_episode(episode)
        self.scanner.get_metadata.assert_has_calls([])

        # check that changing the `modified_time` will result in the
        # episode getting updated in the db.        
        self.scanner.get_metadata.reset_mock()
        self.scanner.get_file_modified_time.return_value = datetime(2014, 11, 15, 21, 25, 58)
        self.scanner.save_episode(episodes[1])
        self.scanner.get_metadata.assert_has_calls(
            mock.call('/ncis/ncis.2014-11-14.mp4'),
        )

    def test_scan(self):
        episodes = [Parsed_episode_number(
            show_id=1,
            file_show_title='ncis',
            number=4,
            path='/ncis/ncis.4.mp4',
        )]
        self.scanner.get_episodes = mock.MagicMock()
        self.scanner.get_episodes.return_value = episodes
        self.scanner.save_episode = mock.MagicMock()
        self.scanner.episode_show_id_lookup = mock.MagicMock()
        self.scanner.episode_number_lookup = mock.MagicMock()

        self.scanner.scan()

        self.scanner.episode_show_id_lookup.assert_called_with(episodes[0])
        self.scanner.episode_number_lookup.assert_called_with(episodes[0])
        self.scanner.save_episode.assert_called_with(episodes[0])

    def test_get_episodes(self):
        self.scanner.get_files = mock.MagicMock()
        self.scanner.get_files.return_value = [
            '/Naruto/[HorribleSubs] Naruto Shippuuden - 379 [1080p].mkv'
        ]
        episodes = self.scanner.get_episodes()
        self.assertEqual(len(episodes), 1)
        self.assertTrue(isinstance(episodes[0], Parsed_episode_number))

class test_parse_episode(unittest.TestCase):

    def test(self):
        # Normal
        path = '/Alpha House/Alpha.House.S02E01.The.Love.Doctor.720p.AI.WEBRip.DD5.1.x264-NTb.mkv'
        info = parse_episode(
            path
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_season),
        )
        self.assertEqual(info.file_show_title, 'alpha.house')
        self.assertEqual(info.season, 2)
        self.assertEqual(info.episode, 1)
        self.assertEqual(info.path, path)

        # Anime
        path = '/Naruto/[HorribleSubs] Naruto Shippuuden - 379 [1080p].mkv'
        info = parse_episode(
            path
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
        )
        self.assertEqual(info.file_show_title, 'naruto shippuuden')
        self.assertEqual(info.number, 379)
        self.assertEqual(info.path, path)

        path = '/Naruto Shippuuden/Naruto Shippuuden.426.720p.mkv'
        info = parse_episode(
            path
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
        )
        self.assertEqual(info.file_show_title, 'naruto shippuuden')
        self.assertEqual(info.number, 426)
        self.assertEqual(info.path, path)


        # Air date
        path = '/The Daily Show/The.Daily.Show.2014.06.03.Ricky.Gervais.HDTV.x264-D0NK.mp4'
        info = parse_episode(
            path
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_air_date),
        )
        self.assertEqual(info.file_show_title, 'the.daily.show')
        self.assertEqual(info.air_date, '2014-06-03')
        self.assertEqual(info.path, path)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
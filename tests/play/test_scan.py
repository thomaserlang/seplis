import unittest
import nose
import mock
import logging
from seplis.play.connections import database
from seplis.play.decorators import new_session
from seplis.logger import logger
from seplis import config_load, config
from seplis.play.scan import Play_scan, Shows_scan, parse_episode, \
    Parsed_episode_season, Parsed_episode_air_date, \
    Parsed_episode_number
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
            show_title='NCIS',
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
            show_title='NCIS',
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
            show_title='NCIS',
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

class test_parse_episode(unittest.TestCase):

    def test(self):
        # Normal
        info = parse_episode(
            'Alpha.House.S02E01.The.Love.Doctor.720p.AI.WEBRip.DD5.1.x264-NTb.mkv'
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_season),
        )
        self.assertEqual(info.show_title, 'Alpha House')
        self.assertEqual(info.season, 2)
        self.assertEqual(info.episode, 1)

        # Anime
        info = parse_episode(
            '[HorribleSubs] Naruto Shippuuden - 379 [1080p].mkv'
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_number),
        )
        self.assertEqual(info.show_title, 'Naruto Shippuuden')
        self.assertEqual(info.number, 379)

        # Air date
        info = parse_episode(
            'The.Daily.Show.2014.06.03.Ricky.Gervais.HDTV.x264-D0NK.mp4'
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_air_date),
        )
        self.assertEqual(info.show_title, 'The Daily Show')
        self.assertEqual(info.air_date, '2014-06-03')

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
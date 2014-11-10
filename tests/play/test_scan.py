import unittest
import nose
import mock
import logging
from seplis.logger import logger
from seplis import config_load, config
from seplis.play.scan import Play_scan, parse_episode, \
    Parsed_episode_season, Parsed_episode_airdate, \
    Parsed_episode_number
from seplis.play import models

class test_scan(unittest.TestCase):

    def setUp(self):        
        config_load()
        config['logging']['path'] = None
        config['play']['database'] = 'sqlite://'# memory db
        from seplis.play.connections import database
        from seplis.play.decorators import new_session
        models.base.metadata.create_all(database.engine)
        self.scanner = Play_scan(
            '/', 
            type_='shows',
        )
    
    def test_get_files(self):
        print('b')
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

    def test_show_id_lookup(self):
        self.scanner.shows_web_lookup = mock.MagicMock(return_value=[
            {
                'id': 1,
                'title': 'Test show',
            }
        ])

        # test that a show we have not yet searched is not in the db
        self.assertEqual(
            None,
            self.scanner.show_id_db_lookup('test show'),
        )

        # search for the show
        self.assertEqual(
            1,
            self.scanner.show_id_lookup('test show')
        )

        # the result should now be stored in the database
        self.assertEqual(
            1,
            self.scanner.show_id_db_lookup('test show'),
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

        # Airdate
        info = parse_episode(
            'The.Daily.Show.2014.06.03.Ricky.Gervais.HDTV.x264-D0NK.mp4'
        )
        self.assertTrue(
            isinstance(info, Parsed_episode_airdate),
        )
        self.assertEqual(info.show_title, 'The Daily Show')
        self.assertEqual(info.airdate, '2014-06-03')

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
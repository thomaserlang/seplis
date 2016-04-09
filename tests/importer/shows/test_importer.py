# coding=UTF-8
import nose
import mock
from unittest import TestCase
from datetime import date
from seplis.importer.shows.importer import *

class Test_update_show_info(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    @mock.patch('seplis.importer.shows.importer.call_importer')
    def test(self, call_importer, client):
        show = {
            'id': 1,
            'importers': {
                'info': 'test_importer'
            }
        }
        call_importer.return_value = {'title': 'Test show'}
        update_show_info(show)
        call_importer.assert_called_with(
            id_=show['importers']['info'],
            method='info',
            show_id=show['id'],
        )
        client.patch.assert_called_with(
            '/shows/{}'.format(show['id']),
            {'title': 'Test show'},
            timeout=120,
        )
        
class Test_update_show_episodes(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    @mock.patch('seplis.importer.shows.importer.call_importer')
    def test(self, call_importer, client):
        show = {
            'id': 1,
            'importers': {
                'episodes': 'test_importer'
            }
        }
        client.get.all.return_value = []
        call_importer.return_value = [{'number': 1}]
        update_show_episodes(show)
        call_importer.assert_called_with(
            id_=show['importers']['episodes'],
            method='episodes',
            show_id=show['id'],
        )
        client.patch.assert_called_with(
            '/shows/{}'.format(show['id']),
            {'episodes': [{'number': 1}]},
            timeout=120,
        )

class Test_cleanup_episodes(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    def test(self, client):
        episodes = [{'number': 1}, {'number': 2}, {'number': 3}]
        imp_episodes = [{'number': 1}]
        cleanup_episodes(
            show_id=1, 
            episodes=episodes, 
            imported_episodes=imp_episodes
        )
        self.assertEqual(
            client.delete.mock_calls,
            [
                mock.call('/shows/1/episodes/2'),
                mock.call('/shows/1/episodes/3'),
            ]
        )

class Test_show_info_changes(TestCase):

    def test(self):        
        show = {
            'title': 'NCIS',
            'description': {
                'text': 'this is a description',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'status': 1,            
            'genres': [
                'test1',
                'test2',
            ],
        }
        show_changed = {   
            'title': 'NCIS 2',
            'description': {
                'text': 'this is a description 2',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'status': 1,
            'premiered': date(2014, 9, 3),
            'genres': [
                'test1',
                'test2',
                'test3',
            ],
        }

        changes = show_info_changes(show, show_changed)
        self.assertEqual(changes, {
            'title': 'NCIS 2',
            'description': {
                'text': 'this is a description 2',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'premiered': date(2014, 9, 3),            
            'genres': [
                'test3',
            ],
        })

    def test_genres(self):
        show = {
            'genres': [
                'test1',
                'test2',
            ]
        }
        show_changed = {
            'genres': [
                'test2',
                'test1',
            ]
        }
        changes = show_info_changes(show, show_changed)
        self.assertFalse(changes, changes)

class Test_show_episode_changes(TestCase):

    def test_episodes_changed(self):
        episode = {
            'number': 1,
            'title': 'Episode 1',
            'description': {
                'text': 'this is a description',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'air_date': date(2014, 9, 3),
            'season': 1,
            'genres': [
                'test1',
                'test2',
            ]
        }
        episodes_changed = [
            {   
                'number': 1,
                'title': 'Episode 1 (new title)',
                'description': {
                    'text': 'this is a description 2',
                    'url': 'http://example.org',
                    'title': 'Example',
                },
                'air_date': date(2014, 9, 4),
                'episode': 1,
            },
            {   
                'number': 2,
                'title': 'Episode 2',
                'description': {
                    'text': 'this is a description',
                    'url': 'http://example.org',
                    'title': 'Example',
                },
                'air_date': date(2014, 9, 5),
                'episode': 2,
                'season': 1,
            }
        ]

        changes = show_episode_changes([episode], episodes_changed)
        self.assertEqual(changes[0], {   
            'number': 1,
            'title': 'Episode 1 (new title)',
            'description': {
                'text': 'this is a description 2',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'air_date': date(2014, 9, 4),
            'episode': 1,
        })
        self.assertEqual(changes[1], episodes_changed[1])

        # test no changes
        changes = show_episode_changes([episode], [episode])
        self.assertEqual(len(changes), 0)

        # test None description
        episode = {
            'number': 1,
            'title': 'Episode 1',
            'description': {
                'text': 'this is a description',
                'url': 'http://example.org',
                'title': 'Example',
            },
            'air_date': date(2014, 9, 3),
            'season': 1,
        }
        episodes_changed = [
            {   
                'number': 1,
                'title': 'Episode 1 (new title)',
                'description': None,
                'air_date': date(2014, 9, 4),
                'episode': 1,
            },
        ]        
        changes = show_episode_changes([episode], episodes_changed)
        self.assertEqual(changes[0], {   
            'number': 1,
            'title': 'Episode 1 (new title)',
            'air_date': date(2014, 9, 4),
            'episode': 1,
        })

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
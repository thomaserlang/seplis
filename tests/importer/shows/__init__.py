# coding=UTF-8
import nose
import mock
from unittest import TestCase
from seplis import utils, importer
from datetime import date

class test_show_info_changes(TestCase):

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

        changes = importer.shows.show_info_changes(show, show_changed)
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
        changes = importer.shows.show_info_changes(show, show_changed)
        self.assertFalse(changes, changes)

class test_episode_changes(TestCase):
    def test(self):
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

        changes = importer.shows.show_episode_changes([episode], episodes_changed)
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
        changes = importer.shows.show_episode_changes([episode], [episode])
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
        changes = importer.shows.show_episode_changes([episode], episodes_changed)
        self.assertEqual(changes[0], {   
            'number': 1,
            'title': 'Episode 1 (new title)',
            'air_date': date(2014, 9, 4),
            'episode': 1,
        })

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
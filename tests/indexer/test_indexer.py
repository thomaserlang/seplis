# coding=UTF-8
import nose
import mock
import json
import show.test_tvrage
from tornado import gen
from datetime import date
from unittest import TestCase
from seplis.indexer.indexer import show_info_changes, show_episode_changes
from seplis.indexer import Show_indexer

@gen.coroutine
def mock_show_patch(self, request, callback=None, **kwargs):
    if request.method == 'PATCH':
        return mock.Mock(
            headers={},
            body=json.dumps(
                {}
            ),
            code=200,
        )
    elif request.method == 'GET':
        if 'episodes' in request.url:
            return mock.Mock(
                headers={},
                body=json.dumps([
                    {
                        'number': 1
                    }
                ]),
                code=200,
            )
        elif 'shows/' in request.url:
            if '4628' in request.url:
                return mock.Mock(
                    headers={},
                    body=json.dumps({
                        'id': '4628',
                        'title': 'NCIS: Has been updated',
                        'indices': {
                            'info': 'tvrage',
                            'episodes': 'tvrage',
                        },
                        'externals': {
                            'tvrage': '4628'
                        },
                    }),
                    code=200,
                )
            elif '2445' in request.url:
                return mock.Mock(
                    headers={},
                    body=json.dumps({
                        'id': '2445',
                        'title': '24: Has been updated',                
                        'indices': {
                            'info': 'tvrage',
                            'episodes': 'tvrage',
                        },
                        'externals': {
                            'tvrage': '2445'
                        },
                    }),
                    code=200,
                )
        elif '/externals/tvrage' in request.url:
            if '4628' in request.url:
                return mock.Mock(
                    headers={},
                    body=json.dumps({
                        'id': '4628',
                        'title': 'NCIS: Should be updated',
                        'indices': {
                            'info': 'tvrage',
                            'episodes': 'tvrage',
                        },
                        'externals': {
                            'tvrage': '4628'
                        },
                    }),
                    code=200,
                )        
            elif '2445' in request.url:
                return mock.Mock(
                    headers={},
                    body=json.dumps({
                        'id': '2445',
                        'title': '24: Should be updated',                
                        'indices': {
                            'info': 'tvrage',
                            'episodes': 'tvrage',
                        },
                        'externals': {
                            'tvrage': '2445'
                        },
                    }),
                    code=200,
                )

class test_indexer(TestCase):

    @mock.patch('requests.get', show.test_tvrage.mock_tvrage)
    def test_update(self):
        with mock.patch('tornado.httpclient.AsyncHTTPClient.fetch', mock_show_patch) as m:
            indexer = Show_indexer('http://example.org')
            updated_shows = indexer.update()

            self.assertTrue('2445' in updated_shows)
            self.assertEqual(len(updated_shows['2445']['episodes']), 4)
            self.assertTrue('4628' in updated_shows)
            self.assertEqual(len(updated_shows['4628']['episodes']), 4)

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
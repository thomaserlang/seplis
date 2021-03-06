# coding=UTF-8
import responses
import nose
import mock
import requests.exceptions
from unittest import TestCase
from datetime import date
from seplis.importer.shows.importer import client, importers, update_show, \
    update_show_info, update_show_images, update_show_episodes, \
    _save_image, _upload_image, _show_info_changes, _show_episode_changes, \
    _importers_with_support, _cleanup_episodes, _importer_incremental, \
    update_shows_incremental, Importer_exception, Importer_upload_image_exception
from seplis.importer.shows.base import Show_importer_base

class Test_update_shows_incremental(TestCase):

    @mock.patch.dict('seplis.importer.shows.base.importers', {}, clear=True)
    @mock.patch('seplis.importer.shows.importer._importer_incremental')
    def test(self, _importer_incremental):
        importers['test'] = mock.Mock()

        update_shows_incremental()

        _importer_incremental.assert_called_with(importers['test'])

class Test__importer_incremental(TestCase):

    @mock.patch('seplis.importer.shows.importer.update_show_images')
    @mock.patch('seplis.importer.shows.importer.update_show')
    @mock.patch('seplis.importer.shows.importer.client')
    def test(self, client, update_show, update_show_images):
        test_importer = mock.Mock()
        test_importer.external_name = 'test'
        test_importer.incremental_updates.return_value = ['1']
        show = {
            'id': 1,
            'importers': {
                'info': 'test',
            },
            'externals': {},
        }
        client.get.return_value = show

        _importer_incremental(test_importer)        
        client.get.assert_called_with('/shows/externals/test/1')
        update_show.assert_called_with(show)
        self.assertTrue(test_importer.save_timestamp.called)
        update_show.reset_mock()

        # The importer `test` is not part of the shows importers
        # therefore update_show must not be called.
        # But the image importer should be called.
        show['importers'] = {
            'info': 'test2',
        }
        _importer_incremental(test_importer)        
        client.get.assert_called_with('/shows/externals/test/1')
        self.assertFalse(update_show.called)
        self.assertTrue(test_importer.save_timestamp.called)
        update_show_images.assert_called_with(show)

class Test_update_show(TestCase):

    @mock.patch('seplis.importer.shows.importer.update_show_images')
    @mock.patch('seplis.importer.shows.importer.update_show_episodes')
    @mock.patch('seplis.importer.shows.importer.update_show_info')
    def test(self, update_show_info, update_show_episodes, update_show_images):
        show = {
            'externals': {
                'test': 'abc',
            },
            'importers': {
                'info': 'test',
                'episodes': 'test',
            },
        }
        update_show_info.return_value = show
        update_show(show)
        update_show_info.assert_called_with(show)
        update_show_episodes.assert_called_with(show)
        update_show_images.assert_called_with(show)

class Test_update_show_info(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    @mock.patch('seplis.importer.shows.importer.call_importer')
    def test(self, call_importer, client):
        show = {
            'id': 1,
            'importers': {
                'info': 'test_importer'
            },
            'externals': {
                'test_importer': 'abc',
            }
        }
        call_importer.return_value = {'title': 'Test show'}
        client.patch.return_value = {'title': 'Test show'}
        info = update_show_info(show)
        self.assertEqual(info, {'title': 'Test show'})
        call_importer.assert_called_with(
            external_name=show['importers']['info'],
            method='info',
            show_id='abc',
        )
        client.patch.assert_called_with(
            '/shows/{}'.format(show['id']),
            {'title': 'Test show'},
            timeout=120,
        )

        # Check that show returns if the import does not exist
        call_importer.return_value = None
        info = update_show_info(show)
        self.assertEqual(info, show)

class Test_update_show_episodes(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    @mock.patch('seplis.importer.shows.importer.call_importer')
    def test(self, call_importer, client):
        show = {
            'id': 1,
            'importers': {
                'episodes': 'test_importer'
            },
            'externals': {
                'test_importer': 'abc',
            }
        }
        client.get().all.return_value = []
        call_importer.return_value = [{'number': 1}]
        update_show_episodes(show)
        call_importer.assert_called_with(
            external_name=show['importers']['episodes'],
            method='episodes',
            show_id='abc',
        )
        client.patch.assert_called_with(
            '/shows/{}'.format(show['id']),
            {'episodes': [{'number': 1}]},
            timeout=120,
        )

    @mock.patch('seplis.importer.shows.importer.client')
    @mock.patch('seplis.importer.shows.importer.call_importer')
    def test_call_importer_return_none(self, call_importer, client):
        show = {
            'id': 1,
            'importers': {
                'episodes': 'test_importer'
            },
            'externals': {
                'test_importer': 'abc',
            }
        }
        client.get().all.return_value = []
        call_importer.return_value = None    
        update_show_episodes(show)

class Test__cleanup_episodes(TestCase):

    @mock.patch('seplis.importer.shows.importer.client')
    def test(self, client):
        episodes = [{'number': 1}, {'number': 2}, {'number': 3}]
        imp_episodes = [{'number': 1}]
        _cleanup_episodes(
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


class Test_update_show_images(TestCase):

    @mock.patch.dict('seplis.importer.shows.base.importers', {}, clear=True)
    @mock.patch('seplis.importer.shows.importer._save_image')
    @mock.patch('seplis.importer.shows.importer._upload_image')
    @mock.patch('seplis.importer.shows.importer.client')
    def test(self, client, _upload_image, _save_image):
        show = {
            'id': 1,
            'externals': {
                'test': 1,
            },
        }
        imported_images = [
            {
                'id': None,
                'external_name': 'test',
                'external_id': 1,
                'hash': None,
            },
            {
                'id': None,
                'external_name': 'test',
                'external_id': 2,
                'hash': None,
            },
            {
                'id': None,
                'external_name': 'test',
                'external_id': 3,
                'hash': None,
            },
        ]
        importers['test'] = mock.Mock()
        importers['test'].external_name = 'test'
        importers['test'].supported = ('images')
        importers['test'].images.return_value = imported_images

        existing_images = [
            {
                'id': 1,
                'external_name': 'test',
                'external_id': 1,
                'hash': None,
            },            
            {
                'id': 2,
                'external_name': 'test',
                'external_id': 2,
                'hash': 'some hash',
            },
        ]
        client.get().all.return_value = existing_images

        update_show_images(show)
        _save_image.assert_called_with(show['id'], imported_images[2])
        _upload_image.assert_called_with(show['id'], existing_images[0])

class Test__save_image(TestCase):

    @mock.patch('seplis.importer.shows.importer._upload_image')
    @mock.patch('seplis.importer.shows.importer.client')
    def test(self, client, _upload_image):
        client.post.return_value = {'id': 1}
        _save_image(1, {'id': None})
        _upload_image.assert_called_with(1, {'id': 1})

class Test__upload_image(TestCase):

    @responses.activate
    def test(self):
        image = {
            'id': 1,
            'source_url': 'http://example.net/test.jpg',
        }

        # Test retrive image error        
        responses.add(responses.GET, 'http://example.net/test.jpg',
            body='AN IMAGE',
            status=404,
            stream=True,
        )
        with mock.patch('seplis.importer.shows.importer.client') as c:
            with self.assertRaises(Importer_exception):
                _upload_image(1, image)
            self.assertTrue(c.delete.called)

        # Test upload fail
        responses.reset()
        responses.add(responses.GET, 'http://example.net/test.jpg',
            body='AN IMAGE',
            status=200,
            stream=True,
        )
        upload_url = client.url+'/shows/1/images/1/data'
        delete_url = client.url + '/shows/1/images/1'
        responses.add(responses.PUT, upload_url, status=500, body='{"code": 1}')
        with mock.patch('seplis.importer.shows.importer.client') as c:
            c.url = client.url
            with self.assertRaises(Importer_upload_image_exception):
                _upload_image(1, image)
            self.assertTrue(c.delete.called)

        # Test successfully
        upload_url = client.url+'/shows/2/images/1/data'
        responses.add(responses.PUT, upload_url, status=200)
        self.assertTrue(_upload_image(2, image))

class Test__importers_with_support(TestCase):

    def test(self):
        imps = {}
        i1 = Show_importer_base()
        i1.external_name = 'test_importer_1'
        i1.supported = ('info', 'images')
        imps[i1.external_name] = i1
        i2 = Show_importer_base()
        i2.external_name = 'test_importer_2'
        i2.supported = ('info')
        imps[i2.external_name] = i2
        with mock.patch.dict(
            'seplis.importer.shows.base.importers',
            imps,
            clear=True,
        ):
            self.assertEqual(
                _importers_with_support({'test_importer_1': 1}, 'images'),
                ['test_importer_1'],
            )
            self.assertEqual(
                _importers_with_support({'test_importer_2': 1}, 'images'),
                [],
            )
            self.assertEqual(
                _importers_with_support(
                    {'test_importer_1': 1, 'test_importer_2': 1}, 
                    'images'
                ),
                ['test_importer_1'],
            )
            self.assertCountEqual(
                _importers_with_support(
                    {'test_importer_1': 1, 'test_importer_2': 1}, 
                    'info'
                ),
                ['test_importer_1', 'test_importer_2'],
            )

class Test__show_info_changes(TestCase):

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

        changes = _show_info_changes(show, show_changed)
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
        changes = _show_info_changes(show, show_changed)
        self.assertFalse(changes, changes)

class Test__show_episode_changes(TestCase):

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

        changes = _show_episode_changes([episode], episodes_changed)
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
        changes = _show_episode_changes([episode], [episode])
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
        changes = _show_episode_changes([episode], episodes_changed)
        self.assertEqual(changes[0], {   
            'number': 1,
            'title': 'Episode 1 (new title)',
            'air_date': date(2014, 9, 4),
            'episode': 1,
        })

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
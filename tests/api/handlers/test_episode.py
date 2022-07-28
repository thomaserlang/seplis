# coding=UTF-8
import json
from seplis.api.testbase import Testbase
from datetime import datetime, date, timedelta
from seplis.utils import json_dumps, json_loads
from seplis import utils
from seplis.api.decorators import new_session
from seplis.api.connections import database
from seplis.config import config
from seplis.api import constants

class Test_episode(Testbase):

    def test_search(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'air_time': '22:00',
                    'air_datetime': '2014-01-01T22:00:00+01:00',
                    'description': {
                        'text': 'Test description.'
                    },
                    'runtime': 30,
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)

        response = self.get('/1/shows/{}/episodes/{}'.format(
            show_id,
            1
        ))
        self.assertEqual(response.code, 200, response.body)
        episode = utils.json_loads(response.body)
        self.assertEqual(episode['number'], 1)
        self.assertEqual(episode['title'], 'Episode 1')
        self.assertEqual(episode['description'], {
            'text': 'Test description.',
            'url': None,
            'title': None,            
        })
        self.assertEqual(episode['runtime'], 30)
        self.assertEqual(episode['air_date'], '2014-01-01')
        self.assertEqual(episode['air_time'], '22:00:00')
        self.assertEqual(episode['air_datetime'], '2014-01-01T21:00:00Z')

        # test that we can patch the description        
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'description': {
                        'title': 'Test',
                    }
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/shows/{}/episodes/{}'.format(
            show_id,
            1
        ))
        self.assertEqual(response.code, 200, response.body)
        episode = utils.json_loads(response.body)  
        self.assertEqual(episode['number'], 1)
        self.assertEqual(episode['title'], 'Episode 1')
        self.assertEqual(episode['description'], {
            'text': 'Test description.',
            'url': None,
            'title': 'Test',            
        })


        # test search
        self.refresh_es()
        response = self.get('/1/shows/{}/episodes'.format(show_id), {
            'q': 'air_date:2014-01-01',
        })
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0], episode)

    def test_empty_episode_get(self):
        show_id = self.new_show()
        response = self.get('/1/shows/{}/episodes'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        
        response = self.get('/1/shows/{}/episodes/1'.format(show_id))
        self.assertEqual(response.code, 404, response.body)

    def test_delete(self):        
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2015-01-01',
                    'description': {
                        'text': 'Test description.'
                    },
                    'runtime': 30,
                }
            ]
        })
        self.assertEqual(response.code, 200)
        # we need to test that deleting an episode also delets all relations
        # to watched episodes.
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(
            show_id, 
            1
        ))
        self.assertEqual(response.code, 200)

        response = self.delete('/1/shows/{}/episodes/1'.format(
            show_id
        ))
        self.assertEqual(response.code, 201)

        response = self.get('/1/shows/{}/episodes/{}/watched'.format(
            show_id,
            1
        ))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/episodes/1'.format(show_id))
        self.assertEqual(response.code, 404, response.body)

class Test_episode_append_fields(Testbase):

    def test_user_watched(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), 
            {
                'episodes': [
                    {
                        'air_date': '2003-09-23', 
                        'air_datetime': '2003-09-23T00:00:00Z', 
                        'title': 'Yankee White', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1
                    },
                    {
                        'air_date': '2003-09-24', 
                        'air_datetime': '2003-09-24T00:00:00Z',
                        'title': 'Yankee White 2', 
                        'season': 1, 
                        'number': 2, 
                        'episode': 2
                    },
                ]
            }
        )
        self.assertEqual(response.code, 200)
        self.refresh_es()

        # we haven't watched any episodes so user_watched should be None

        # test single episode
        response = self.get('/1/shows/{}/episodes/1?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episode = utils.json_loads(response.body)
        self.assertTrue('user_watched' in episode)
        self.assertEqual(episode['user_watched'], None)
        self.assertEqual(episode['air_time'], None)
        self.assertEqual(episode['air_datetime'], '2003-09-23T00:00:00Z')

        # test multi episodes
        response = self.get('/1/shows/{}/episodes?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 2, episodes)
        for episode in episodes:
            self.assertTrue('user_watched' in episode)
            self.assertEqual(episode['user_watched'], None)

        # Let's watch some episodes
        for number in [1,2]:
            response = self.put('/1/shows/{}/episodes/{}/watched'.format(show_id, number))
            self.assertEqual(response.code, 200, 'Run: {}'.format(number))

        # test single episode
        response = self.get('/1/shows/{}/episodes/1?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episode = utils.json_loads(response.body)
        self.assertTrue('user_watched' in episode)
        self.assertEqual(episode['user_watched']['times'], 1)

        # test multi episodes
        response = self.get('/1/shows/{}/episodes?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 2)
        for episode in episodes:
            self.assertTrue('user_watched' in episode)
            self.assertEqual(episode['user_watched']['times'], 1)

class Test_play_servers(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'Test show',
            'episodes': [
                {
                    'title': 'Episode 1',
                    'number': 1,
                },                
            ],
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)

        response = self.post('/1/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server = utils.json_loads(response.body)

        # Let's get the server that the user has access to
        # with a play id, that we can use when contacting the server.
        response = self.get('/1/shows/{}/episodes/1/play-servers'.format(
            show['id'],
        ))
        self.assertEqual(response.code, 200)
        servers = utils.json_loads(response.body)
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0]['play_url'], 'http://example.net')
        self.assertTrue(servers[0]['play_id'])

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
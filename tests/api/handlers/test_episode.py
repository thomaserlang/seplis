# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from datetime import datetime, date
from seplis.utils import json_dumps, json_loads
from seplis import utils
from seplis.connections import database
from seplis.config import config

class Test_episode(Testbase):

    def test_search(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'description': {
                        'text': 'Test description.'
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
            'title': None,
            
        })

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
        self.get('http://{}/episodes/_refresh'.format(
            config['elasticsearch']
        ))
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
        self.assertEqual(response.code, 400, response.body)
        
        response = self.get('/1/shows/{}/episodes/1'.format(show_id))
        self.assertEqual(response.code, 404, response.body)

class Test_episode_watched(Testbase):

    def test(self):
        show_id = self.new_show()
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps({
                'episodes': [
                    {
                        'air_date': date(2003, 9, 23), 
                        'title': 'Yankee White', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1
                    },
                ]
            }),
        )

        # mark the episode as watched
        response = response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id, 1))
        self.assertEqual(response.code, 200, response.body)
        watched = json_loads(response.body)
        self.assertEqual(watched['times'], 1)
        # check that duplicating a watched episode works.
        response = response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id, 1), {
            'times': 100,
        })
        self.assertEqual(response.code, 200)
        watched = json_loads(response.body)
        self.assertEqual(watched['times'], 101)

        # check that the list of latest watched shows works.
        show_id_2 = self.new_show()
        response = self.put(
            '/1/shows/{}'.format(show_id_2), 
            json_dumps({
                'episodes': [
                    {
                        'air_date': date(2003, 9, 24), 
                        'title': 'Some test', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1
                    },
                ]
            }),
        )
        response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id_2, 1))
        self.assertEqual(response.code, 200)

        '''
        response = self.get('/1/users/{}/watched/shows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 2)   
        self.assertEqual(shows[0]['id'], show_id_2, response.body)  
        self.assertEqual(shows[1]['id'], show_id, response.body)   
        '''

        # check that the watched episode can be deleted
        response = self.delete('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id, 1))
        self.assertEqual(response.code, 200)

        response = self.delete('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id, 1))
        self.assertEqual(response.code, 400)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
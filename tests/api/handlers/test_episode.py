# coding=UTF-8
import json
import nose
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
            config['api']['elasticsearch']
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
        self.assertEqual(response.code, 200, response.body)
        
        response = self.get('/1/shows/{}/episodes/1'.format(show_id))
        self.assertEqual(response.code, 404, response.body)

class Test_episode_watched(Testbase):

    def _test_watched_count(self, expected_count, expected_minutes_spent=0):        
        response = self.get('/1/users/{}/stats'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        stats = utils.json_loads(response.body)
        self.assertEqual(stats['episodes_watched'], expected_count)
        self.assertEqual(stats['minutes_spent'], expected_minutes_spent)

    def test(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), 
            {
                'episodes': [
                    {
                        'air_date': date(2003, 9, 23), 
                        'title': 'Yankee White', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1,
                        'runtime': 45,
                    },
                ]
            }
        )
        self.assertEqual(response.code, 200)

        # mark the episode as watched
        response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(
            self.current_user.id, 
            show_id, 
            1)
        )
        self.assertEqual(response.code, 200, response.body)

        self._test_watched_count(1, 45)

        # check that duplicating a watched episode works.
        response = response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(
                self.current_user.id, 
                show_id, 
                1
            ), {
            'times': 100,
        })
        self.assertEqual(response.code, 200)
        self._test_watched_count(101, 45*101)

        # check that the list of latest watched shows works.
        show_id_2 = self.new_show()
        response = self.patch(
            '/1/shows/{}'.format(show_id_2), 
            json_dumps({
                'episodes': [
                    {
                        'air_date': date(2003, 9, 24), 
                        'title': 'Some test', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1,
                        'runtime': 45,
                    },
                ]
            }),
        )

        # mark a second episode as watched.
        # run it twitch to check for duplication error.
        # it should increment the watched by 2 in the end.
        for i in [1,2]:
            response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(
                self.current_user.id, 
                show_id_2, 
                1
            ))
            self.assertEqual(response.code, 200)

        self._test_watched_count(103, 45*103)

        # check that the watched episode can be deleted
        response = self.delete('/1/users/{}/watched/shows/{}/episodes/{}'.format(
            self.current_user.id, 
            show_id, 
            1
        ))
        self.assertEqual(response.code, 200)

        response = self.delete('/1/users/{}/watched/shows/{}/episodes/{}'.format(
            self.current_user.id, 
            show_id, 
            1
        ))
        self.assertEqual(response.code, 400)

        # After removing episode 1 as watched there should
        # only be stats left from episode 2.        
        self._test_watched_count(2, 45*2)


class Test_episode_append_fields(Testbase):

    def test_user_watched(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), 
            {
                'episodes': [
                    {
                        'air_date': date(2003, 9, 23), 
                        'title': 'Yankee White', 
                        'season': 1, 
                        'number': 1, 
                        'episode': 1
                    },
                    {
                        'air_date': date(2003, 9, 24), 
                        'title': 'Yankee White 2', 
                        'season': 1, 
                        'number': 2, 
                        'episode': 2
                    },
                ]
            }
        )
        self.assertEqual(response.code, 200)

        # we haven't watched any episodes so user_watched should be None

        # test single episode
        response = self.get('/1/shows/{}/episodes/1?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episode = utils.json_loads(response.body)
        self.assertTrue('user_watched' in episode)
        self.assertEqual(episode['user_watched'], None)

        # test multi episodes
        response = self.get('/1/shows/{}/episodes?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        for episode in episodes:
            self.assertTrue('user_watched' in episode)
            self.assertEqual(episode['user_watched'], None)

        # Let's watch some episodes
        for number in [1,2]:
            response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(self.current_user.id, show_id, number))
            self.assertEqual(response.code, 200)


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
        for episode in episodes:
            self.assertTrue('user_watched' in episode)
            self.assertEqual(episode['user_watched']['times'], 1)


        # test that we can watch a interval of episodes at a time
        response = self.put('/1/users/{}/watched/shows/{}/episodes/1-2'.format(self.current_user.id, show_id))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/episodes?append=user_watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        for episode in episodes:
            self.assertTrue('user_watched' in episode)
            self.assertEqual(episode['user_watched']['times'], 2)

class Test_air_dates(Testbase):

    def test_air_dates(self):
        self.login(constants.LEVEL_EDIT_SHOW)

        # Okay, to run this test we create 2 shows.
        # Each show gets assigned 2 episodes.
        # Show 1's first episode will air today and
        # episode 2 will air in 8 days.
        # Show 2's first episode will air today and
        # the second episode will air tomorrow.

        # Therefore the end result should be 3 episodes in the air dates.
        # Since we only ask for air dates in the next 7 days.

        response = self.post('/1/shows', {
            'title': 'Test show 1',
            'episodes': [
                {
                    'title': 'Episode 1',
                    'number': 1,
                    'season': 1,
                    'episode': 1,
                    'air_date': datetime.utcnow().date().isoformat(),
                },                
                {
                    'title': 'Episode 2',
                    'number': 2,
                    'season': 1,
                    'episode': 2,
                    'air_date': (datetime.utcnow() + timedelta(days=8)).date().isoformat(),
                },
            ],
        })
        self.assertEqual(response.code, 201)
        show_1 = utils.json_loads(response.body)

        response = self.post('/1/shows', {
            'title': 'Test show 2',
            'episodes': [
                {
                    'title': 'Episode 1',
                    'number': 3,
                    'season': 3,
                    'episode': 3,
                    'air_date': datetime.utcnow().date().isoformat(),
                },
                {
                    'title': 'Episode 2',
                    'number': 4,
                    'season': 3,
                    'episode': 4,
                    'air_date': (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
                },
            ],
        })
        self.assertEqual(response.code, 201)
        show_2 = utils.json_loads(response.body) 
        response = self.get('http://{}/_refresh'.format(
            config['api']['elasticsearch']
        ))
        self.assertEqual(response.code, 200)

        # The user must be a fan of the show before they should show up
        # in the user's air dates calender.
        response = self.get('/1/users/{}/air-dates'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        air_dates = utils.json_loads(response.body)
        self.assertEqual(len(air_dates), 0)

        # Let's become a fan of the shows.
        for show_id in [show_1['id'], show_2['id']]:
            response = self.put('/1/users/{}/fan-of/{}'.format(self.current_user.id, show_id), {
                'user_id': self.current_user.id,
            })        
            self.assertEqual(response.code, 200, response.body)

        # Let's get our air dates calendar.        
        self.get('http://{}/_refresh'.format(
            config['api']['elasticsearch']
        ))
        response = self.get('/1/users/{}/air-dates?per_page=5'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        air_dates = utils.json_loads(response.body)
        self.assertEqual(len(air_dates), 3)

        self.assertEqual(air_dates[0]['show']['id'], show_1['id'])
        self.assertEqual(air_dates[0]['episode']['number'], 1)
        self.assertEqual(air_dates[1]['show']['id'], show_2['id'])
        self.assertEqual(air_dates[1]['episode']['number'], 3)
        self.assertEqual(air_dates[2]['show']['id'], show_2['id'])
        self.assertEqual(air_dates[2]['episode']['number'], 4)

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
        self.assertEqual(response.code, 201)
        show = utils.json_loads(response.body)

        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
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
        self.assertEqual(servers[0]['play_server']['id'], server['id'])
        self.assertTrue(servers[0]['play_id'])

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
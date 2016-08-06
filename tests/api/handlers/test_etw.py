# coding=UTF-8
import nose
from seplis.api.testbase import Testbase
from seplis.utils import json_dumps, json_loads
from seplis.api import constants
from datetime import datetime, timedelta

class Test_etw(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'episodes': [
                {
                    'number': 1,
                    'air_date': (datetime.now() - timedelta(days=7)).date().isoformat(),
                },
                {
                    'number': 2,
                    'air_date': (datetime.now() - timedelta(days=7)).date().isoformat(),
                },
            ],
        })
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)
        self.refresh_es()

        # We are not a fan of anything so our etw list should be empty
        response = self.get('/1/users/{}/etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 0, shows)

        # Become a fan of the show
        response = self.put('/1/users/{}/fan-of/{}'.format(
            self.current_user.id,
            show['id'], 
        ))
        self.assertEqual(response.code, 204, response.body)

        # Test that the show and the first episode shows up
        response = self.get('/1/users/{}/etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 1, shows)
        self.assertEqual(shows[0]['id'], show['id'])
        self.assertEqual(shows[0]['next_episode']['number'], 1)
        self.assertEqual(shows[0]['total_next_episodes'], 2)


        # Test after marking the first episode as watching
        # that the episode is still on the etw list
        response = self.put('/1/shows/{}/episodes/{}/watching'.format(
            show['id'],
            1
        ), {
            'position': 120,
        })
        response = self.get('/1/users/{}/etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 1, shows)
        self.assertEqual(shows[0]['id'], show['id'])
        self.assertEqual(shows[0]['next_episode']['number'], 1)
        self.assertEqual(shows[0]['total_next_episodes'], 2)

        # Test that the next episode is on the list after we have watched the first one
        response = self.put(
            '/1/shows/{}/episodes/{}/watched'.format(
                show['id'],
                1
            )
        )
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/users/{}/etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 1, shows)
        self.assertEqual(shows[0]['id'], show['id'])
        self.assertEqual(shows[0]['next_episode']['number'], 2)
        self.assertEqual(shows[0]['total_next_episodes'], 1)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
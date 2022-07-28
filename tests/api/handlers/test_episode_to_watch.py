# coding=UTF-8
from seplis.api.testbase import Testbase
from seplis.utils import json_dumps, json_loads
from seplis.api import constants

class Test_next_to_watch(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'episodes': [
                {'number': 1},
                {'number': 2},
                {'number': 3},
            ],
        })
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)

        # without having watched anything we should get
        # the first episode.
        next_to_watch_url = '/1/shows/{}/episodes/to-watch'.format(
            show['id']
        )
        response = self.get(next_to_watch_url)
        self.assertEqual(response.code, 200)
        ntw = json_loads(response.body)
        self.assertEqual(ntw['number'], 1)
        self.assertEqual(ntw['user_watched'], None)

        # set episode 1 as watching
        response = self.put(
            '/1/shows/{}/episodes/{}/position'.format(show['id'], 1), 
            {'position': 200}
        )
        self.assertEqual(response.code, 204)

        # next to watch should be episode 1 at position 200
        ntw = json_loads(self.get(next_to_watch_url).body)
        self.assertEqual(ntw['number'], 1)
        self.assertEqual(ntw['user_watched']['position'], 200)

        # complete episode 1
        response = self.put(
            '/1/shows/{}/episodes/{}/watched'.format(show['id'], 1)
        )        
        self.assertEqual(response.code, 200, response.body)

        # next to watch should be episode 2
        ntw = json_loads(self.get(next_to_watch_url).body)
        self.assertEqual(ntw['number'], 2)
        self.assertEqual(ntw['user_watched'], None)

        response = self.put(
            '/1/shows/{}/episodes/{}/watched'.format(show['id'], 3)
        )        
        self.assertEqual(response.code, 200, response.body)
        response = self.put(
            '/1/shows/{}/episodes/{}/position'.format(show['id'], 3), 
            {'position': 200}
        )
        self.assertEqual(response.code, 204)
        ntw = json_loads(self.get(next_to_watch_url).body)
        self.assertEqual(ntw['number'], 3)

        response = self.delete(
            '/1/shows/{}/episodes/{}/watched'.format(show['id'], 3)
        )
        self.assertEqual(response.code, 204, response.body)

        ntw = json_loads(self.get(next_to_watch_url).body)
        self.assertEqual(ntw['number'], 2)

        response = self.get('/1/shows/{}/episodes/last-watched'.format(show['id']))
        self.assertEqual(response.code, 200)
        ntw = json_loads(response.body)
        self.assertEqual(ntw['number'], 1)

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
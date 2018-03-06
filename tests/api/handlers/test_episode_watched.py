# coding=UTF-8
import nose
from seplis.api.testbase import Testbase
from seplis.api import constants
from seplis import utils

class Test_episode_watched(Testbase):

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
        self.refresh_es()
        show = utils.json_loads(response.body)
        url = '/1/shows/{}/episodes/{}/watched'.format(show['id'], 1)
        response = self.get(url)
        self.assertEqual(response.code, 204)

        response = self.put(url, {'times': 2})
        self.assertEqual(response.code, 200, response.body)

        response = self.get(url)
        self.assertEqual(response.code, 200)
        w = utils.json_loads(response.body)     
        self.assertEqual(w['times'], 2)
        self.assertEqual(w['position'], 0)        
        self.assertTrue(w['watched_at'] is not None)

        response = self.delete(url)
        self.assertEqual(response.code, 204)
        response = self.get(url)
        self.assertEqual(response.code, 204)

        # test that we can watch a range of episodes at a time
        response = self.put('/1/shows/{}/episodes/1-3/watched'.format(show['id']), 
            {'times': 2})
        self.assertEqual(response.code, 204)
        response = self.get('/1/shows/{}/episodes?append=user_watched'.format(show['id']))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 3, episodes)
        self.assertEqual(episodes[0]['user_watched']['times'], 2)
        self.assertEqual(episodes[1]['user_watched']['times'], 2)
        self.assertEqual(episodes[2]['user_watched']['times'], 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
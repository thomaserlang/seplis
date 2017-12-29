# coding=UTF-8
import nose
from seplis.api.testbase import Testbase
from seplis.utils import json_dumps, json_loads
from seplis.api import constants

class Test_episode_watching(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'episodes': [
                {
                    'number': 1,
                },
            ],
        })
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)
        url = '/1/shows/{}/episodes/{}/watching'.format(
            show['id'],
            1
        )
        # Return 204 if the episode has not been watched
        response = self.get(url)
        self.assertEqual(response.code, 204)

        response = self.put(url, {'position': 200})
        self.assertEqual(response.code, 204, response.body)
        response = self.get(url)
        self.assertEqual(response.code, 200)
        w = json_loads(response.body)
        self.assertEqual(w['completed'], False)        
        self.assertEqual(w['times'], 0)
        self.assertEqual(w['position'], 200)        
        self.assertTrue(w['updated_at'] is not None)

        response = self.put(url, {'position': 201})
        self.assertEqual(response.code, 204, response.body)
        response = self.get(url)
        self.assertEqual(response.code, 200)
        w = json_loads(response.body)
        self.assertEqual(w['completed'], False)        
        self.assertEqual(w['times'], 0)
        self.assertEqual(w['position'], 201)        
        self.assertTrue(w['updated_at'] is not None)

        response = self.delete(url)
        self.assertEqual(response.code, 204, response.body)
        response = self.get(url)
        self.assertEqual(response.code, 204, response.body)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
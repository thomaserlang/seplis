# coding=UTF-8
import nose
from seplis.api.testbase import Testbase
from seplis.utils import json_dumps, json_loads
from seplis.api import constants

class Test_episode_watched(Testbase):

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
        url = '/1/users/{}/watched/shows/{}/episodes/{}'.format(
            self.current_user.id,
            show['id'],
            1
        )
        response = self.get(url)
        self.assertEqual(response.code, 404)

        response = self.put(
            url, 
            {
                'times': 2,
            }
        )
        self.assertEqual(response.code, 200, response.body)

        response = self.get(url)
        self.assertEqual(response.code, 200)
        w = json_loads(response.body)
        self.assertEqual(w['completed'], True)        
        self.assertEqual(w['times'], 2)
        self.assertEqual(w['position'], 0)        
        self.assertTrue(w['updated_at'] is not None)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
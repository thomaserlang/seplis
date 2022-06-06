
import logging
from seplis import utils
from seplis.api import constants
from seplis.api.testbase import Testbase, run_file

class test_movie_watched(Testbase):

    def test(self):
        self.login_async(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/movies', {
            'title': 'National Treasure'
        })
        movie = utils.json_loads(response.body)
        self.assertEqual(response.code, 201)

        response = self.get(f'/1/movies/{movie["id"]}/stared')
        self.assertEqual(response.code, 404)
        
        response = self.put(f'/1/movies/{movie["id"]}/stared')
        self.assertEqual(response.code, 204, response.body)
        
        response = self.get(f'/1/movies/{movie["id"]}/stared')
        self.assertEqual(response.code, 200)
        
        response = self.delete(f'/1/movies/{movie["id"]}/stared')
        self.assertEqual(response.code, 204)

        response = self.get(f'/1/movies/{movie["id"]}/stared')
        self.assertEqual(response.code, 404)

if __name__ == '__main__':
    run_file(__file__)
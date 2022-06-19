
import logging
from seplis import utils
from seplis.api import constants
from seplis.api.testbase import Testbase, run_file

class test_movie(Testbase):

    def test(self):
        self.login_async(constants.LEVEL_EDIT_SHOW)

        r = self.post('/1/movies', {
            'title': 'National Treasure',
            'externals': {
                'imdb': 'tt0368891',
            },
        })
        self.assertEqual(r.code, 201)
        
        r = self.get('/1/movies/externals/imdb/tt0368891')
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(data['externals']['imdb'], 'tt0368891')

        r = self.get('/1/movies/externals/imdb/1234')
        self.assertEqual(r.code, 404)

if __name__ == '__main__':
    run_file(__file__)
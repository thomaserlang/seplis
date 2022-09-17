from seplis import utils
from seplis.api import constants
from seplis.api.testbase import Testbase, run_file

class test_movie(Testbase):

    def test(self):
        self.login_async(constants.LEVEL_EDIT_SHOW)
        response = self.get(f'/1/movies/1')
        self.assertEqual(response.code, 404, response.body)

        response = self.post('/1/movies', {
            'title': 'National Treasure',
            'externals': {
                'imdb': 'tt0368891',
            },
            'alternative_titles': [
                'National Treasure 2004',
            ]
        })
        self.assertEqual(response.code, 201, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['title'], 'National Treasure')
        self.assertEqual(data['externals']['imdb'], 'tt0368891')
        self.assertEqual(data['alternative_titles'], ['National Treasure 2004'])
        
        response = self.get(f'/1/movies/{data["id"]}')
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['title'], 'National Treasure')
        self.assertEqual(data['externals']['imdb'], 'tt0368891')

        response = self.patch(f'/1/movies/{data["id"]}', {
            'externals': {
                'themoviedb': '12345',
            },
            'alternative_titles': [
                'National Treasure test',
            ]
        })
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['title'], 'National Treasure')
        self.assertEqual(data['externals']['imdb'], 'tt0368891')
        self.assertEqual(data['externals']['themoviedb'], '12345')
        self.assertEqual(sorted(data['alternative_titles']), sorted(['National Treasure test', 'National Treasure 2004']))

        response = self.put(f'/1/movies/{data["id"]}', {
            'externals': {
                'themoviedb': '12345',
            },
            'alternative_titles': [],
        })
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['title'], 'National Treasure')
        self.assertFalse('imdb' in data['externals'])
        self.assertEqual(data['externals']['themoviedb'], '12345')
        self.assertEqual(data['alternative_titles'], [])

        response = self.delete(f'/1/movies/{data["id"]}')
        self.assertEqual(response.code, 204)

if __name__ == '__main__':
    run_file(__file__)
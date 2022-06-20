from seplis import utils
from seplis.api import constants
from seplis.api.testbase import Testbase, run_file
from seplis.api.connections import database

class test_movie(Testbase):

    def test(self):
        self.login_async(constants.LEVEL_EDIT_SHOW)

        r = self.post('/1/movies', {
            'title': 'National Treasure',
            'externals': {
                'imdb': 'tt0368891',
            },
            'release_date': '2004-11-19',
            'alternative_titles': [
                'Nacionalno blago',
                'Büyük hazine',
            ],
            'externals': {
                'imdb': 'tt0368891',
            },
        })
        self.assertEqual(r.code, 201)
        movie1 = utils.json_loads(r.body)
        
        database.es.indices.refresh(index='titles')

        r = self.get('/1/search', { 'query': 'National Treasure'})
        self.assertEqual(r.code, 200, r.body)
        data = utils.json_loads(r.body)
        self.assertEqual(data[0]['id'], movie1['id'])


        r = self.get('/1/search', { 'query': 'Natioal Treasure'})
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(data[0]['id'], movie1['id'])


        r = self.get('/1/search', { 'query': 'Natioal 2004'})
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(data[0]['id'], movie1['id'])


        r = self.get('/1/search', { 'query': 'Buyuk-hazine'})
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(data[0]['id'], movie1['id'])

    
        r = self.get('/1/search', { 'query': 'tt0368891'})
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(data[0]['id'], movie1['id'])

        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/movies', {
            'title': 'This is a test show',
            'alternative_titles': [
                'kurt 1',
            ]
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.refresh_es()

        # Test that lowercase does not matter
        response = self.get('/1/search', {'query': 'this'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)

        # Test that both title and alternative_titles is searched in
        response = self.get('/1/search', {'query': 'kurt'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)

        # Test ascii folding
        response = self.get('/1/search', {'query': 'kùrt'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)


        # Test apostrophe
        response = self.post('/1/movies', {
            'title': 'DC\'s legend of something',
            'alternative_titles': [
                'DC’s kurt',
            ]
        })
        self.assertEqual(response.code, 201, response.body)
        show2 = utils.json_loads(response.body)
        self.refresh_es()

        response = self.get('/1/search', {'query': 'dc\'s'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/search', {'query': 'dc’s'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/search', {'query': 'dcs'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        response = self.get('/1/search', {'query': '"dcs kurt"'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 2, data)
        response = self.get('/1/search', {'query': '"dc’s kurt"'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/search', {'query': 'dc'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)

        # Test dotted search
        response = self.get('/1/search', {'query': 'dcs.legend.of.something'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])

        # Test score
        # Searching for "dcs legend of something" should not return
        # "Test DC's legend of something" as the first result
        response = self.post('/1/movies', {
            'title': 'Test DCs legend of something',
        })
        self.assertEqual(response.code, 201, response.body)
        show3 = utils.json_loads(response.body)
        response = self.post('/1/movies', {
            'title': 'legend',
        })
        self.assertEqual(response.code, 201, response.body)
        show3 = utils.json_loads(response.body)
        self.refresh_es()

        response = self.get('/1/search', {'title': 'dc\'s legend of something'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 2, data)
        self.assertEqual(data[0]['id'], show2['id'], data)


        # Test the walking dead
        response = self.post('/1/movies', {
            'title': 'The Walking Dead',
            'release_date': '2010-10-31',
        })
        self.assertEqual(response.code, 201, response.body)
        response = self.post('/1/movies', {
            'title': 'Fear the Walking Dead',
            'release_date': '2015-08-23',
        })
        self.assertEqual(response.code, 201, response.body)
        self.refresh_es()
        response = self.get('/1/search', {'title': 'The Walking Dead'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 2, data)
        self.assertEqual(data[0]['title'], 'The Walking Dead')


        # Test `&` and `and`
        response = self.post('/1/movies', {
            'title': 'Test & Test',
            'release_date': '2010-10-31',
        })
        self.assertEqual(response.code, 201, response.body)
        self.refresh_es()
        response = self.get('/1/search', {'title': 'Test and Test'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)

if __name__ == '__main__':
    run_file(__file__)
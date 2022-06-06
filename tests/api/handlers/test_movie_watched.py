
from seplis import utils
from seplis.api import models, schemas
from seplis.api.testbase import Testbase, run_file

class test_movie_watched(Testbase):

    def test(self):
        self.login_async()
        movie = self.with_session(models.Movie.save, 
            movie=schemas.Movie_schema(title='National Treasure'))        

        response = self.get(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 204)

        response = self.post(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 1)
        self.assertTrue(data['watched_at'])
        
        response = self.get(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 1)
        self.assertEqual(data['position'], 0)
        self.assertTrue(data['watched_at'])

        response = self.post(f'/1/movies/{movie.id}/watched', {
            'watched_at': '2022-06-05T22:00:00+02',
        })
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 2)
        self.assertTrue(data['watched_at'], '2022-06-05T20:00:00Z')

        response = self.post(f'/1/movies/{movie.id}/watched', {
            'watched_at': '2022-06-05T21:00:00',
        })
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 3)
        self.assertTrue(data['watched_at'], '2022-06-05T21:00:00Z')

        response = self.delete(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 2)
        self.assertTrue(data['watched_at'], '2022-06-05T20:00:00Z')

        response = self.delete(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['times'], 1)

        response = self.delete(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 204)

        response = self.get(f'/1/movies/{movie.id}/watched')
        self.assertEqual(response.code, 204)

if __name__ == '__main__':
    run_file(__file__)

from seplis import utils
from seplis.api import models, schemas
from seplis.api.testbase import Testbase, run_file

class test_movie_watched(Testbase):

    def test(self):
        self.login_async()
        movie = self.with_session(models.Movie.save, 
            movie=schemas.Movie_create(title='National Treasure'))        

        response = self.get(f'/1/movies/{movie.id}/position')
        self.assertEqual(response.code, 204)

        response = self.put(f'/1/movies/{movie.id}/position', {
            'position': 300,
        })
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['position'], 300)
        self.assertTrue(data['watched_at'])        
        
        response = self.put(f'/1/movies/{movie.id}/position', {
            'position': 200,
        })
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['position'], 200)


        response = self.get(f'/1/movies/{movie.id}/position')
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['position'], 200)

if __name__ == '__main__':
    run_file(__file__)
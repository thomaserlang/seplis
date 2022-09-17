
from seplis import utils
from seplis.api import models, schemas
from seplis.api.testbase import Testbase, run_file

class test_movie_watched(Testbase):

    def test(self):
        self.login_async()
        movie1 = self.with_session(models.Movie.save, 
            movie=schemas.Movie_create(title='National Treasure'))     
        movie2 = self.with_session(models.Movie.save, 
            movie=schemas.Movie_create(title='Takedown'))   

        r = self.post(f'/1/movies/{movie1.id}/watched', {
            'watched_at': '2022-06-06T01:00:00Z',
        })
        self.assertEqual(r.code, 200)

        r = self.post(f'/1/movies/{movie2.id}/watched', {
            'watched_at': '2022-06-06T02:00:00Z',
        })
        self.assertEqual(r.code, 200)

        r = self.get('/1/users/me/movies-watched')
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], movie2.id)
        self.assertEqual(data[0]['user_watched']['times'], 1)
        self.assertEqual(data[1]['id'], movie1.id)
        self.assertEqual(data[0]['user_watched']['times'], 1)

        r = self.get(f'/1/users/{self.current_user.id}/movies-watched')
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], movie2.id)
        self.assertEqual(data[0]['user_watched']['times'], 1)
        self.assertEqual(data[1]['id'], movie1.id)
        self.assertEqual(data[0]['user_watched']['times'], 1)


if __name__ == '__main__':
    run_file(__file__)
from seplis import utils
from seplis.api import models, schemas
from seplis.api.testbase import Testbase, run_file


class test_movie(Testbase):

    def test(self):
        self.login_async()
        movie1 = self.with_session(models.Movie.save, movie=schemas.Movie_create(title='National Treasure'))
        movie2 = self.with_session(models.Movie.save, movie=schemas.Movie_create(title='Takedown'))

        self.put(f'/1/movies/{movie1.id}/stared')
        self.put(f'/1/movies/{movie2.id}/stared')

        r = self.get('/1/users/me/movies-stared')
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(len(data), 2)
        self.assertTrue(data[0]['user_stared_at'])
        self.assertTrue(data[1]['user_stared_at'])

        r = self.get(f'/1/users/{self.current_user.id}/movies-stared')
        self.assertEqual(r.code, 200)
        data = utils.json_loads(r.body)
        self.assertEqual(len(data), 2)
        self.assertTrue(data[0]['user_stared_at'])
        self.assertTrue(data[1]['user_stared_at'])


if __name__ == '__main__':
    run_file(__file__)
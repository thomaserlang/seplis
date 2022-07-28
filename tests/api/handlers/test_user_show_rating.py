from seplis.api.testbase import Testbase
from seplis import utils, config
from seplis.api import constants, models

class Test_user_show_rating(Testbase):    

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)        
        response = self.post('/1/shows', {
            'title': 'Something',
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)

        response = self.put(f'/1/shows/{show["id"]}/user-rating', {
            'rating': 5,
        })
        self.assertEqual(response.code, 204)

        response = self.get(f'/1/shows/{show["id"]}/user-rating')
        self.assertEqual(response.code, 200)
        d = utils.json_loads(response.body)
        self.assertEqual(d['rating'], 5)

        response = self.get(f'/1/shows/{show["id"]}', {
            'append': 'user_rating'
        })
        self.assertEqual(response.code, 200)
        d = utils.json_loads(response.body)
        self.assertEqual(d['user_rating'], 5)

        response = self.delete(f'/1/shows/{show["id"]}/user-rating')
        self.assertEqual(response.code, 204)

        response = self.get(f'/1/shows/{show["id"]}', {
            'append': 'user_rating'
        })
        self.assertEqual(response.code, 200)
        d = utils.json_loads(response.body)
        self.assertEqual(d['user_rating'], None)

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
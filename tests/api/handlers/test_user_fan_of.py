import nose
import logging
from seplis.api.testbase import Testbase
from seplis.api import constants
from seplis import utils

class Test_user_fan_of(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)

        show1 = utils.json_loads(self.post('/1/shows').body)
        show2 = utils.json_loads(self.post('/1/shows').body)

        # Check a user that is not a fan of any shows
        response = self.get('/1/users/{}/fan-of'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows, [])

        # Become a fan of a show, do it twice 
        # to check for duplication bug.
        for i in [1,2]:
            response = self.put('/1/users/{}/fan-of/{}'.format(
                self.current_user.id, 
                show1['id']
            ))
            self.assertEqual(response.code, 204)

        # Check that the user has become a fan of the show
        response = self.get('/1/users/{}/fan-of'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['id'], show1['id'])

        # Test that the show fans count has incremented
        show1 = utils.json_loads(self.get('/1/shows/{}'.format(show1['id'])).body)
        self.assertEqual(show1['fans'], 1)

        # Become a fan of show 2 to test pagination
        self.put('/1/users/{}/fan-of/{}'.format(self.current_user.id, show2['id']))

        # Test pagination
        response = self.get('/1/users/{}/fan-of?per_page=1'.format(
            self.current_user.id
        ))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(response.headers['X-Total-Count'], '2')
        self.assertEqual(response.headers['X-Total-Pages'], '2')
        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0]['id'], show2['id'])

        response = self.get('/1/users/{}/fan-of?per_page=1&page=2'.format(
            self.current_user.id
        ))
        shows = utils.json_loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0]['id'], show1['id'])

        # Test unfan
        response = self.delete('/1/users/{}/fan-of/{}'.format(
            self.current_user.id,
            show1['id'],
        ))
        self.assertEqual(response.code, 204)

        response = self.get('/1/users/{}/fan-of'.format(
            self.current_user.id
        ))
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['X-Total-Count'], '1', response.body)
        self.assertEqual(len(shows), 1)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
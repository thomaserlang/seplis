import nose
from seplis.api.testbase import Testbase
from seplis import utils
from seplis.api import constants
from datetime import datetime, timedelta

class Test_shows_countdown(Testbase):

    def test(self):        
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'Test show 1',
            'episodes': [
                {
                    'number': 1,
                    'air_date': (datetime.utcnow()-timedelta(days=1)).date().isoformat(),
                },
                {
                    'number': 2,
                    'air_date': datetime.utcnow().date().isoformat(),
                },
                {
                    'number': 3,
                    'air_date': (datetime.utcnow()+timedelta(days=1)).date().isoformat(),
                },
            ],
        })
        self.assertEqual(response.code, 201)
        show = utils.json_loads(response.body)
        response = self.post('/1/shows', {
            'title': 'Test show 2',
            'episodes': [
                {
                    'number': 1,
                    'air_date': (datetime.utcnow()-timedelta(days=1)).date().isoformat(),
                },
                {
                    'number': 2,
                    'air_date': datetime.utcnow().date().isoformat(),
                },
                {
                    'number': 3,
                    'air_date': (datetime.utcnow()+timedelta(days=1)).date().isoformat(),
                },
            ],
        })
        self.assertEqual(response.code, 201)

        # Not a fan yet = empty
        response = self.get('/1/users/{}/shows-countdown'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows, [])

        response = self.put('/1/users/{}/fan-of/{}'.format(
            self.current_user.id, show['id'],
        ))

        response = self.get('/1/users/{}/shows-countdown'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['show']['title'], 'Test show 1')
        self.assertEqual(shows[0]['episode']['number'], 2)
        self.assertEqual(len(shows), 1)



if __name__ == '__main__':
    nose.run(defaultTest=__name__)
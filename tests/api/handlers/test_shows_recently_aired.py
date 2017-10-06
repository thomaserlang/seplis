import nose
from seplis.api.testbase import Testbase
from seplis import utils
from seplis.api import constants
from datetime import datetime, timedelta

class Test_shows_recently_aired(Testbase):

    def test(self):        
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'Test show 1',
            'episodes': [
                {
                    'number': 1,
                    'air_date': (datetime.utcnow()-timedelta(days=2)).date().isoformat(),
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
        show1 = utils.json_loads(response.body)
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
        show2 = utils.json_loads(response.body)

        # Not a fan yet = empty
        response = self.get('/1/users/{}/shows-recently-aired'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows, [])

        response = self.put('/1/users/{}/fan-of/{}'.format(
            self.current_user.id, show1['id'],
        ))
        response = self.put('/1/users/{}/fan-of/{}'.format(
            self.current_user.id, show2['id'],
        ))

        response = self.get('/1/users/{}/shows-recently-aired'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['show']['title'], 'Test show 2')
        self.assertEqual(shows[0]['episode']['number'], 1)
        self.assertEqual(shows[1]['show']['title'], 'Test show 1')
        self.assertEqual(shows[1]['episode']['number'], 1)
        self.assertEqual(len(shows), 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
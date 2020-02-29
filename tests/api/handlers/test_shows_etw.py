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
        response = self.get('/1/users/{}/shows-etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows, [])

        # Become a fan
        response = self.put('/1/users/{}/shows-following/{}'.format(
            self.current_user.id, show1['id'],
        ))
        response = self.put('/1/users/{}/shows-following/{}'.format(
            self.current_user.id, show2['id'],
        ))
        # Watch some episodes
        response = self.put('/1/shows/{}/episodes/1/watched'.format(show1['id']))
        self.assertEqual(response.code, 200, response.body)
        response = self.put('/1/shows/{}/episodes/2/watched'.format(show2['id']))
        self.assertEqual(response.code, 200, response.body)

        response = self.get('/1/users/{}/shows-etw'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 1, shows)
        self.assertEqual(shows[0]['show']['title'], 'Test show 1')
        self.assertEqual(shows[0]['episode']['number'], 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
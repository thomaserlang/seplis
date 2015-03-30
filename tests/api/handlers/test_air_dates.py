# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from datetime import datetime, date, timedelta
from seplis.utils import json_dumps, json_loads
from seplis import utils
from seplis.api.decorators import new_session
from seplis.api.connections import database
from seplis.config import config
from seplis.api import constants

class Test_air_dates(Testbase):

    def test_air_dates(self):
        self.login(constants.LEVEL_EDIT_SHOW)

        # Okay, to run this test we create 2 shows.
        # Each show gets assigned 2 episodes.
        # Show 1's first episode will air "today" and
        # episode 2 will air in "8 days".
        # Show 2's first episode will air "today" and
        # the second episode will air "tomorrow".

        # Therefore the end result should be 3 episodes in the result.
        # Since we only ask for episodes that airs in the next 7 days.
        episode_airdates = [
            datetime.utcnow().date().isoformat(),
            (datetime.utcnow() + timedelta(days=8)).date().isoformat(),
            (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
        ]
        response = self.post('/1/shows', {
            'title': 'Test show 1',
            'episodes': [
                {
                    'title': 'Episode 1',
                    'number': 1,
                    'season': 1,
                    'episode': 1,
                    'air_date': episode_airdates[0],
                },                
                {
                    'title': 'Episode 2',
                    'number': 2,
                    'season': 1,
                    'episode': 2,
                    'air_date': episode_airdates[1],
                },
            ],
        })
        self.assertEqual(response.code, 201)
        show_1 = utils.json_loads(response.body)

        response = self.post('/1/shows', {
            'title': 'Test show 2',
            'episodes': [
                {
                    'title': 'Episode 1',
                    'number': 3,
                    'season': 3,
                    'episode': 3,
                    'air_date': episode_airdates[0],
                },
                {
                    'title': 'Episode 2',
                    'number': 4,
                    'season': 3,
                    'episode': 4,
                    'air_date': episode_airdates[2],
                },
            ],
        })
        self.assertEqual(response.code, 201)
        show_2 = utils.json_loads(response.body) 
        response = self.get('http://{}/_refresh'.format(
            config['api']['elasticsearch']
        ))
        self.assertEqual(response.code, 200)

        # The user must be a fan of the show before they should show up
        # in the user's air dates calender.
        response = self.get('/1/users/{}/air-dates'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        airdates = utils.json_loads(response.body)
        self.assertEqual(len(airdates), 0)

        # Let's become a fan of the shows.
        for show_id in [show_1['id'], show_2['id']]:
            response = self.put('/1/users/{}/fan-of/{}'.format(self.current_user.id, show_id), {
                'user_id': self.current_user.id,
            })        
            self.assertEqual(response.code, 200, response.body)

        # Let's get our air dates calendar.        
        self.get('http://{}/_refresh'.format(
            config['api']['elasticsearch']
        ))
        response = self.get('/1/users/{}/air-dates?per_page=5'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        airdates = utils.json_loads(response.body)
        self.assertEqual(len(airdates), 2, airdates)

        self.assertEqual(airdates[0]['air_date'], episode_airdates[0])
        self.assertEqual(airdates[0]['shows'][0]['id'], show_1['id'])
        self.assertEqual(airdates[0]['shows'][0]['episodes'][0]['number'], 1)
        self.assertEqual(airdates[0]['shows'][1]['id'], show_2['id'])
        self.assertEqual(airdates[0]['shows'][1]['episodes'][0]['number'], 3)
        self.assertEqual(airdates[1]['air_date'], episode_airdates[2])
        self.assertEqual(airdates[1]['shows'][0]['id'], show_2['id'])
        self.assertEqual(airdates[1]['shows'][0]['episodes'][0]['number'], 4)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
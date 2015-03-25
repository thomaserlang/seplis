# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis import utils, config
from seplis.api import constants, models
from seplis.api.decorators import new_session
from datetime import datetime, date


class test_shows_recently_watched(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        show_ids = [self.new_show() for x in range(0, 3)]
        air_date = datetime.now().date().isoformat()
        for show_id in show_ids:
            response = self.put('/1/shows/{}'.format(show_id), {
                'episodes': [
                    {
                        'number': show_id,
                        'air_date': air_date,
                    }
                ]
            })
            self.assertEqual(response.code, 200, response.body)
            response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(
                self.current_user.id,
                show_id,
                show_id,
            ))
            self.assertEqual(response.code, 200)

        response = self.get('/1/users/{}/shows-recently-watched'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 3, shows)
        for show, show_id in zip(shows, reversed(show_ids)):
            self.assertEqual(show['id'], show_id)
            self.assertEqual(show['user_watching']['number'], show_id)

        # test pagination        
        for i, show_id in enumerate(reversed(show_ids)):
            response = self.get('/1/users/{}/shows-recently-watched'.format(
                self.current_user.id
            ), {
                'per_page': 1,
                'page': i+1,
            })
            self.assertEqual(response.code, 200)
            shows = utils.json_loads(response.body)
            self.assertEqual(len(shows), 1, shows)
            self.assertEqual(shows[0]['id'], show_id)
            self.assertEqual(shows[0]['user_watching']['number'], show_id)
            self.assertTrue(isinstance(shows[0]['user_watching']['episode'], dict))
            self.assertEqual(shows[0]['user_watching']['episode']['number'], show_id)
            self.assertEqual(shows[0]['user_watching']['episode']['air_date'], air_date)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
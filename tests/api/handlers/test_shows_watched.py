# coding=UTF-8
import json
import nose
import logging
from seplis.api.testbase import Testbase
from seplis import utils, config
from seplis.api import constants, models
from seplis.api.decorators import new_session
from datetime import datetime, date

class Test_shows_watched(Testbase):

    def test(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        show_ids = [self.new_show() for x in range(0, 3)]
        air_date = datetime.now().date().isoformat()
        # run it twice to check for duplication bugs.
        for show_id in show_ids+show_ids:
            response = self.put('/1/shows/{}'.format(show_id), {
                'episodes': [
                    {
                        'number': show_id,
                        'air_date': air_date,
                    }
                ]
            })
            self.assertEqual(response.code, 200, response.body)
            response = self.put('/1/shows/{}/episodes/{}/watched'.format(
                show_id,
                show_id,
            ))
            self.assertEqual(response.code, 200)

        response = self.get('/1/users/{}/shows-watched'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 3, shows)
        for show, show_id in zip(shows, reversed(show_ids)):
            self.assertEqual(show['id'], show_id)
            self.assertEqual(show['user_watching']['episode_number'], show_id)

        # test pagination
        for i, show_id in enumerate(reversed(show_ids)):
            response = self.get('/1/users/{}/shows-watched'.format(
                self.current_user.id
            ), {
                'per_page': 1,
                'page': i+1,
            })
            self.assertEqual(response.code, 200)
            shows = utils.json_loads(response.body)
            self.assertEqual(len(shows), 1, shows)
            self.assertEqual(shows[0]['id'], show_id)
            self.assertEqual(shows[0]['user_watching']['episode_number'], show_id)
            self.assertTrue(isinstance(shows[0]['user_watching']['episode'], dict))
            self.assertEqual(shows[0]['user_watching']['episode']['number'], show_id)
            self.assertEqual(shows[0]['user_watching']['episode']['air_date'], air_date)

        # test that deleting all watched episodes for a show does not
        # reset the hole recently watched list.
        response = self.delete('/1/shows/{0}/episodes/{0}/watched'.format(
            show_ids[0]# the episode number is the same as the show id.
        ))
        response = self.get('/1/users/{}/shows-watched'.format(
            self.current_user.id
        ))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 2, shows)


        # test that resetting the position does not changed the show watched
        # order
        response = self.put('/1/shows/{0}/episodes/{0}/position'.format(
            show_ids[1]# the episode number is the same as the show id.
        ), {'position': 10})
        self.assertEqual(response.code, 204)

        response = self.get('/1/users/{}/shows-watched'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['id'], show_ids[2])
        self.assertEqual(shows[1]['id'], show_ids[1])

        response = self.put('/1/shows/{0}/episodes/{0}/watched'.format(
            show_ids[2]# the episode number is the same as the show id.
        ))
        self.assertEqual(response.code, 200)

        response = self.get('/1/users/{}/shows-watched'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['id'], show_ids[2])
        self.assertEqual(shows[1]['id'], show_ids[1])

        response = self.delete('/1/shows/{0}/episodes/{0}/position'.format(
            show_ids[1]# the episode number is the same as the show id.
        ))
        self.assertEqual(response.code, 204)
  
        response = self.get('/1/users/{}/shows-watched'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['id'], show_ids[2])
        self.assertEqual(shows[1]['id'], show_ids[1])

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
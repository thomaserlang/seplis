# coding=UTF-8
from seplis.api.testbase import Testbase
from seplis import utils, config
from seplis.api import constants, models
from seplis.api.decorators import new_session

class Test(Testbase):
    
    def test(self):
        self.login()
        with new_session() as session:
            show = models.Series(
                title='Test show',
                runtime=30,
            )
            session.add(show)
            session.flush()

            episode1 = models.Episode(show_id=show.id, number=1)
            session.add(episode1)
            episode2 = models.Episode(show_id=show.id, number=2)
            session.add(episode2)
            episode3 = models.Episode(show_id=show.id, number=3, runtime=40)
            session.add(episode3)
            session.commit()

            show = show.serialize()
            episode1 = episode1.serialize()
            episode2 = episode2.serialize()
            episode3 = episode3.serialize()

        response = self.get('/1/shows/{}/user-stats'.format(show['id']))
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['episodes_watched'], 0)
        self.assertEqual(data['episodes_watched_minutes'], 0)

        # watched time
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show['id'],1))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/user-stats'.format(show['id']))
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['episodes_watched'], 1, data)
        self.assertEqual(data['episodes_watched_minutes'], 30, data)

        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show['id'],1))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/user-stats'.format(show['id']))
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['episodes_watched'], 2, data)
        self.assertEqual(data['episodes_watched_minutes'], 60, data)

        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show['id'],2))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/user-stats'.format(show['id']))
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['episodes_watched'], 3, data)
        self.assertEqual(data['episodes_watched_minutes'], 90, data)

        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show['id'],3))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/user-stats'.format(show['id']))
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['episodes_watched'], 4, data)
        self.assertEqual(data['episodes_watched_minutes'], 130, data)

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
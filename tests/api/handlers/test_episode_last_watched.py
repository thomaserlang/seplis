import nose
from seplis.api.testbase import Testbase
from seplis import utils, constants
from seplis.api.decorators import new_session
from seplis.api import models

class Test_next_to_watch(Testbase):

    def test(self):
        self.login(constants.LEVEL_PROGRESS)
        # Create a show and 2 episodes
        with new_session() as session:
            show = models.Show()
            session.add(show)
            session.flush()
            episode1 = models.Episode(show_id=show.id, number=1)
            session.add(episode1)
            episode2 = models.Episode(show_id=show.id, number=2)
            session.add(episode2)
            session.commit()
            show_id = show.id

        # Test no watched episodes
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 204, response.body)
        self.assertEqual(response.body, b'')

        # set episode 1 as watching
        response = self.put('/1/shows/{}/episodes/{}/watching'.format(show_id,1), 
            {'position': 200}
        )
        self.assertEqual(response.code, 204)

        # Since we have not completed the first episode 
        # and it's the only episode we have watched the result
        # should be empty 
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 204, response.body)
        self.assertEqual(response.body, b'')


        # Start watching episode 2.
        # Episode 1 should now be the latest watched even though it 
        # is not completed.
        response = self.put('/1/shows/{}/episodes/{}/watching'.format(show_id,2), 
            {'position': 202}
        )
        self.assertEqual(response.code, 204)
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['number'], 1)
        self.assertEqual(data['user_watched']['position'], 200)
        self.assertEqual(data['user_watched']['times'], 0)

        # Set episode 2 as completed.
        # Episode 2 should now be the last watched
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show_id,2))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['number'], 2)
        self.assertEqual(data['user_watched']['position'], 0)
        self.assertEqual(data['user_watched']['times'], 1)


        # set episode 1 as watched
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show_id,1))
        # unwatch episode 2
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show_id,2), {
            'times': -1,
        })
        self.assertEqual(response.code, 204)
        # episode 1 should now be the last watched
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['number'], 1)

        # watch episode 2 twice
        response = self.put('/1/shows/{}/episodes/{}/watched'.format(show_id,2), {
            'times': 2,
        })
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}/episodes/last-watched'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data['number'], 2)
        self.assertEqual(data['user_watched']['position'], 0)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
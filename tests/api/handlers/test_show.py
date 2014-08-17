# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from datetime import datetime, date
from seplis.utils import json_dumps, json_loads
from seplis import utils
from seplis.connections import database

class test_show(Testbase):

    def update_show(self):
        show_id = self.new_show()
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps({'title2': 'asd', 'description': {'asd': '123'}}),
        )
        self.assertEqual(response.code, 400, response.body)
        self.assertEqual(json_loads(response.body)['errors'][0]['message'], 'extra keys not allowed')

        show = {
            'title': 'Thomas\' show',
            'premiered': datetime.utcnow().date(),
            'ended': datetime.utcnow().date(), 
            'episodes': [
                {
                    'number': 1,
                    'title': 'First episode',
                    'season': 1,
                    'episode': 1
                },
                {
                    'number': 2,
                    'title': 'Second episode',
                    'season': 2,
                    'episode': 2
                }
            ],
            'external': {
                'imdb': 'tt1234',
                'tvrage': '123',
            }
        }
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps(show),
        )
        self.assertEqual(response.code, 200, response.body)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'Thomas\' show', response.body)
        self.assertEqual(show['external']['imdb'], 'tt1234')
        self.assertEqual(show['external']['tvrage'], '123')
        return show_id

class test_show_1(test_show):

    def test_show(self):
        # get single show 
        show_id = self.update_show()
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'Thomas\' show', response.body)

    def test_put(self):
        show_id = self.new_show()

        # test wrong field
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps({'title2': 'asd'}),
        )
        self.assertEqual(response.code, 400, response.body)

        # test normal update
        show = {
            'title': 'Thomas\' show 1',
            'premiered': datetime.utcnow().date(),
            'ended': datetime.utcnow().date(), 
            'episodes': [
                {
                    'number': 1,
                    'title': 'First episode',
                    'season': 1,
                    'episode': 1
                },
                {
                    'number': 3,
                    'title': 'Third episode',
                    'season': 2,
                    'episode': 1
                },
                {
                    'number': 2,
                    'title': 'Second episode',
                    'season': 1,
                    'episode': 2
                },
            ],
            'external': {
                'imdb': 'tt1234',
                'tvrage': '123'
            },
            'index': {
                'info': 'imdb',
                'episodes': 'tvrage'
            }
        }
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps(show),
        )
        self.assertEqual(response.code, 200, response.body)

        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'Thomas\' show 1', response.body)
        self.assertEqual(show['external']['imdb'], 'tt1234')
        self.assertEqual(show['index']['info'], 'imdb')
        self.assertEqual(show['index']['episodes'], 'tvrage')
        self.assertEqual(show['followers'], 0, response.body)
        self.assertEqual(len(show['seasons']), 2)
        self.assertEqual(show['seasons'][0]['season'], 1)
        self.assertEqual(show['seasons'][0]['from'], 1)
        self.assertEqual(show['seasons'][0]['to'], 2)
        self.assertEqual(show['seasons'][1]['season'], 2)
        self.assertEqual(show['seasons'][1]['from'], 3)
        self.assertEqual(show['seasons'][1]['to'], 3)

        # check update overwrite and append
        show = {
            'title': 'thomas 2',
            'external': {
                'tvrage': '123'
            }
        }
        response = self.patch(
            '/1/shows/{}'.format(show_id), 
            json_dumps(show),
        )
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'thomas 2', response.body)
        self.assertEqual(show['external']['imdb'], 'tt1234')
        self.assertEqual(show['external']['tvrage'], '123')

        show = {
            'external': {
                'tvrage': '1234'
            }
        }
        response = self.patch(
            '/1/shows/{}'.format(show_id), 
            json_dumps(show),
        )
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'thomas 2', response.body)
        self.assertEqual(show['external']['imdb'], 'tt1234')
        self.assertEqual(show['external']['tvrage'], '1234')

        # test index
        show = {
            'index': {
                'wrong': 'tvrage',
            }
        }
        response = self.put(
            '/1/shows/{}'.format(show_id), 
            json_dumps(show),
        )
        self.assertEqual(response.code, 400, response.body)

        show = {
            'index': {
                'info': 'tvrage',
                'episodes': 'imdb'
            }
        }
        response = self.patch(
            '/1/shows/{}'.format(show_id),
            json_dumps(show),
        )
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['index']['info'], 'tvrage')
        self.assertEqual(show['index']['episodes'], 'imdb')

    def test_show_2(self):
        self.login(6)

        show = {
            'ended': None, 
            'title': 'NCIS æøå', 
            'external': {
                'imdb': 'tt1234',
                'tvrage': '123',
            },
            'episodes': [
                {
                    'air_date': date(2003, 9, 23), 
                    'title': 'Yankee White', 
                    'season': 1, 
                    'number': 1, 
                    'episode': 1
                }, 
                {
                    'air_date': date(2003, 9, 30), 
                    'title': 'Hung Out to Dry', 
                    'season': 1, 
                    'number': 2, 
                    'episode': 2
                }, 
                {
                    'air_date': date(2003, 10, 7), 
                    'title': 'Seadog', 
                    'season': 1, 
                    'number': 3, 
                    'episode': 3
                }
            ]
        }
        response = self.post('/1/shows', show)
        self.assertEqual(response.code, 201, response.body)

    def test_duplicate_external(self):
        self.login(6)

        # create a new show
        response = self.post('/1/shows', {
            'external': {
                'a': '123',
                'b': '321',
            }
        })
        self.assertEqual(response.code, 201, response.body)
        show = json_loads(response.body)
        self.assertTrue(show['id'] > 0)
        self.assertEqual(show['external']['a'], '123')
        self.assertEqual(show['external']['b'], '321')

        response = self.post('/1/shows', {
            'external': {
                'a': '123',
            }
        })
        self.assertEqual(response.code, 400, response.body)
        error = json_loads(response.body)
        self.assertEqual(error['extra']['show'], show)
        self.assertEqual(error['extra']['external_title'], 'a')
        self.assertEqual(error['extra']['external_id'], '123')

    """
    def test_tagging(self):
        self.login(0)
        show_id = self.new_show()        
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)

        show_id2 = self.new_show()        
        response = self.get('/1/shows/{}'.format(show_id2))
        self.assertEqual(response.code, 200)
        show2 = json_loads(response.body)

        show_id3 = self.new_show()        
        response = self.get('/1/shows/{}'.format(show_id3))
        self.assertEqual(response.code, 200)
        show3 = json_loads(response.body)

        # empty list of tags for this user and show
        response = self.get('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags), 0, response.body)

        # add a tag to the show
        response = self.put('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id), {
            'name': 'Test tag 1',
        })
        self.assertEqual(response.code, 200, response.body)
        tag = json_loads(response.body)
        self.assertTrue(tag['id'] > 0, response.body)

        # check that we can receive all the tags added to the show
        response = self.get('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags), 1, response.body)
        self.assertEqual(tag, tags[0])

        # add a new tag
        response = self.put('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id), {
            'name': 'Test tag 2',
        })
        self.assertEqual(response.code, 200)
        tag2 = json_loads(response.body)

        # check that we get both tags for the show
        response = self.get('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags), 2, response.body)      
        self.assertEqual(tag, tags[0], response.body)        
        self.assertEqual(tag2, tags[1], response.body) 

        # add the second show to tag 1
        response = self.put('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id2), {
            'name': 'Test tag 1',
        })
        self.assertEqual(response.code, 200)

        # check that we can get the shows from tag 1
        response = self.get('/1/users/{}/tags/{}/shows'.format(self.current_user.id, tag['id']))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows['records']), 2, response.body)
        self.assertEqual(shows['records'][0], show)
        self.assertEqual(shows['records'][1], show2)

        # add the third show to tag 3
        response = self.put('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id3), {
            'name': 'Test tag 3',
        })
        self.assertEqual(response.code, 200)
        tag3 = json_loads(response.body)


        # test that we can get all the shows in all the users tags
        response = self.get('/1/users/{}/tags/shows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows['records']), 3, response.body)
        self.assertEqual(shows['records'][0], show)
        self.assertEqual(shows['records'][1], show2)
        self.assertEqual(shows['records'][2], show3)
        self.assertEqual(shows['total'], 3)

        # test pagination
        response = self.get('/1/users/{}/tags/shows?per_page=1'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows['records']), 1, response.body)
        self.assertEqual(shows['records'][0], show)

        response = self.get('/1/users/{}/tags/shows?per_page=1&page=3'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows['records']), 1, response.body)
        self.assertEqual(shows['records'][0], show3)
        self.assertEqual(shows['total'], 3)

        # get a list of tags that the user has used
        response = self.get('/1/users/{}/tags?type=shows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags['shows']), 3, response.body)

        # delete a tag relation
        response = self.delete('/1/users/{}/tags/{}/shows/{}'.format(
            self.current_user.id, 
            tag['id'],
            show_id,
        ))
        self.assertEqual(response.code, 200)

        # after we have removed tag 1 from show 1 we'll have to test that only tag 2 will 
        # come back for show 1
        response = self.get('/1/users/{}/tags/shows/{}'.format(self.current_user.id, show_id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags), 1, response.body)
        self.assertEqual(tag2, tags[0])

        # the tag test 2 for the show 2 have only been used on that show.
        # therefore we must make sure that it does not show up under the users active tags.

        # delete a tag relation
        response = self.delete('/1/users/{}/tags/{}/shows/{}'.format(
            self.current_user.id, 
            tag3['id'],
            show_id3,
        ))
        self.assertEqual(response.code, 200)

        response = self.get('/1/users/{}/tags?type=shows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        tags = json_loads(response.body)
        self.assertEqual(len(tags['shows']), 2, response.body)


        # make sure that what deleting a show from a tag it still exists 
        # in the all list if it still is connected to a tag.
        response = self.delete('/1/users/{}/tags/{}/shows/{}'.format(
            self.current_user.id, 
            tag['id'],
            show_id,
        ))
        self.assertEqual(response.code, 200)

        response = self.get('/1/users/{}/tags/shows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows['records']), 2, response.body)
    """
class test_show_external(test_show):

    def test_external(self):
        show_id = self.update_show()

        response = self.get('/1/shows/external/imdb/tt1234')
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'Thomas\' show')

        response = self.get('/1/shows/external/tvrage/123')
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['title'], 'Thomas\' show')

class test_episodes(test_show):

    def test_episodes(self):
        show_id = self.update_show()
        response = self.get('/1/shows/{}/episodes?from=1&to=2'.format(show_id))
        self.assertEqual(response.code, 200)
        episodes = json_loads(response.body)
        self.assertEqual(episodes[0]['number'], 1)
        self.assertEqual(episodes[0]['title'], 'First episode')
        self.assertEqual(episodes[0]['season'], 1)
        self.assertEqual(episodes[0]['episode'], 1)
        self.assertEqual(episodes[1]['number'], 2)
        self.assertEqual(episodes[1]['title'], 'Second episode')
        self.assertEqual(episodes[1]['season'], 2)
        self.assertEqual(episodes[1]['episode'], 2)

class test_episode(test_show):

    def test_episode(self):
        show_id = self.update_show()

        response = self.get('/1/shows/{}/episodes/{}'.format(show_id, 3))
        self.assertEqual(response.code, 404)

        # Create
        response = self.put('/1/shows/{}/episodes/{}'.format(show_id, 3), {
            'season': 3,
            'episode': 3,
            'title': 'Thrid episode'
        })
        self.assertEqual(response.code, 200)
        episode = json_loads(response.body)
        response = self.get('/1/shows/{}/episodes/{}'.format(show_id, 3))
        self.assertEqual(response.code, 200)
        episode = json_loads(response.body)
        self.assertEqual(episode['number'], 3)
        self.assertEqual(episode['title'], 'Thrid episode')
        self.assertEqual(episode['season'], 3)
        self.assertEqual(episode['episode'], 3)


        # Update
        response = self.put('/1/shows/{}/episodes/{}'.format(show_id, 3), {
            'season': 4,
            'episode': 4,
            'title': 'Fourth episode'
        })
        response = self.get('/1/shows/{}/episodes/{}'.format(show_id, 3))
        self.assertEqual(response.code, 200)
        episode = json_loads(response.body)
        self.assertEqual(episode['number'], 3)
        self.assertEqual(episode['title'], 'Fourth episode')
        self.assertEqual(episode['season'], 4)
        self.assertEqual(episode['episode'], 4)

        # Delete
        response = self.delete('/1/shows/{}/episodes/{}'.format(show_id, 1234))
        self.assertEqual(response.code, 404, response.body)
        response = self.delete('/1/shows/{}/episodes/{}'.format(show_id, 3))
        self.assertEqual(response.code, 204)
        response = self.get('/1/shows/{}/episodes/{}'.format(show_id, 3))
        self.assertEqual(response.code, 404)

class Test_follow(test_show):

    def test(self):
        show_id = self.new_show()
        response = self.put('/1/shows/{}/follow'.format(show_id))
        self.assertEqual(response.code, 204)

        # duplicate follow
        response = self.put('/1/shows/{}/follow'.format(show_id))
        self.assertEqual(response.code, 204)
        
        # test that the followers count on the show increments
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['followers'], 1)

        # second show
        show_id_2 = self.new_show()
        response = self.put('/1/shows/{}/follow'.format(show_id_2))
        self.assertEqual(response.code, 204)

        # test get shows
    
        response = self.get('/1/users/{}/follows'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 2)
        self.assertEqual(shows[0]['id'], show_id, response.body)        
        self.assertEqual(shows[1]['id'], show_id_2, response.headers)
        
        # delete follow status
        response = self.delete('/1/shows/{}/follow'.format(show_id))
        self.assertEqual(response.code, 204)

        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = json_loads(response.body)
        self.assertEqual(show['followers'], 0)
        
        # should be an error if the user does not follow the show.
        # response = self.delete('/1/shows/{}/fans'.format(show_id))
        # self.assertEqual(response.code, 400)

class Test_multi_shows(test_show):

    def test_get(self):
        show_id1 = self.new_show()        
        response = self.put('/1/shows/{}/follow'.format(show_id1))
        self.assertEqual(response.code, 204)
        show_id2 = self.new_show()
        response = self.put('/1/shows/{}/follow'.format(show_id2))
        self.assertEqual(response.code, 204)

        response = self.get('/1/shows/{},{},'.format(show_id1, show_id2))
        self.assertEqual(response.code, 200)
        shows = json_loads(response.body)
        self.assertEqual(len(shows), 2)
        for show in shows:
            self.assertEqual(show['followers'], 1)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis import utils, config
from seplis.api import constants, models
from seplis.decorators import new_session
from datetime import datetime, date
import time

class test_show(Testbase):

    def test_post(self):
        self.login(constants.LEVEL_EDIT_SHOW)

        # Creating a new show without any data is OK.
        response = self.post('/1/shows')
        self.assertEqual(response.code, 201, response.body)

        # this should be a successfully creation of a new show
        response = self.post('/1/shows', {
            'title': 'NCIS',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service. \_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
                'title': 'IMDb',
                'url': 'http://www.imdb.com/title/tt0364845/',
            },
            'premiered': '2003-01-01',
            'ended': None,
            'indices': {
                'info': 'imdb',
                'episodes': 'imdb',
            },
            'externals': {
                'imdb': 'tt0364845',
            },
            'genres': [
                'Action',
                'Thriller',
            ],
            'alternate_titles': [
                'NCIS 2',
                'NCIS 3',
            ],
            'runtime': 40,
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'NCIS')
        self.assertEqual(show['description'], {
            'text': 'The cases of the Naval Criminal Investigative Service. \_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
            'title': 'IMDb',
            'url': 'http://www.imdb.com/title/tt0364845/',
        })
        self.assertEqual(show['premiered'], '2003-01-01')
        self.assertEqual(show['ended'], None)
        self.assertEqual(show['indices'], {
            'info': 'imdb',
            'episodes': 'imdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt0364845',
        })
        self.assertTrue('Action' in show['genres'])
        self.assertTrue('Thriller' in show['genres'])
        self.assertTrue('NCIS 2' in show['alternate_titles'])
        self.assertTrue('NCIS 3' in show['alternate_titles'])
        self.assertEqual(show['runtime'], 40)

    def test_patch(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'title': 'NCIS',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service.',
            },
            'premiered': '2003-01-01',
            'indices': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt0364845',
            },
        })
        self.assertEqual(response.code, 200, response.body)
        response = self.patch('/1/shows/{}'.format(show_id), {
            'indices': {
                'episodes': 'imdb'
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'NCIS')
        self.assertEqual(show['description'], {
            'text': 'The cases of the Naval Criminal Investigative Service.',
            'title': None,
            'url': None,
        })
        self.assertEqual(show['premiered'], '2003-01-01')
        self.assertEqual(show['ended'], None)
        self.assertEqual(show['indices'], {
            'info': 'imdb',
            'episodes': 'imdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt0364845',
        })


    def test_put(self):
        show_id = self.new_show()
        response = self.put('/1/shows/{}'.format(show_id), {
            'title': 'NCIS',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service.',
            },
            'premiered': '2003-01-01',
            'indices': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt0364845',
            },
        })

        self.assertEqual(response.code, 200, response.body)
        response = self.put('/1/shows/{}'.format(show_id), {
            'indices': {
                'episodes': 'thetvdb',
            },
            'externals': {
                'thetvdb': '1234',
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'NCIS')
        self.assertEqual(show['indices'], {
            'info': None,
            'episodes': 'thetvdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'thetvdb': '1234',
        })
    def test_indices(self):
        show_id = self.new_show()

        # it should not be possible to add a index with out it exists as
        # a external.
        response = self.patch('/1/shows/{}'.format(show_id), {
            'indices':{
                'info': 'imdb',
            }
        })
        self.assertEqual(response.code, 400, response.body)
        error = utils.json_loads(response.body)
        self.assertEqual(error['code'], 1401)


        # so when adding the index to the externals with a value
        # it should be OK.
        response = self.patch('/1/shows/{}'.format(show_id), {
            'indices':{
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt1234',
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)        
        self.assertEqual(show['indices'], {
            'info': 'imdb',
            'episodes': None,
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt1234',
        })


        # it should be possible to set both the index and the external
        # value to None.        
        response = self.patch('/1/shows/{}'.format(show_id), {
            'indices':{
                'info': None,
            },
            'externals': {
                'imdb': None,
            }
        })
        show = utils.json_loads(response.body)      
        self.assertEqual(response.code, 200, response.body)
        self.assertEqual(show['indices'], {
            'info': None,
            'episodes': None,
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': None,
        })

    def test_external(self):
        show_id = self.new_show()

        response = self.patch('/1/shows/{}'.format(show_id), {
            'externals': {
                'imdb': 'tt1234',
                'seplis_old': '1234',
            }
        })
        self.assertEqual(response.code, 200, response.body)

        response = self.get('/1/shows/externals/imdb/tt1234')
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['id'], show_id)

        response = self.get('/1/shows/externals/seplis_old/1234')
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['id'], show_id)

        # Let's try to get a show that does not have a
        # external id associated with it.
        response = self.get('/1/shows/externals/imdb/404')
        self.assertEqual(response.code, 404)


        # make sure that removing a external id results in it
        # not being found again.
        response = self.patch('/1/shows/{}'.format(show_id), {
            'externals': {
                'imdb': None,
            }
        })
        self.assertEqual(response.code, 200, response.body)

        response = self.get('/1/shows/externals/imdb/tt1234')
        self.assertEqual(response.code, 404)        

        # with the other external id it should still be possible
        # to get the show.
        response = self.get('/1/shows/externals/seplis_old/1234')
        self.assertEqual(response.code, 200)

    def test_externals_int_id(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'externals': {
                'imdb': 'tt1234',
                'seplis_old': 1234,
            },            
            'indices': {
                'info': 'imdb',
                'episodes': 'seplis_old',
            }
        })
        self.assertEqual(response.code, 400, response.body)

    def test_episodes(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'description': {
                        'text': 'Test description.'
                    }
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)

        self.get('http://{}/episodes/_refresh'.format(
            config['elasticsearch']
        ))
        response = self.get('/1/shows/{}/episodes'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 1, response.body)

    def test_search(self):
        show_id1 = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id1), {
            'title': 'This is a test show',
            'premiered': '2013-01-01',
        })
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/{}'.format(show_id1))        
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'This is a test show')

        show_id2 = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id2), {
            'title': 'Test show',
            'premiered': '2014-01-01',
        })
        self.assertEqual(response.code, 200)

        self.get('http://{}/shows/_refresh'.format(
            config['elasticsearch']
        ))
 
        response = self.get('/1/shows', {
            'q': 'this is a',
        })
        self.assertEqual(response.code, 200)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0]['title'], 'This is a test show')

    def test_search_errors(self):
        # there is no shows
        response = self.get('/1/shows/999999')
        self.assertEqual(response.code, 404, response.body)
        # wrong sort
        response = self.get('/1/shows?sort=a')
        self.assertEqual(response.code, 400, response.body)

    def test_description(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'NCIS',
            'description': None,
            'premiered': '2003-01-01',
            'ended': None,
            'indices': {
                'info': 'imdb',
                'episodes': 'imdb',
            },
            'externals': {
                'imdb': 'tt0364845',
            },
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'description': None,
                }
            ],
        })        
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'NCIS')

    def test_unknown_show(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.get('/1/shows/999999')
        self.assertEqual(response.code, 404, response.body)

    def test_season_count(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'description': {
                        'text': 'Test description.'
                    }
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['seasons'], [])

        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'season': 1,
                    'episode': 1,
                },
                {
                    'number': 2,
                    'season': 1,
                    'episode': 2,
                },
                {
                    'number': 3,
                    'season': 2,
                    'episode': 1,
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['seasons'], [
            {'total': 2, 'season': 1, 'to': 2, 'from': 1}, 
            {'total': 1, 'season': 2, 'to': 3, 'from': 3},
        ])

    def test_item_list_updates(self):
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'alternate_titles': [
                'test',
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternate_titles'])

        # append and duplicate
        response = self.patch('/1/shows/{}'.format(show_id), {
            'alternate_titles': [
                'test',
                'test2'
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternate_titles'])
        self.assertTrue('test2' in show['alternate_titles'])        

        response = self.patch('/1/shows/{}'.format(show_id), {
            'alternate_titles': [
                'test',
                'test',
                'test2'
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternate_titles'])
        self.assertTrue('test2' in show['alternate_titles'])

    def test_empty_lists(self):
        self.login(constants.LEVEL_EDIT_SHOW) 
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'title': 'test'
        })
        self.assertEqual(response.code, 200, response.body)
        
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['genres'], [])
        self.assertEqual(show['alternate_titles'], [])
        self.assertEqual(show['seasons'], [])

    def test_fan(self):        
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'test show',
            'status': 1,
            'episodes': [
                {
                    'number': 1,
                }
            ]
        })
        self.assertEqual(response.code, 201)
        show = utils.json_loads(response.body)
        show_id = show['id']
        self.get('http://{}/shows/_refresh'.format(
            config['elasticsearch']
        ))

        # Let's become a fan of the show
        for i in [1,2]:
            response = self.put('/1/shows/{}/fans/{}'.format(show_id, self.current_user.id))
            self.assertEqual(response.code, 200, response.body)
            response = self.get('/1/shows/{}?append=is_fan'.format(show_id))
            self.assertEqual(response.code, 200)
            show = utils.json_loads(response.body)
            self.assertEqual(show['fans'], 1)
            self.assertEqual(show['is_fan'], True)

        # Let's test that we haven't overwritten any essential data.
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertTrue('title' in show)
        self.assertEqual(show['title'], 'test show')

        # Let's check that we can find the user in the shows fan
        # list.
        response = self.get('/1/shows/{}/fans'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        fans = utils.json_loads(response.body)
        self.assertEqual(fans[0]['id'], self.current_user.id)

        # Let's check that we can find the show in the users
        # fan of list.
        response = self.get('/1/users/{}/fan-of'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        fan_of = utils.json_loads(response.body)
        self.assertEqual(fan_of[0]['id'], show_id)
        self.assertEqual(fan_of[0]['user_watching'], None)

        # When searching for fans we should be able to append the is_fan field.
        response = self.get('/1/shows?q=id:{}&append=is_fan'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(shows[0]['id'], show_id)
        self.assertEqual(shows[0]['is_fan'], True)

        # Let's watch a part of an episode and see if it shows up
        # in the user_watching field.
        response = self.put('/1/users/{}/watched/shows/{}/episodes/{}'.format(
            self.current_user.id,
            show_id,
            1
        ), {
            'position': 120,
            'times': 0,
        })
        self.assertEqual(response.code, 200)        
        response = self.get('/1/users/{}/fan-of'.format(self.current_user.id))
        self.assertEqual(response.code, 200, response.body)
        fan_of = utils.json_loads(response.body)
        self.assertEqual(fan_of[0]['id'], show_id)
        self.assertEqual(fan_of[0]['user_watching']['position'], 120)
        self.assertEqual(fan_of[0]['user_watching']['episode']['number'], 1)

        # Now unfan the show
        for i in [1,2]:
            response = self.delete('/1/shows/{}/fans/{}'.format(
                show_id,
                self.current_user.id
            ))
            self.assertEqual(response.code, 200, response.body)        
            response = self.get('/1/shows/{}'.format(show_id))
            self.assertEqual(response.code, 200)
            show = utils.json_loads(response.body)
            self.assertEqual(show['fans'], 0)


        # Let's test that we haven't overwritten any essential data.
        response = self.get('/1/shows/{}'.format(show_id))
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertTrue('title' in show)
        self.assertEqual(show['title'], 'test show')

    def test_add_image(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows/1/images', {
            'external_name': 'Test',
            'external_id': '1',
            'source_title': 'Test',
            'source_url': 'http://example.net',
            'type': constants.IMAGE_TYPE_POSTER,
        })
        self.assertEqual(response.code, 200)
        image = utils.json_loads(response.body)

        # we need to fake that an image has been uploaded
        with new_session() as session:
            session.query(models.Image).filter(
                models.Image.id == image['id'],
            ).update({
                'hash': '17fb3ee9dac3969819af794c1fd11fbd0e02ca3d0e86b9f0c0365f13fa27d225'
            })
            session.commit()

        response = self.post('/1/shows', {
            'title': 'test show',
            'status': 1,
            'poster_image_id': image['id']
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['poster_image']['id'], image['id'])

        # remove the image
        response = self.put('/1/shows/{}'.format(show['id']), {
            'poster_image_id': None
        })
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['poster_image'], None)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
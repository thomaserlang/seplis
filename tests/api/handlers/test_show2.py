# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis import utils
from seplis.config import config
from datetime import datetime, date
import time

class test_show(Testbase):

    def test_post(self):
        self.login(0)

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
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt0364845',
        })

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
        response = self.patch('/1/shows/{}'.format(show_id))
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
            'episodes': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt0364845',
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
        self.assertEqual(error['code'], 4001)


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

        # lets try to get a show that does not have a
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
        self.login(0)
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

    def test_description(self):
        self.login(0)
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
            ]
        })        
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'NCIS')

    def test_unknown_show(self):
        self.login(0)
        response = self.get('/1/shows/999999')
        self.assertEqual(response.code, 404)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
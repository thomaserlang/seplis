from seplis.api.testbase import Testbase, run_file
from seplis import utils, config
from seplis.api import constants, models
from seplis.api.decorators import new_session

class test_show(Testbase):

    def test_post(self):
        self.login(constants.LEVEL_EDIT_SHOW)

        # Creating a new show without any data is OK.
        response = self.post('/1/shows')
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)

        # this should be a successfully creation of a new show
        response = self.post('/1/shows', {
            'title': 'QWERTY',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service. \_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
                'title': 'IMDb',
                'url': 'http://www.imdb.com/title/tt123456799/',
            },
            'premiered': '2003-01-01',
            'ended': None,
            'importers': {
                'info': 'imdb',
                'episodes': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
            },
            'genres': [
                'Action',
                'Thriller',
            ],
            'alternative_titles': [
                'QWERTY 2',
                'QWERTY 3',
            ],
            'runtime': 40,
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'QWERTY')
        self.assertEqual(show['description'], {
            'text': 'The cases of the Naval Criminal Investigative Service. \_(ʘ_ʘ)_/ "\'<!--/*༼ つ ◕_◕ ༽つ',
            'title': 'IMDb',
            'url': 'http://www.imdb.com/title/tt123456799/',
        })
        self.assertEqual(show['premiered'], '2003-01-01')
        self.assertEqual(show['ended'], None)
        self.assertEqual(show['importers'], {
            'info': 'imdb',
            'episodes': 'imdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt123456799',
        })
        self.assertTrue('Action' in show['genres'])
        self.assertTrue('Thriller' in show['genres'])
        self.assertTrue('QWERTY 2' in show['alternative_titles'])
        self.assertTrue('QWERTY 3' in show['alternative_titles'])
        self.assertEqual(show['runtime'], 40)
        self.assertEqual(
            show['episode_type'], 
            constants.SHOW_EPISODE_TYPE_SEASON_EPISODE
        )

    def test_patch(self):
        show_id = self.new_show()
        response = self.patch('/1/series/{}'.format(show_id), {
            'title': 'QWERTY',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service.',
            },
            'premiered': '2003-01-01',
            'importers': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
            },
            'episode_type': constants.SHOW_EPISODE_TYPE_AIR_DATE,
        })
        self.assertEqual(response.code, 200, response.body)
        response = self.patch('/1/shows/{}'.format(show_id), {
            'importers': {
                'episodes': 'imdb'
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'QWERTY')
        self.assertEqual(show['description'], {
            'text': 'The cases of the Naval Criminal Investigative Service.',
            'title': None,
            'url': None,
        })
        self.assertEqual(show['premiered'], '2003-01-01')
        self.assertEqual(show['ended'], None)
        self.assertEqual(show['importers'], {
            'info': 'imdb',
            'episodes': 'imdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt123456799',
        })
        self.assertEqual(
            show['episode_type'], 
            constants.SHOW_EPISODE_TYPE_AIR_DATE
        )

    def test_put(self):
        show_id = self.new_show()
        response = self.put('/1/shows/{}'.format(show_id), {
            'title': 'QWERTY',
            'description': {
                'text': 'The cases of the Naval Criminal Investigative Service.',
            },
            'premiered': '2003-01-01',
            'importers': {
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
            },
            'episode_type': constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
        })

        self.assertEqual(response.code, 200, response.body)
        response = self.put('/1/shows/{}'.format(show_id), {
            'importers': {
                'episodes': 'thetvdb',
            },
            'externals': {
                'thetvdb': '1234',
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertEqual(show['title'], 'QWERTY')
        self.assertEqual(show['importers'], {
            'info': None,
            'episodes': 'thetvdb',
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'thetvdb': '1234',
        })
        self.assertEqual(
            show['episode_type'], 
            constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
        )

    def test_importers(self):
        show_id = self.new_show()
        response = self.get('/1/shows/{}'.format(show_id))
        # it should not be possible to add a importer without it exists as
        # an external.
        response = self.patch('/1/shows/{}'.format(show_id), {
            'importers':{
                'info': 'imdb',
            }
        })
        self.assertEqual(response.code, 400, response.body)
        error = utils.json_loads(response.body)
        self.assertEqual(error['code'], 1401)


        # so when adding the importer to the externals with a value
        # it should be OK.
        response = self.patch('/1/shows/{}'.format(show_id), {
            'importers':{
                'info': 'imdb',
            },
            'externals': {
                'imdb': 'tt1234',
            }
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)        
        self.assertEqual(show['importers'], {
            'info': 'imdb',
            'episodes': None,
            'images': None,
        })
        self.assertEqual(show['externals'], {
            'imdb': 'tt1234',
        })


        # it should be possible to set both the importer and the external
        # value to None.        
        response = self.patch('/1/shows/{}'.format(show_id), {
            'importers':{
                'info': None,
            },
            'externals': {
                'imdb': None,
            }
        })
        show = utils.json_loads(response.body)      
        self.assertEqual(response.code, 200, response.body)
        self.assertEqual(show['importers'], {
            'info': None,
            'episodes': None,
            'images': None,
        })
        self.assertEqual(show['externals'], {})

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

        # check that we can do the with two shows
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'externals': {
                'imdb': 'tt12345',
                'seplis_old': '12345',
            }
        })
        self.assertEqual(response.code, 200, response.body)
        response = self.get('/1/shows/externals/imdb/tt12345')
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['id'], show_id)

        # check that we can't duplicate a external id
        show_id = self.new_show()
        response = self.patch('/1/shows/{}'.format(show_id), {
            'externals': {
                'imdb': 'tt12345',
                'seplis_old': '12345',
            }
        })
        self.assertEqual(response.code, 400, response.body)

    def test_externals_int_id(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'externals': {
                'imdb': 'tt1234',
                'seplis_old': 1234,
            },            
            'importers': {
                'info': 'imdb',
                'episodes': 'seplis_old',
            }
        })
        self.assertEqual(response.code, 201, response.body)

    def test_episode_type(self):
        show_id = self.new_show()
        response = self.put('/1/shows/{}'.format(show_id), {
            'episode_type': constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
        })
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)        
        self.assertEqual(
            show['episode_type'], 
            constants.SHOW_EPISODE_TYPE_ABSOLUTE_NUMBER,
        )

        # test wrong episode type
        response = self.put('/1/shows/{}'.format(show_id), {
            'episode_type': 999,
        })
        self.assertEqual(response.code, 400)

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


        self.refresh_es()

        response = self.get('/1/shows/{}/episodes'.format(show_id))
        self.assertEqual(response.code, 200, response.body)
        episodes = utils.json_loads(response.body)
        self.assertEqual(len(episodes), 1, response.body)


        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 0',
                    'season': 0,
                }
            ]
        })
        self.assertEqual(response.code, 400, response.body)
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 0',
                    'episode': 0,
                }
            ]
        })
        self.assertEqual(response.code, 400, response.body)

        # Allow season and episode None
        response = self.patch('/1/shows/{}'.format(show_id), {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 0',
                    'season': None,
                    'episode': None,
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)


    def test_delete(self):
        show_id = self.new_show()
        response = self.patch(f'/1/shows/{show_id}', {
            'episodes': [
                {
                    'number': 1,
                    'title': 'Episode 1',
                    'air_date': '2014-01-01',
                    'description': {
                        'text': 'Test description.'
                    }
                },
                {
                    'number': 2,
                    'title': 'Episode 2',
                    'air_date': '2014-01-01',
                    'description': {
                        'text': 'Test description.'
                    }
                }
            ]
        })
        self.assertEqual(response.code, 200, response.body)

        response = self.delete(f'/1/shows/{show_id}')
        self.assertEqual(response.code, 204)

        self.refresh_es()

        response = self.get(
            f'{config.data.api.elasticsearch}/episodes/_doc/{show_id}-1'
        )
        self.assertEqual(response.code, 404)

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

        self.refresh_es()
 
        response = self.get('/1/shows', {
            'q': 'this is a',
        })
        self.assertEqual(response.code, 200, response.body)
        shows = utils.json_loads(response.body)
        self.assertEqual(len(shows), 1)
        self.assertEqual(shows[0]['title'], 'This is a test show')

    def test_search_errors(self):
        # there is no shows
        response = self.get('/1/shows/999999')
        self.assertEqual(response.code, 404, response.body)

    def test_description(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'QWERTY',
            'description': None,
            'premiered': '2003-01-01',
            'ended': None,
            'importers': {
                'info': 'imdb',
                'episodes': 'imdb',
            },
            'externals': {
                'imdb': 'tt123456799',
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
        self.assertEqual(show['title'], 'QWERTY')

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
            'alternative_titles': [
                'test',
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternative_titles'])

        # append and duplicate
        response = self.patch('/1/shows/{}'.format(show_id), {
            'alternative_titles': [
                'test',
                'test2'
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternative_titles'])
        self.assertTrue('test2' in show['alternative_titles'])        

        response = self.patch('/1/shows/{}'.format(show_id), {
            'alternative_titles': [
                'test',
                'test',
                'test2'
            ],
        })
        self.assertEqual(response.code, 200, response.body)
        show = utils.json_loads(response.body)
        self.assertTrue('test' in show['alternative_titles'])
        self.assertTrue('test2' in show['alternative_titles'])

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
        self.assertEqual(show['alternative_titles'], [])
        self.assertEqual(show['seasons'], [])

    def _test_fan_count(self, expected_count):        
        response = self.get('/1/users/{}/stats'.format(self.current_user.id))
        self.assertEqual(response.code, 200)
        stats = utils.json_loads(response.body)
        self.assertEqual(stats['fan_of'], expected_count)

    def test_add_image(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows/1/images', {
            'external_name': 'Test',
            'external_id': '1',
            'source_title': 'Test',
            'source_url': 'http://example.net',
            'type': constants.IMAGE_TYPE_POSTER,
        })
        self.assertEqual(response.code, 200, response.body)
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

        # when retrieving the show the poster image must be there.
        response = self.get('/1/shows/{}'.format(show['id']))
        self.assertEqual(response.code, 200)        
        show = utils.json_loads(response.body)
        self.assertEqual(show['poster_image']['id'], image['id'])

        # remove the image
        response = self.put('/1/shows/{}'.format(show['id']), {
            'poster_image_id': None
        })
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['poster_image'], None)

        # add the image again
        response = self.put('/1/shows/{}'.format(show['id']), {
            'poster_image_id': image['id']
        })
        self.assertEqual(response.code, 200)
        show = utils.json_loads(response.body)
        self.assertEqual(show['poster_image']['id'], image['id'])

    def test_search_title(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        response = self.post('/1/shows', {
            'title': 'This is a test show',
            'alternative_titles': [
                'kurt 1',
            ]
        })
        self.assertEqual(response.code, 201, response.body)
        show = utils.json_loads(response.body)
        self.refresh_es()

        # Test that lowercase does not matter
        response = self.get('/1/shows', {'q': 'this'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)

        # Test that both title and alternative_titles is searched in
        response = self.get('/1/shows', {'q': 'kurt'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)

        # Test ascii folding
        response = self.get('/1/shows', {'q': 'kùrt'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1)


        # Test apostrophe
        response = self.post('/1/shows', {
            'title': 'DC\'s legend of something',
            'alternative_titles': [
                'DC’s kurt',
            ]
        })
        self.assertEqual(response.code, 201, response.body)
        show2 = utils.json_loads(response.body)
        self.refresh_es()

        response = self.get('/1/shows', {'q': 'dc\'s'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/shows', {'q': 'dc’s'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/shows', {'q': 'dcs'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        response = self.get('/1/shows', {'q': '"dcs kurt"'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        response = self.get('/1/shows', {'q': '"dc’s kurt"'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(data[0]['id'], show2['id'])
        response = self.get('/1/shows', {'q': 'dc'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 0, data)

        # Test dotted search
        response = self.get('/1/shows', {'q': 'dcs.legend.of.something'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)
        self.assertEqual(data[0]['id'], show2['id'])

        # Test score
        # Searching for "dcs legend of something" should not return
        # "Test DC's legend of something" as the first result
        response = self.post('/1/shows', {
            'title': 'Test DCs legend of something',
        })
        self.assertEqual(response.code, 201, response.body)
        show3 = utils.json_loads(response.body)
        response = self.post('/1/shows', {
            'title': 'legend',
        })
        self.assertEqual(response.code, 201, response.body)
        show3 = utils.json_loads(response.body)
        self.refresh_es()

        response = self.get('/1/shows', {'title': 'dc\'s legend of something'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 2, data)
        self.assertEqual(data[0]['id'], show2['id'], data)


        # Test the walking dead
        with new_session() as session:
            session.query(models.Series).delete()
            session.commit()
        response = self.post('/1/shows', {
            'title': 'The Walking Dead',
            'premiered': '2010-10-31',
        })
        self.assertEqual(response.code, 201, response.body)
        response = self.post('/1/shows', {
            'title': 'Fear the Walking Dead',
            'premiered': '2015-08-23',
        })
        self.assertEqual(response.code, 201, response.body)
        self.refresh_es()
        response = self.get('/1/shows', {'title': 'The Walking Dead'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 2, data)
        self.assertEqual(data[0]['title'], 'The Walking Dead')


        # Test `&` and `and`
        response = self.post('/1/shows', {
            'title': 'Test & Test',
            'premiered': '2010-10-31',
        })
        self.assertEqual(response.code, 201, response.body)
        self.refresh_es()
        response = self.get('/1/shows', {'title': 'Test and Test'})
        self.assertEqual(response.code, 200, response.body)
        data = utils.json_loads(response.body)
        self.assertEqual(len(data), 1, data)


if __name__ == '__main__':
    run_file(__file__)
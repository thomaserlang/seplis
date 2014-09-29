import logging
from datetime import datetime
from seplis.web.handlers import base
from seplis import utils, constants
from seplis.web.client import API_error
from seplis.api import exceptions
from tornado import gen, escape
from tornado.web import HTTPError, authenticated

class Handler(base.Handler):

    @gen.coroutine
    def get(self, show_id):
        show = yield self.get_show(show_id)

        selected_season, episodes = yield self.get_season_episodes(show)
        next_episode = yield self.get_next_episode(show_id)
        if next_episode and \
            not self.get_argument('season', None) and \
                selected_season != next_episode['season']:
            selected_season = next_episode['season']
        self.render(
            'show.html',
            title=show['title'],
            show=show,
            episodes=episodes,
            selected_season=selected_season,
            next_episode=next_episode,
        )

    @gen.coroutine
    def get_show(self, show_id):        
        if self.current_user:
            show = yield self.client.get('/shows/{}?append=is_fan'.format(show_id))
        else:
            show = yield self.client.get('/shows/{}'.format(show_id))
        if not show:
            raise HTTPError(404, 'Unknown show')
        return show

    @gen.coroutine
    def get_season_episodes(self, show):
        selected_season = None
        _ss = int(self.get_argument('season', 0))
        if 'seasons' in show and show['seasons']:
            for season in show['seasons']:
                season = season
                if season['season'] == _ss:
                    break
            selected_season = season['season']
            req = {
                'q': 'number:[{} TO {}]'.format(
                    season['from'],
                    season['to'],
                ),
                'sort': 'number:desc',
            }
            if self.current_user:
                req['append'] = 'user_watched'
            episodes = yield self.client.get(
                '/shows/{}/episodes'.format(show['id']),
                req
            )
            return (selected_season, episodes)
        return (None, [])

    @gen.coroutine
    def get_next_episode(self, show_id):
        req = {
            'q': 'air_date:[{} TO *]'.format(datetime.utcnow().date()),
            'per_page': 1,
            'sort': 'number:asc',
        }
        if self.current_user:
            req['append'] = 'user_watched'
        episodes = yield self.client.get(
            '/shows/{}/episodes'.format(show_id),
            req
        )
        if episodes:
            return episodes[0]

class Redirect_handler(base.Handler_unauthenticated):

    @gen.coroutine
    def get(self, show_id):        
        show = yield self.client.get('/shows/{}'.format(show_id))
        if not show:
            raise HTTPError(404, 'Unknown show')
        self.redirect('/show/{}/{}{}'.format(
            show_id,
            utils.slugify(show['title']),
            '?'+utils.url_encode_tornado_arguments(self.request.arguments) \
                if self.request.arguments else '',
        ))

class API_fan_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        show_id = self.get_argument('show_id')
        do = self.get_argument('do')
        if do == 'fan':
            yield self.client.put('/shows/{}/fans/{}'.format(
                show_id,
                self.current_user['id'],
            ))
        elif do == 'unfan':            
            yield self.client.delete('/shows/{}/fans/{}'.format(
                show_id,
                self.current_user['id'],
            ))
        else:
            self.set_status(400)
        self.write_object({})

class API_watched_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        show_id = self.get_argument('show_id')
        number = self.get_argument('number')
        do = self.get_argument('do')

        if do == 'delete':
            yield self.client.delete('/users/{}/watched/shows/{}/episodes/{}'.format(
                self.current_user['id'],
                show_id,
                number,
            ))
        else:
            times = 1 if do == 'incr' else -1
            yield self.client.put('/users/{}/watched/shows/{}/episodes/{}'.format(
                self.current_user['id'],
                show_id,
                number,
            ), {
                'times': times,
                'position': 0,
            })
        self.write_object({})

class New_handler(base.Handler):

    @authenticated
    def get(self):
        self.render('show_edit.html',
            title='New show',
            show=None,
        )

class API_new_handler(base.API_handler):

    @gen.coroutine
    def post(self):
        data = self.build_data()
        show = yield self.client.post('/shows', data)
        yield self.client.post('/shows/{}/update'.format(show['id']))
        self.write_object(show)

    def build_data(self):
        imdb = self.get_argument('imdb')
        for name in constants.EXTERNAL_REQUIRED_TYPES:
            check = self.get_argument(name)
            if not check:
               raise API_error(400, None, '{} ID is missing or invalid'.format(
                    constants.EXTERNAL_TYPE_NAMES[name]
                )) 
        externals = {name: self.get_argument(name) \
            for name in constants.EXTERNAL_TYPES \
                if self.get_argument(name, None)}
        indices = {name: self.get_argument(name) \
            for name, externals in constants.INDEX_TYPES \
                if self.get_argument(name, None)}
        return {
            'externals': externals,
            'indices': indices,
        }

class Edit_handler(Handler):

    @authenticated
    @gen.coroutine
    def get(self, show_id):
        show = yield self.get_show(show_id)
        self.render('show_edit.html',
            title='Edit show',
            show=show,
        )

class API_edit_handler(API_new_handler):

    @gen.coroutine
    def post(self, show_id):
        data = self.build_data()
        show = yield self.client.put('/shows/{}'.format(show_id), data)
        if not show:
            raise exceptions.Show_unknow()
        yield self.client.post('/shows/{}/update'.format(show_id))
        self.write_object(show)
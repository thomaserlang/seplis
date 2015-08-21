import logging
from datetime import datetime
from seplis.web.handlers import base
from seplis import utils, constants
from seplis.web.client import API_error
from seplis.api import exceptions
from tornado import gen
from tornado.web import HTTPError, authenticated

class Handler(base.Handler):

    @gen.coroutine
    def get(self, show_id):
        show = yield self.get_show(show_id)        
        next_to_air = yield self.get_next_to_air(show['id'])
        next_episode = next_to_air[0] if next_to_air else None
        selected_season = None
        if not self.get_argument('season', None):
            if 'user_watching' in show and show['user_watching']:
                selected_season = show['user_watching']['episode']['season']
            elif next_episode:
                selected_season = next_episode['season']        
        selected_season, episodes = yield self.get_season_episodes(
            show,
            season=selected_season,
        )
        self.render(
            'show/show.html',
            title=show['title'],
            show=show,
            episodes=episodes,
            selected_season=selected_season,
            next_episode=next_episode,
            next_to_air=next_to_air,
        )

    @gen.coroutine
    def get_show(self, show_id):        
        if self.current_user:
            show = yield self.client.get('/shows/{}'.format(show_id), {
                'append': 'is_fan,user_watching',
            })
        else:
            show = yield self.client.get('/shows/{}'.format(show_id))
        if not show:
            raise HTTPError(404, 'Unknown show')
        return show

    @gen.coroutine
    def get_season_episodes(self, show, season=None):
        selected_season = None
        _ss = int(self.get_argument('season', 0)) or season
        req = {}
        if self.current_user:
            req['append'] = 'user_watched'
        if not show.get('seasons'):
            episodes = yield self.client.get(
                '/shows/{}/episodes'.format(show['id']),
                req,
            )
            return (None, episodes)
        for season in show['seasons']:
            season = season
            if season['season'] == _ss:
                break
        selected_season = season['season']
        req.update({
            'q': 'number:[{} TO {}]'.format(
                season['from'],
                season['to'],
            ),
            'sort': 'number:asc',
            'per_page': 50,
        })
        episodes = yield self.client.get(
            '/shows/{}/episodes'.format(show['id']),
            req
        )
        episodes = yield episodes.all_async()
        return (selected_season, episodes)

    @gen.coroutine
    def get_next_to_air(self, show_id, per_page=5):
        episodes = yield self.client.get(
            '/shows/{}/episodes'.format(show_id),
            {                
                'q': 'air_date:[{} TO *]'.format(datetime.utcnow().date()),
                'per_page': per_page,
                'sort': 'number:asc',
            }
        )
        return episodes

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

class API_get_play_now(base.API_handler):

    @authenticated
    @gen.coroutine
    def get(self):        
        show_id = self.get_argument('show_id')
        show = yield self.client.get('/shows/{}'.format(show_id),{
            'fields': 'id',
            'append': 'user_watching',
        })
        if not show:
            raise HTTPError(404, 'show not found')
        episode = yield self.get_play_episode(show)
        self.write_object(
            episode
        )

    @gen.coroutine
    def get_watching(self, show_id, from_number):
        episodes = yield self.client.get('/shows/{}/episodes'.format(show_id),
            {
                'q': 'number:[{} TO {}]'.format(
                    from_number,
                    from_number+1,
                ),
                'append': 'user_watched',
            }
        )
        return episodes

    @gen.coroutine
    def get_play_episode(self, show):
        number = (show.get('user_watching') or {}).get('episode', {}).get('number') or 1
        episodes = yield self.get_watching(show['id'], number)
        if not episodes:
            raise HTTPError(404, 'no episodes')
        episode1 = episodes[0]
        if not episode1['user_watched']:
            return episode1
        if episode1['user_watched']['position'] > 0:
            return episode1
        if len(episodes) != 2:
            raise HTTPError(404, 'no more episodes to watch')
        episode2 = episodes[1]
        if episode2['user_watched']:
            episode2['user_watched']['position'] = 0
        return episode2

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
        from_ = self.get_argument('from', None)
        if from_:
            to = self.get_argument('to')
        else:
            number = self.get_argument('number')
        do = self.get_argument('do')

        if do == 'delete':
            if not from_:
                yield self.client.delete('/users/{}/watched/shows/{}/episodes/{}'.format(
                    self.current_user['id'],
                    show_id,
                    number,
                ))
            else:
                yield self.client.delete('/users/{}/watched/shows/{}/episodes/{}-{}'.format(
                    self.current_user['id'],
                    show_id,
                    from_,
                    to,
                ))
        else:
            times = 1 if do == 'incr' else -1
            data = {
                'times': times,
            }
            if not from_:
                yield self.client.put('/users/{}/watched/shows/{}/episodes/{}'.format(
                    self.current_user['id'],
                    show_id,
                    number,
                ), data)
            else:
                yield self.client.put('/users/{}/watched/shows/{}/episodes/{}-{}'.format(
                    self.current_user['id'],
                    show_id,
                    from_,
                    to,
                ), data)

        self.write_object({})

class New_handler(base.Handler):

    @authenticated
    def get(self):
        self.render('show/show_edit.html',
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
        alternative_titles = set(filter(None, self.get_argument(
            'alternative_titles', 
            ''
        ).split(',')))
        episode_type = int(self.get_argument('episode_type'))
        return {
            'externals': externals,
            'indices': indices,
            'alternative_titles': alternative_titles,
            'episode_type': episode_type,
        }

class Edit_handler(Handler):

    @authenticated
    @gen.coroutine
    def get(self, show_id):
        show = yield self.get_show(show_id)
        self.render('show/show_edit.html',
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

class Fan_of_handler(base.Handler):

    @authenticated
    @gen.coroutine
    def get(self):
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'title.raw:asc')
        shows = yield self.client.get('/users/{}/fan-of'.format(
            self.current_user['id'],
        ), {
            'sort': sort,
            'page': page,
            'per_page': 50,
        })
        if shows.count == 0:
            yield self.show_empty()
        else:
            layout = self.get_cookie('layout', 'grid')
            temp = 'fan_of_list.html' if layout == 'list' \
                else 'fan_of.html'
            self.render(temp,
                title='Fan of',
                shows=shows,
                current_page=page,
            )

    @gen.coroutine
    def show_empty(self):
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'fans:desc')
        shows = yield self.client.get('/shows'.format(
            self.current_user['id'],
        ), {
            'sort': sort,
            'page': page,
            'per_page': 12,
        })
        self.render('fan_of_empty.html',
            title='Fan of',
            shows=shows,
            current_page=page,
        )

class Index_handler(base.Handler):

    @gen.coroutine
    def get(self):
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'fans:desc')
        shows = yield self.client.get('/shows', {
            'sort': sort,
            'page': page,
            'per_page': 50,
        })
        layout = self.get_cookie('layout', 'grid')
        temp = 'show_index_list.html' if layout == 'list' \
            else 'show_index.html'
        self.render(temp,
            title='Show index',
            shows=shows,
            current_page=page,
        )
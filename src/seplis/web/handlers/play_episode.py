import logging
from datetime import datetime
from seplis.web.handlers import base
from seplis import utils, constants, config
from seplis.web.client import API_error
from seplis.api import exceptions
from tornado import gen
from tornado.web import HTTPError, authenticated

class Handler(base.Handler):

    @authenticated
    @gen.coroutine
    def get(self, show_id, number):
        show = yield self.get_show(show_id)
        if not show:
            raise HTTPError(404, 'unknown show')
        episode, next_episode = yield self.get_episode_and_next(show_id, number)
        if not episode:
            raise HTTPError(404, 'unknown episode')
        play_servers = yield self.client.get('/shows/{}/episodes/{}/play-servers'.format(
            show_id,
            number,
        ))
        if not play_servers:
            self.render('play_episode/no_play_servers.html',
                show=show,
                episode=episode,
            )
            return
        self.render('play_episode/episode.html',
            show=show,
            show_json=utils.json_dumps(show),
            episode=episode,
            episode_json=utils.json_dumps(episode),
            play_servers=play_servers,
            next_episode=next_episode,
            chromecast_appid=config['play']['chromecast_appid'],
        )

    @gen.coroutine
    def get_show(self, show_id):
        show = yield self.client.get('/shows/{}'.format(show_id),{
            'fields': 'title',
        })
        return show

    @gen.coroutine
    def get_episode_and_next(self, show_id, number):
        episodes = yield self.client.get('/shows/{}/episodes'.format(
            show_id, 
        ), {
            'fields': 'title,number,season,episode',
            'append': 'user_watched',
            'q': 'number:[{} TO {}]'.format(
                number,
                int(number)+1
            )
        })
        if not episodes:
            return
        if episodes[0]['number'] != int(number):
            return
        return (
            episodes[0],
            episodes[1] if len(episodes) == 2 else None
        )

class API_watching_handler(base.API_handler):

    @authenticated
    @gen.coroutine
    def post(self):
        show_id = self.get_argument('show_id')
        number = self.get_argument('episode_number')
        position = int(self.get_argument('position'), 0)
        times = int(self.get_argument('times', 0))
        if times > 0:
            url = '/users/{}/watched/shows/{}/episodes/{}'
            data = { 
                'times': times,
            }
        else:
            url = '/users/{}/watching/shows/{}/episodes/{}'
            data = {
                'position': position,
            }
        yield self.client.put(url.format(
            self.current_user['id'],
            show_id,
            number,
        ), data)
        self.write('{}')
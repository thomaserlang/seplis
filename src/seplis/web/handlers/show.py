from seplis.web.handlers import base
from tornado import gen

class Handler(base.Handler_authenticated):

    @gen.coroutine
    def get(self, show_id=None):
        show = yield self.client.get('/shows/{}?append=following'.format(show_id))
        episodes = []
        selected_season = -1
        if 'seasons' in show:
            for season in show['seasons']:
                if season['season'] == int(self.get_argument('season', 0)):
                    break
            selected_season = season['season']
            episodes = yield self.client.get('/shows/{}/episodes?from={}&to={}'.format(
                show_id,
                season['from'],
                season['to'],
            ))
        self.render(
            'show.html',
            title='{} - SEPLIS'.format(show.get('title')),
            show=show,
            episodes=episodes,
            selected_season=selected_season,
        )

class Follow_handler(base.Handler_authenticated):

    @gen.coroutine
    def post(self):
        show_id = self.get_argument('show_id')
        do = self.get_argument('do')
        if do == 'follow':
            yield self.client.put('/shows/{}/follow'.format(show_id))
        elif do == 'unfollow':            
            yield self.client.delete('/shows/{}/follow'.format(show_id))
        else:
            self.set_status(400)
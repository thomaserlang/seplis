import tornado.web
import tornado.gen
import tornado.escape
from seplis import config, utils, Async_client
from seplis.play import models
from seplis.play.decorators import new_session
from sqlalchemy import desc

class Handler(tornado.web.RequestHandler):

    def get(self):
        with new_session() as session:
            shows = session.query(
                models.Show_id_lookup
            ).order_by(
                desc(models.Show_id_lookup.updated),
            ).all()
            self.render(
                'play_shows.html',
                shows=shows,
                config=config,
                url_escape=tornado.escape.url_escape
            )

    def post(self):
        set_default_headers(self)
        with new_session() as session:
            with session.no_autoflush:
                show = session.query(
                    models.Show_id_lookup,
                ).filter(
                    models.Show_id_lookup.file_show_title == \
                        self.get_argument('file_show_title')
                ).first()
                if not show:
                    raise tornado.web.HTTPError(404, 'show not found')
                old_show_id = show.show_id
                show.show_id = self.get_argument('show_id')            
                show.show_title = self.get_argument('show_title')
                if old_show_id:
                    count = session.query(
                        models.Show_id_lookup,
                    ).filter(
                        models.Show_id_lookup.show_id == old_show_id
                    ).count()
                    if count < 2:
                        session.query(
                            models.Episode_number_lookup,
                        ).filter(
                            models.Episode_number_lookup.show_id == old_show_id,
                        ).update({
                            'show_id': show.show_id,
                        })
                        session.query(
                            models.Episode,
                        ).filter(
                            models.Episode.show_id == old_show_id,
                        ).update({
                            'show_id': show.show_id,
                        })
                session.commit()
                self.write('{}')

class API_show_suggest_handler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        client = Async_client(config['client']['api_url'], version='1')
        set_default_headers(self)
        q = self.get_argument('q')
        shows = yield client.get('/shows', {
            'q': q,
            'fields': 'title,poster_image'
        })
        self.write(utils.json_dumps(shows))

def set_default_headers(self):
    self.set_header('Cache-Control', 'no-cache, must-revalidate')
    self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
    self.set_header('Content-Type', 'application/json')
    self.set_header('Access-Control-Allow-Origin', '*')
    self.set_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, X-Requested-With')
    self.set_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE')
    self.set_header('Access-Control-Expose-Headers', 'ETag, Link, X-Total-Count, X-Total-Pages')
    self.set_header('Access-Control-Max-Age', '86400')
    self.set_header('Access-Control-Allow-Credentials', 'true')
import sys
import inspect
from seplis import utils
from seplis.api import models
from seplis.api import elasticcreate
from seplis.connections import database, Database
from seplis.decorators import new_session, auto_pipe, auto_session
from sqlalchemy import func, or_
from datetime import datetime
from elasticsearch import helpers

class Rebuild_cache(object):

    def rebuild(self):
        print('Rebuilding cache/search data for:')
        sys.stdout.flush()
        database.redis.flushdb()
        elasticcreate.create_indices()
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name[:8] == 'rebuild_':
                print('... {}'.format(name[8:]))
                sys.stdout.flush()
                method()
        print('Done!')

    @auto_session
    @auto_pipe
    def rebuild_shows(self, session, pipe):
        from seplis.api.base.show import Show
        to_es = []
        for item in session.query(models.Show).yield_per(10000):
            a = Show._format_from_row(item)
            to_es.append({
                '_index': 'shows',
                '_type': 'show',
                '_id': a.id,
                '_source': utils.json_dumps(a),
            })
        helpers.bulk(database.es, to_es)

    @auto_session
    @auto_pipe
    def rebuild_fans(self, session, pipe):
        from seplis.api.base.show import Show        
        fans = session.query(models.Show_fan).all()
        for fan in fans:
            Show.cache_fan(
                show_id=fan.show_id,
                user_id=fan.user_id,
                pipe=pipe,
            )

    @auto_session
    def rebuild_episodes(self, session):
        from seplis.api.base.episode import Episode
        to_es = []
        for item in session.query(models.Episode).yield_per(10000):
            a = Episode._format_from_row(item)
            a.show_id = item.show_id
            to_es.append({
                '_index': 'episodes',
                '_type': 'episode',
                '_id': '{}-{}'.format(item.show_id, a.number),
                '_source': utils.json_dumps(a),
            })
        helpers.bulk(database.es, to_es)

    def rebuild_tags(self):
        from seplis.api.base.tag import Tag
        with new_session() as session:
            for tag in session.query(models.Tag).yield_per(10000):
                tag = Tag._format_from_query(tag)
                tag.cache()

    def rebuild_tag_relations_relations(self):
        from seplis.api.base.tag import User_tag_relation
        with new_session() as session:
            with database.redis.pipeline() as pipe:
                for rel in session.query(models.Tag_relation).yield_per(10000):
                    User_tag_relation.cache(
                        pipe=pipe,
                        user_id=rel.user_id,
                        tag_id=rel.tag_id,
                        tag_type=rel.type,
                        relation_id=rel.relation_id,
                    )
                pipe.execute()

    @auto_session
    @auto_pipe
    def rebuild_users(self, session, pipe):
        from seplis.api.base.user import User
        for user in session.query(models.User).yield_per(10000):
            user = User._format_from_query(user)
            user.cache(pipe=pipe)

    def rebuild_tokens(self):
        from seplis.api.base.user import Token
        with new_session() as session:
            pipe = database.redis.pipeline()
            for token in session.query(models.Token).filter(
                or_(
                    models.Token.expires >= datetime.now(),
                    models.Token.expires == None,
                )
            ).yield_per(10000):
                Token.cache(
                    user_id=token.user_id,
                    token=token.token,
                    expire_days=abs((datetime.now()-token.expires).days) if token.expires else None,
                    pipe=pipe,
                    user_level=token.user_level,
                )
            pipe.execute()

    @auto_session
    @auto_pipe
    def rebuild_watched(self, session, pipe):
        from seplis.api.base.episode import Watched
        usershows = []
        users = []
        for row in session.query(models.Episode_watched).yield_per(10000):
            Watched.cache_watched(
                user_id=row.user_id,
                show_id=row.show_id,
                number=row.episode_number,
                times=row.times,
                datetime_=row.datetime,
                position=row.position,
                pipe=pipe,
            )
            n = '{}-{}'.format(row.user_id, row.show_id)
            if n not in usershows:
                lw = Watched._get_latest_watched(
                    user_id=row.user_id,
                    show_id=row.show_id,
                    session=session,
                )
                Watched.cache_currently_watching(
                    user_id=row.user_id,
                    show_id=row.show_id,
                    number=lw.episode_number,
                    position=lw.position,
                    datetime_=lw.datetime,
                    pipe=pipe,
                )
                usershows.append(n)
                users.append(row.user_id)
        for user_id in set(users):
            Watched.cache_minutes_spent(user_id, session=session, pipe=pipe)

    @auto_session
    def rebuild_images(self, session):
        from seplis.api.base.image import Image
        to_es = []
        for image in session.query(models.Image).yield_per(10000):
            i = Image._format_from_row(image)
            to_es.append({
                '_index': 'images',
                '_type': 'image',
                '_id': i.id,
                '_source': i.__dict__,
            })
        helpers.bulk(database.es, to_es)

def main():
    Rebuild_cache().rebuild()
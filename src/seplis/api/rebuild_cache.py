import sys
import inspect
from seplis.api import models
from seplis.api import elasticcreate
from seplis.connections import database, Database
from seplis.decorators import new_session, auto_pipe, auto_session
from sqlalchemy import func, or_
from datetime import datetime

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
        shows = session.query(models.Show).filter(
            models.Show.status>0,
        ).all()        
        total = len(shows)
        i = 0   
        print('... ... {}/{}'.format(i, total))
        for show in shows:
            i += 1
            print('... ... {}/{}'.format(i, total))
            s = Show._format_from_row(show)
            s.save(session=session, pipe=pipe)
            sys.stdout.flush()

    @auto_session
    @auto_pipe
    def rebuild_fans(self, session, pipe):
        from seplis.api.base.show import Show        
        fans = session.query(models.Show_fan).all()
        for fan in fans:
            Show.cache_fan(
                show_id=follow.show_id,
                user_id=follow.user_id,
                pipe=pipe,
            )

    @auto_session
    def rebuild_episodes(self, session):
        from seplis.api.base.episode import Episode
        episodes = session.query(models.Episode).all()
        total = len(episodes)
        i = 0
        print('... ... {}/{}'.format(i, total))
        for episode in episodes:
            i += 1
            print('\r... ... {}/{}'.format(i, total))
            e = Episode._format_from_row(episode)
            e.to_elasticsearch(episode.show_id)
            sys.stdout.flush()

    def rebuild_tags(self):
        from seplis.api.base.tag import Tag
        with new_session() as session:
            tags = session.query(models.Tag).all()
            for tag in tags:
                tag = Tag._format_from_query(tag)
                tag.cache()

    def rebuild_tag_relations_relations(self):
        from seplis.api.base.tag import User_tag_relation
        with new_session() as session:
            relations = session.query(models.Tag_relation).all()
            with database.redis.pipeline() as pipe:
                for rel in relations:
                    User_tag_relation.cache(
                        pipe=pipe,
                        user_id=rel.user_id,
                        tag_id=rel.tag_id,
                        tag_type=rel.type,
                        relation_id=rel.relation_id,
                    )
                pipe.execute()

    def rebuild_users(self):
        from seplis.api.base.user import User
        with new_session() as session:
            users = session.query(models.User).all()
            pipe = database.redis.pipeline()
            for user in users:
                user = User._format_from_query(user)
                user.cache(pipe=pipe)
            pipe.execute()

    def rebuild_tokens(self):
        from seplis.api.base.user import Token
        with new_session() as session:
            tokens = session.query(models.Token).filter(
                or_(
                    models.Token.expires >= datetime.now(),
                    models.Token.expires == None,
                )
            ).all()
            pipe = database.redis.pipeline()
            for token in tokens:
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
        rows = session.query(
            models.Episode_watched,
        ).all()
        usershows = []
        for row in rows:
            Watched.cache(
                user_id=row.user_id,
                show_id=row.show_id,
                number=row.number,
                times=row.times,
                datetime=row.datetime,
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
                    session=session,
                    pipe=pipe,
                )
                usershows.append(n)

def main():
    Rebuild_cache().rebuild()
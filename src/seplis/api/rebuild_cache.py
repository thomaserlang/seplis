import sys
import inspect
from seplis.api import models
from seplis.api import elasticcreate
from seplis.connections import database, Database
from seplis.decorators import new_session
from sqlalchemy import func, or_
from datetime import datetime

class Rebuild_cache(object):

    def rebuild(self):
        print('Rebuilding cache/search data for:')
        sys.stdout.flush()
        database.redis.flushdb()
        database.es.indices.delete(index='_all')
        elasticcreate.create_indices()
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if name[:8] == 'rebuild_':
                print('... {}'.format(name[8:]))
                sys.stdout.flush()
                method()
        print('Done!')

    def rebuild_shows(self):
        from seplis.api.base.show import Show
        with new_session() as session:
            shows = session.query(models.Show).filter(
                models.Show.status>0,
            ).all()
            pipe = database.redis.pipeline()
            for show in shows:
                s = Show._format_from_row(show)
                s.save(session, pipe)
            pipe.execute()

    def rebuild_follow(self):
        from seplis.api.base.show import Follow        
        with new_session() as session:
            followers = session.query(models.Show_follow).all()
            for follow in followers:
                Follow.cache(
                    show_id=follow.show_id,
                    user_id=follow.user_id,
                )

    def rebuild_episodes(self):
        from seplis.api.base.show import Episode
        with new_session() as session:
            episodes = session.query(models.Episode).all()
            #pipe = database.redis.pipeline()
            for episode in episodes:
                e = Episode._format_from_row(episode)
                e.to_elasticsearch(episode.show_id)

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

def main():
    Rebuild_cache().rebuild()
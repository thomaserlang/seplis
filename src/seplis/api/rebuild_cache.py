from seplis.config import config
Config.load()
import sys
import inspect
from seplis.api import models
from seplis.api import elasticcreate
from seplis.connections import database
from seplis.decorators import new_session
from sqlalchemy import func
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
            shows = session.query(models.Show).all()
            pipe = database.redis.pipeline()
            for show in shows:
                if not show.data:
                    continue
                Show.cache(
                    pipe=pipe,
                    show_id=show.data['id'],
                    data=show.data,
                )
                Show.to_elasticsearch(
                    show_id=show.data['id'],
                    data=show.data
                )
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
            pipe = database.redis.pipeline()
            episodes_data = []
            for episode in episodes:
                if not episode.data:
                    continue
                episodes_data.append(episode.data)
                Episode.cache(
                    pipe=pipe,
                    show_id=episode.show_id,
                    number=episode.number,
                    data=episode.data,
                )
                episode.data['id'] = '{}-{}'.format(episode.data['show_id'], episode.data['number'])
            pipe.execute()
            if episodes_data:
                database.es.bulk(
                    body=episodes_data,
                    index='episodes',
                    doc_type='episode',
                )

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
                models.Token.expires >= datetime.now()
            ).all()
            pipe = database.redis.pipeline()
            for token in tokens:
                Token.cache(
                    user_id=token.user_id,
                    token=token.token,
                    expire_days=abs((datetime.now()-token.expires).days),
                    pipe=pipe,
                )
            pipe.execute()

if __name__ == '__main__':
    Rebuild_cache().rebuild()
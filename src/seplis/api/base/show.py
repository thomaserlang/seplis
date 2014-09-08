import urllib.parse
import logging
import copy
import time
from seplis.decorators import new_session, auto_session
from seplis.connections import database
from seplis import utils
from seplis.api.base.pagination import Pagination
from seplis.api.base.episode import Episode
from seplis.api.base.description import Description
from seplis.api import exceptions, constants, models
from datetime import datetime
from sqlalchemy import asc

class Show(object):

    def __init__(self, id, title, description, premiered, ended, 
                 externals, indices, status, runtime, genres,
                 alternate_titles, seasons, updated=None):
        '''

        :param id: int
        :param title: str
        :param description: `seplis.api.description.description()`
        :param premiered: `datetime.date()`
        :param ended: `datetime.date()`
        :param externals: `dict()`
            {
                'name': 'value1
            }
        :param indices: `dict()`
            {
                'index': 'value'
            }
        :param status: int
        :param runtime: int
        :param genres: list of str
        :param alternate_titles: list of str
        :param seasons: list of dict
        :param updated: datetime
        '''
        self.id = id
        self.title = title
        self.description = description
        self.premiered = premiered
        self.ended = ended
        if not externals:
            externals = {}
        self.externals = externals
        if not indices:
            indices = {}
        self.indices = indices
        self.status = status
        self.runtime = runtime
        self.genres = genres
        self.alternate_titles = alternate_titles
        self.seasons = seasons
        self.updated = updated

    def save(self, session=None, pipe=None):
        _pipe = pipe
        if not pipe:
            _pipe = database.redis.pipeline()
        if not session:
            with new_session() as session:
                self._save(session, _pipe)
                session.commit()
        else:            
            self._save(session, _pipe)
        if not pipe:
            _pipe.execute()

    def _save(self, session, pipe):
        self._check_index()
        self.updated = datetime.utcnow()
        session.query(
            models.Show,
        ).filter(
            models.Show.id == self.id,
        ).update({
            'title': self.title,
            'description_text': self.description.text,
            'description_title': self.description.title,
            'description_url': self.description.url,
            'premiered': self.premiered,
            'ended': self.ended,
            'index_info': self.indices.get('info') if self.indices else None,
            'index_episodes': self.indices.get('episodes') if self.indices else None,
            'externals': self.externals,
            'status': self.status,
            'runtime': self.runtime,
            'genres': self.genres,
            'alternate_titles': self.alternate_titles,
            'seasons': self.seasons,
            'updated': self.updated,
        })
        self.update_external(
            pipe=pipe,
            session=session,
            overwrite=True,
        )
        self.to_elasticsearch()

    @classmethod
    def _format_from_row(cls, row):
        if not row:
            return None
        return cls(
            id=row.id,
            title=row.title,
            description=Description(
                text=row.description_text,
                title=row.description_title,
                url=row.description_url,
            ),
            premiered=row.premiered,
            ended=row.ended,
            indices={
                'info': row.index_info,
                'episodes': row.index_episodes,
            },
            externals=row.externals if row.externals else {},
            status=row.status,
            runtime=row.runtime,
            genres=row.genres,
            alternate_titles=row.alternate_titles,
            seasons=row.seasons,
            updated=row.updated,
        )

    @classmethod
    def get(cls, id_, session=None):
        '''

        :param id_: int
        :param session: SQLAlchemy session
        :returns: `Show()`
        '''
        if not session:
            with new_session() as session:
                return cls._get(id_, session)
        else:
            return cls._get(id_, session)

    @classmethod
    def _get(cls, id_, session):
        show = session.query(
            models.Show,
        ).filter(
            models.Show.id == id_,
        ).first()
        if not show:
            return None
        return cls._format_from_row(show)

    @classmethod
    @auto_session
    def create(cls, session):        
        '''
        Creates a new show and returns the id.

        :param session: sqlalchemy session
        :returns: int
        '''
        show = models.Show(
            created=datetime.utcnow(),
        )
        session.add(show)
        session.flush()
        return show.id

    def to_dict(self):
        return self.__dict__

    def to_elasticsearch(self):
        '''

        :returns: boolean
        '''
        database.es.index(
            index='shows',
            doc_type='show',
            id=self.id,
            body=utils.json_dumps(self),
        )

    def _check_index(self):
        '''
        Checks that the index value is in the externals. 

        :param show: `Show()`
        :raises: `exceptions.Show_external_field_must_be_specified_exception()`
        :raises: `exceptions.Show_index_type_must_be_in_external_field_exception()`
        '''
        if not self.indices or not self.indices['info'] and not self.indices['episodes']:
            return
        if not self.externals:
            raise exceptions.Show_external_field_must_be_specified_exception()
        for key in self.indices:
            if (self.indices[key] != None) and \
               (self.indices[key] not in self.externals):
                raise exceptions.Show_index_type_must_be_in_external_field_exception(
                    self.indices[key]
                )

    @classmethod
    def _count_season_episodes(cls, session, show_id):
        '''
        Registers `from` and `to` episode numbers per season.
        '''
        episodes = session.query(
            models.Episode,
        ).filter(
            models.Episode.show_id == show_id,
        ).order_by(
            asc(models.Episode.number)
        ).all()
        if not episodes:
            return []
        seasons = []
        last_season = 1
        episode_start = 1
        episode_end = 1
        def update_season():
            seasons.append({
                'season': last_season,
                'from': episode_start,
                'to': episode_end,
                'total': (episode_end + 1) - episode_start,
            })
        for episode in episodes:
            season = episode.data.get('season', 1)
            if season != last_season:
                update_season()
                last_season = season
                episode_start = episode_end + 1
            episode_end = episode.data['number']
        update_season()
        return seasons

    @classmethod
    def update_episodes(cls, session, pipe, show_id, episodes, overwrite=False):
        '''
        
        :param show_id: int
        :param episodes: list of Episode
        '''
        ids = []
        if overwrite:
            pipe.delete('shows:{}:episodes'.format(show_id))
            session.query(
                models.Episode,
            ).filter(
                models.Episode.show_id == show_id,
            ).delete()
        for episode in episodes:
            Episode.update_with_session(
                session=session,
                pipe=pipe,
                show_id=show_id,
                **episode
            )
            ids.append(episode['number'])

    def update_external(self, session, pipe, overwrite=False):
        '''

        :param session: SQLAlchemy session
        :param pipe: Redis pipe
        :param overwrite: boolean
        '''
        if overwrite:
            externals_query = session.query(
                models.Show_external,
            ).filter(
                models.Show_external.show_id == self.id,
            ).all()
            for external in externals_query:
                name = 'shows:external:{}:{}'.format(
                    urllib.parse.quote(external.title),
                    urllib.parse.quote(external.value),
                )
                pipe.delete(name, self.id)
                session.delete(external)
        for key, value in self.externals.items():
            duplicate_show_id = self.get_id_by_external(key, value)
            if duplicate_show_id and (duplicate_show_id != self.id):
                raise exceptions.Show_external_duplicated(
                    external_title=key,
                    external_id=value,
                    show=self.get(duplicate_show_id),
                )
            external = models.Show_external(
                show_id=self.id,
                title=key,
                value=value,
            )
            self.cache_external(
                pipe=pipe,
                external_title=key,
                external_id=value,
                show_id=self.id,
            )
            session.merge(external)

    @classmethod
    def cache_external(cls, pipe, external_title, external_id, show_id):
        if not external_id or not external_title:
            return
        name = 'shows:external:{}:{}'.format(
            urllib.parse.quote(external_title),
            urllib.parse.quote(external_id),
        )
        pipe.set(name, show_id)

    @classmethod
    def get_id_by_external(cls, external_title, external_id):
        '''

        :param external_title: str
        :param external_id: str
        '''
        if not external_id or not external_title:
            return
        name = 'shows:external:{}:{}'.format(
            urllib.parse.quote(external_title),
            urllib.parse.quote(external_id),
        )
        show_id = database.redis.get(name)
        if not show_id:
            return
        return int(show_id)

    @classmethod
    def following(cls, show_id, user_id):
        '''
        Checks if a user is following a show.

        :param show_id: int
        :param user_id: int
        :returns: boolean
        '''
        return database.redis.sismember(
            name='users:{}:follows'.format(user_id),
            value=show_id,
        )
    
class Shows(object):

    @classmethod
    def get(cls, ids):
        pipe = database.redis.pipeline()
        for id_ in ids:
            pipe.get('shows:{}:data'.format(id_))
            pipe.hget('shows:{}'.format(id_), 'followers')
        items = pipe.execute()
        items = zip(
            items[::2], # show data
            items[1::2], # followers
        )
        shows = []
        for show, followers in items:
            show = utils.json_loads(show)
            show['followers'] = int(followers) if followers else 0
            shows.append(show)
        return shows

    @classmethod
    def follows(cls, user_id, page=1, per_page=constants.per_page):
        name = 'users:{}:follows'.format(user_id)
        pipe = database.redis.pipeline()
        pipe.scard(name)
        pipe.sort(
            name=name,
            start=(page - 1) * per_page,
            num=per_page,
            by='shows:*->title',
            alpha=True,
        )
        total_count, show_ids = pipe.execute()
        return Pagination(
            page=page,
            per_page=per_page,
            total=total_count,
            records=cls.get(show_ids),
        )

class Follow(object):

    @classmethod
    def cache(cls, show_id, user_id):
        '''
        Returns `true` if the data did not exist in the cache.

        :param show_id: int
        :param user_id: int
        :returns: boolean
        '''        
        user_id = int(user_id)
        show_id = int(show_id)
        pipe = database.redis.pipeline()
        pipe.zadd('shows:{}:followers'.format(show_id), time.time(), user_id)
        pipe.sadd('users:{}:follows'.format(user_id), show_id)
        response = pipe.execute()
        changed = True if response[1] else False
        if not changed:
            return changed
        pipe.hincrby('shows:{}'.format(show_id), 'followers', 1)
        pipe.hincrby('users:{}'.format(show_id), 'follows', 1)
        pipe.execute()
        return True

    @classmethod
    def follow(cls, show_id, user_id):
        if not cls.cache(show_id, user_id):
            return True
        with new_session() as session:
            follow = models.Show_follow(
                show_id=show_id,
                user_id=user_id,
            )
            session.merge(follow)
            session.commit()
        return True

class Unfollow(object):

    @classmethod
    def cache(cls, show_id, user_id):
        '''
        Returns `true` if the data did not exist in the cache.

        :param show_id: int
        :param user_id: int
        :returns: boolean
        '''        
        user_id = int(user_id)
        show_id = int(show_id)
        pipe = database.redis.pipeline()
        pipe.zrem('shows:{}:followers'.format(show_id), user_id)
        pipe.srem('users:{}:follows'.format(user_id), show_id)
        response = pipe.execute()
        changed = True if response[0] or response[1] else False
        if not changed:
            return changed
        if response[0]:
            pipe.hincrby('shows:{}'.format(show_id), 'followers', -1)
        if response[1]:
            pipe.hincrby('users:{}'.format(show_id), 'follows', -1)
        pipe.execute()
        return True

    @classmethod
    def unfollow(cls, show_id, user_id):
        if not cls.cache(show_id, user_id):
            return True
        with new_session() as session:
            follow = session.query(
                models.Show_follow,
            ).filter(
                models.Show_follow.show_id == show_id,
                models.Show_follow.user_id == user_id,
            ).delete()
            session.commit()
        return True
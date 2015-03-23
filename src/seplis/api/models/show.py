import logging
import sqlalchemy as sa
from .base import Base
from sqlalchemy import event, orm
from sqlalchemy.orm.attributes import get_history, flag_modified
from seplis.utils import JSONEncodedDict
from seplis import utils
from seplis.api.connections import database
from seplis.api import constants, exceptions, rebuild_cache
from seplis.api.decorators import new_session
from datetime import datetime

class Show(Base):
    __tablename__ = 'shows'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, onupdate=datetime.utcnow)
    status = sa.Column(sa.Integer, default=0, nullable=False)
    fans = sa.Column(sa.Integer, default=0)

    title = sa.Column(sa.String(200), unique=True)
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    premiered = sa.Column(sa.Date)
    ended = sa.Column(sa.Date)
    externals = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_dict)
    index_info = sa.Column(sa.String(45))
    index_episodes = sa.Column(sa.String(45))
    index_images = sa.Column(sa.String(45))
    seasons = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    runtime = sa.Column(sa.Integer)
    genres = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    alternative_titles = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = orm.relationship('Image', lazy='joined')
    episode_type = sa.Column(
        sa.Integer, 
        default=constants.SHOW_EPISODE_TYPE_SEASON_EPISODE,
    )
 
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': {
                'text': self.description_text,
                'title': self.description_title,
                'url': self.description_url,
            },
            'premiered': self.premiered,
            'ended': self.ended,
            'indices': self.serialize_indices(),
            'externals': self.externals if self.externals else {},
            'status': self.status,
            'runtime': self.runtime,
            'genres': self.genres if self.genres else [],
            'alternative_titles': self.alternative_titles if \
                self.alternative_titles else [],
            'seasons': self.seasons if self.seasons else [],
            'fans': self.fans,
            'updated': self.updated,
            'poster_image': self.poster_image.serialize() \
                if self.poster_image_id else None,
            'episode_type': self.episode_type,
        }

    def serialize_indices(self):
        return {
            'info': self.index_info,
            'episodes': self.index_episodes,
            'images': self.index_images,
        }

    def to_elasticsearch(self):
        '''Sends the show's info to ES.

        This method is automatically called after update or insert.
        '''
        if not self.id:
            raise Exception('can\'t add the show to ES without an ID.')        
        session = orm.Session.object_session(self)
        session.es_bulk.append({
            '_index': 'shows',
            '_type': 'show',
            '_id': self.id,
            '_source': utils.json_dumps(self.serialize()),
        })

    def before_upsert(self):
        self.check_indices()
        if get_history(self, 'externals').has_changes():
            self.cleanup_externals()        

    def after_upsert(self):
        if get_history(self, 'externals').has_changes():
            self.update_externals()
        self.to_elasticsearch()

    def update_externals(self):
        '''Saves the shows externals to the database and the cache.
        Checks for duplicates.

        This method must be called when the show's externals has 
        been modified.

        :raises: exceptions.Show_external_duplicated()
        '''
        session = orm.Session.object_session(self)
        externals_query = session.query(
            Show_external,
        ).filter(
            Show_external.show_id == self.id,
        ).all()
        # delete externals where the relation has been removed.
        for external in externals_query:
            if not self.externals or (external.title not in self.externals):
                session.delete(external)
        # update the externals. Raises an exception when there is a another
        # show with a relation to the external.
        if not self.externals:
            return
        for title, value in self.externals.items():
            duplicate_show_id = self.show_id_by_external(title, value)
            if duplicate_show_id and (duplicate_show_id != self.id):
                raise exceptions.Show_external_duplicated(
                    external_title=title,
                    external_value=value,
                    show=session.query(Show).get(duplicate_show_id).serialize(),
                )
            external = None
            for ex in externals_query:
                if title == ex.title:
                    external = ex
                    break
            if not external:
                external = Show_external()
                session.add(external)
            external.title = title
            external.value = value
            external.show_id = self.id

    def cleanup_externals(self):
        '''Removes externals with None as value.'''
        popkeys = [key for key, value in self.externals.items() \
            if not value]
        if popkeys:
            for k in popkeys:
                self.externals.pop(k)

    def update_seasons(self):
        '''Counts the number of episodes per season.
        Sets the value in the variable `self.seasons`.

        Must be called if one or more episodes for the show has
        been added/edited/deleted.

            [
                {
                    'season': 1,
                    'from': 1,
                    'to': 22,
                    'total': 22,
                },
                {
                    'season': 2,
                    'from': 23,
                    'to': 44,
                    'total': 22,
                }
            ]
        '''
        session = orm.Session.object_session(self)
        rows = session.execute('''
            SELECT 
                season,
                min(number) as `from`,
                max(number) as `to`,
                count(number) as total
            FROM
                episodes
            WHERE
                show_id = :show_id
            GROUP BY season;
        ''', {
            'show_id': self.id,
        })
        seasons = []
        for row in rows:
            if not row['season']:
                continue
            seasons.append({
                'season': row['season'],
                'from': row['from'],
                'to': row['to'],
                'total': row['total'],
            })
        self.seasons = seasons

    def check_indices(self):
        '''Checks that all the index values are registered as externals.

        :param show: `Show()`
        :raises: `exceptions.Show_external_field_missing()`
        :raises: `exceptions.Show_index_type_not_in_external()`
        '''
        indices = self.serialize_indices()
        if not indices or not any(indices.values()):
            return
        if not self.externals:
            raise exceptions.Show_external_field_missing()
        for key in indices:
            if (indices[key] != None) and \
               (indices[key] not in self.externals):
                raise exceptions.Show_index_type_not_in_external(
                    indices[key]
                )

    @classmethod
    def show_id_by_external(self, external_title, external_value):
        '''

        :returns: int
        '''
        if not external_value or not external_title:
            return
        show_id = database.redis.get(Show_external.format_cache_key(
            external_title,
            external_value,
        ))
        if not show_id:
            return
        return int(show_id)

    def become_fan(self, user_id):
        session = orm.Session.object_session(self)
        if database.redis.sismember(
                Show_fan._show_cache_name.format(self.id),
                user_id
            ):
            return
        fan = Show_fan(
            show_id=self.id,
            user_id=user_id,
        )
        session.add(fan)

    def unfan(self, user_id):
        session = orm.Session.object_session(self)
        fan = session.query(Show_fan).filter(
            Show_fan.show_id == self.id,
            Show_fan.user_id == user_id,
        ).first()
        if not fan:
            return
        session.delete(fan)


class Show_fan(Base):
    __tablename__ = 'show_fans'

    show_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('shows.id'), 
        primary_key=True, 
        autoincrement=False,
    )
    user_id = sa.Column(
        sa.Integer, 
        sa.ForeignKey('users.id'),
        primary_key=True, 
        autoincrement=False,
    )

    _show_cache_name = 'shows:{}:fans'
    _user_cache_name = 'users:{}:fan_of'

    def cache(self):
        session = orm.Session.object_session(self)
        session.pipe.sadd(self.show_cache_name, self.user_id)
        session.pipe.sadd(self.user_cache_name, self.show_id)

    @property
    def show_cache_name(self):
        return self._show_cache_name.format(self.show_id)

    @property
    def user_cache_name(self):
        return self._user_cache_name.format(self.user_id)

    def incr_fan(self, amount):
        '''Increments the fans/fan of counter for the user and the show.
        Automatically called on insert and delete.

        :param amount: int
        '''
        session = orm.Session.object_session(self)
        session.pipe.hincrby('shows:{}'.format(self.show_id), 'fans', amount)
        session.pipe.hincrby('users:{}:stats'.format(self.user_id), 'fan_of', amount)
        session.es_bulk.append({
            '_op_type': 'update',
            '_index': 'shows',
            '_type': 'show',
            '_retry_on_conflict': 3,
            '_id': self.show_id,
            'script': 'ctx._source.fans += {}'.format(amount),
        })
        session.execute(Show.__table__.update()\
            .where(Show.__table__.c.id==self.show_id)\
            .values(fans=Show.__table__.c.fans + amount)
        )
        from seplis.api.models import User
        session.execute(User.__table__.update()\
            .where(User.__table__.c.id == self.user_id)\
            .values(fan_of=User.__table__.c.fan_of + amount)
        )

    def after_upsert(self):
        self.cache()
        self.incr_fan(1)

    def after_delete(self):
        session = orm.Session.object_session(self)
        session.pipe.srem(self.show_cache_name, self.user_id)
        session.pipe.srem(self.user_cache_name, self.show_id)
        self.incr_fan(-1)

    @classmethod
    def is_fan(cls, user_id, show_id):
        '''Check if the user is a fan of one or more shows.

        :param user_id: int
        :param show_id: int or list of int
        :returns: bool or list of bool
        '''
        ids = show_id if isinstance(show_id, list) else [show_id]
        pipe = database.redis.pipeline()
        for id_ in ids:
            pipe.sismember(cls._show_cache_name.format(id_), user_id)
        result = pipe.execute()
        return result if isinstance(show_id, list) else result[0]

class Show_external(Base):
    __tablename__ = 'show_externals'

    show_id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(45), primary_key=True)
    value = sa.Column(sa.String(45))
   
    cache_key = 'shows:external:{external_title}:{external_value}'

    @classmethod
    def format_cache_key(cls, external_title, external_value):
        import urllib.parse
        return cls.cache_key.format(
            external_title=urllib.parse.quote(external_title),
            external_value=urllib.parse.quote(external_value),
        )

    def cache(self):
        session = orm.Session.object_session(self)
        name = self.format_cache_key(
            self.title,
            self.value,
        )
        session.pipe.set(
            name, 
            self.show_id
        )

    def after_delete(self):
        session = orm.Session.object_session(self)
        if not self.title or not self.value:
            return
        name = self.format_cache_key(
            self.title,
            self.value,
        )
        session.pipe.delete(name)

    def after_upsert(self):
        '''Updates the cache for externals'''
        title_hist = get_history(self, 'title')
        value_hist = get_history(self, 'value')
        show_id = get_history(self, 'show_id')
        session = orm.Session.object_session(self)
        if title_hist.deleted or value_hist.deleted:
            title = title_hist.deleted[0] \
                if title_hist.deleted else self.title
            value = value_hist.deleted[0] \
                if value_hist.deleted else self.value
            if not title or not value:
                return
            name = Show_external.format_cache_key(
                title,
                value,
            )
            session.pipe.delete(name)
        if title_hist.added or value_hist.added or show_id.added:
            if not self.title or not self.value:
                return
            self.cache()


@rebuild_cache.register('shows')
def rebuild_shows():
    with new_session() as session:
        for item in session.query(Show).yield_per(10000):
            item.to_elasticsearch()
        session.commit()

@rebuild_cache.register('show_fans')
def rebuild_fans():
    with new_session() as session: 
        for item in session.query(Show_fan).yield_per(10000):
            item.cache()
        session.commit()

@rebuild_cache.register('show_externals')
def rebuild_externals():
    with new_session() as session: 
        for item in session.query(Show_external).yield_per(10000):
            item.cache()
        session.commit()


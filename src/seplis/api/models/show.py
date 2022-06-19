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

    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, onupdate=datetime.utcnow)
    status = sa.Column(sa.Integer, default=0, nullable=False)
    fans = sa.Column(sa.Integer, default=0)

    title = sa.Column(sa.String(200), unique=True)
    description_text = sa.Column(sa.Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    premiered = sa.Column(sa.Date)
    ended = sa.Column(sa.Date)
    externals = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_dict)
    importer_info = sa.Column(sa.String(45))
    importer_episodes = sa.Column(sa.String(45))
    importer_images = sa.Column(sa.String(45))
    seasons = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    runtime = sa.Column(sa.Integer)
    genres = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    alternative_titles = sa.Column(JSONEncodedDict(), default=JSONEncodedDict.empty_list)
    poster_image_id = sa.Column(sa.Integer, sa.ForeignKey('images.id'))
    poster_image = orm.relationship('Image', lazy=False)
    episode_type = sa.Column(
        sa.Integer, 
        default=constants.SHOW_EPISODE_TYPE_SEASON_EPISODE,
    )
    total_episodes = sa.Column(sa.Integer, default=0)
    language = sa.Column(sa.String(100))
 
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title or '',
            'description': {
                'text': self.description_text,
                'title': self.description_title,
                'url': self.description_url,
            },
            'premiered': self.premiered,
            'ended': self.ended,
            'importers': self.serialize_importers(),
            'externals': self.externals if self.externals else {},
            'status': self.status,
            'runtime': self.runtime,
            'genres': self.genres if self.genres else [],
            'alternative_titles': self.alternative_titles if \
                self.alternative_titles else [],
            'seasons': self.seasons if self.seasons else [],
            'fans': self.fans,
            'updated_at': self.updated_at,
            'poster_image': self.poster_image.serialize() \
                if self.poster_image_id else None,
            'episode_type': self.episode_type,
            'total_episodes': self.total_episodes,
            'language': self.language,
        }

    def serialize_importers(self):
        return {
            'info': self.importer_info,
            'episodes': self.importer_episodes,
            'images': self.importer_images,
        }

    def to_elasticsearch(self):
        """Sends the show's info to ES.

        This method is automatically called after update or insert.
        """
        if not self.id:
            raise Exception('can\'t add the show to ES without an ID.')        
        self.session.es_bulk.append({
            '_index': 'shows',
            '_id': self.id,
            '_source': utils.json_dumps(self.serialize()),
        })
        at = [self.title, *self.alternative_titles]
        year = str(self.premiered.year) if self.premiered else ''
        for title in at[:]:
            if title and year not in title:
                t = f'{title} {year}'
                if t not in at:
                    at.append(t)
        self.session.es_bulk.append({
            '_index': 'titles',
            '_id': f'series-{self.id}',
            '_source': utils.json_dumps({ 
                'type': 'series',
                'id': self.id,
                'title': self.title,
                'titles': at,
                'premiered': self.premiered,
                'imdb': self.externals.get('imdb'),
                'poster_image': self.poster_image,
            }),
        })

    def before_upsert(self):
        self.check_importers()
        if get_history(self, 'externals').has_changes():
            self.cleanup_externals()    
            self.update_externals()          
        if get_history(self, 'genres').has_changes():
            self.update_genres()  

    def after_upsert(self):            
        self.to_elasticsearch()

    def before_delete(self):
        self.session.es_bulk.append({
            '_op_type': 'delete',
            '_index': 'shows',
            '_id': self.id,
        })
        self.session.es_bulk.append({
            '_op_type': 'delete',
            '_index': 'titles',
            '_id': f'series-{self.id}',
        })

        from . import Episode
        episodes = self.session.query(Episode).filter(
            Episode.show_id == self.id,
        ).all()
        for e in episodes:
            self.session.delete(e)

        externals = self.session.query(Show_external).filter(
            Show_external.show_id == self.id,
        ).all()
        for e in externals:
            self.session.delete(e)

        from . import Image
        images = self.session.query(Image).filter(
            Image.relation_type == 'show',
            Image.relation_id == self.id,
        ).all()
        for i in images:
            self.session.delete(i)

    def update_externals(self):
        """Saves the shows externals to the database and the cache.
        Checks for duplicates.

        This method must be called when the show's externals has 
        been modified.

        :raises: exceptions.Show_external_duplicated()
        """
        externals_query = self.session.query(
            Show_external,
        ).filter(
            Show_external.show_id == self.id,
        ).all()
        # delete externals where the relation has been removed.
        for external in externals_query:
            if not self.externals or (external.title not in self.externals):
                self.session.delete(external)
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
                    show=self.session.query(Show).get(duplicate_show_id).serialize(),
                )
            external = None
            for ex in externals_query:
                if title == ex.title:
                    external = ex
                    break
            if not external:
                external = Show_external()
                self.session.add(external)
            external.title = title
            external.value = value
            external.show_id = self.id

    def cleanup_externals(self):
        """Removes externals with None as value."""
        popkeys = [key for key, value in self.externals.items() \
            if not value]
        if popkeys:
            for k in popkeys:
                self.externals.pop(k)

    def update_seasons(self):
        """Counts the number of episodes per season.
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
        """
        rows = self.session.execute("""
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
        """, {
            'show_id': self.id,
        })
        seasons = []
        total_episodes = 0
        for row in rows:
            if not row['season']:
                continue
            total_episodes += row['total']
            seasons.append({
                'season': row['season'],
                'from': row['from'],
                'to': row['to'],
                'total': row['total'],
            })
        self.seasons = seasons
        self.total_episodes = total_episodes

    def update_genres(self):
        self.session.query(Show_genre).filter(
            Show_genre.show_id == self.id,
        ).delete()
        for genre in self.genres:
            self.session.add(Show_genre(
                show_id=self.id,
                genre=genre,
            ))

    def check_importers(self):
        """Checks that all the importer values is registered as externals.

        :param show: `Show()`
        :raises: `exceptions.Show_external_field_missing()`
        :raises: `exceptions.Show_importer_not_in_external()`
        """
        importers = self.serialize_importers()
        if not importers or not any(importers.values()):
            return
        if not self.externals:
            raise exceptions.Show_external_field_missing()
        for key in importers:
            if (importers[key] != None) and \
               (importers[key] not in self.externals):
                raise exceptions.Show_importer_not_in_external(
                    importers[key]
                )

    @classmethod
    def show_id_by_external(self, external_title, external_value):
        """

        :returns: int
        """
        if not external_value or not external_title:
            return
        show_id = database.redis.get(Show_external.format_cache_key(
            external_title,
            external_value,
        ))
        if not show_id:
            return
        return int(show_id)

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
        name = self.format_cache_key(
            self.title,
            self.value,
        )
        self.session.pipe.set(
            name, 
            self.show_id
        )

    def after_delete(self):
        if not self.title or not self.value:
            return
        name = self.format_cache_key(
            self.title,
            self.value,
        )
        self.session.pipe.delete(name)

    def after_upsert(self):
        """Updates the cache for externals"""
        title_hist = get_history(self, 'title')
        value_hist = get_history(self, 'value')
        show_id = get_history(self, 'show_id')
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
            self.session.pipe.delete(name)
        if title_hist.added or value_hist.added or show_id.added:
            if not self.title or not self.value:
                return
            self.cache()

class Show_genre(Base):
    __tablename__ = 'show_genres'

    show_id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    genre = sa.Column(sa.String(100), primary_key=True)

    def after_insert(self):
        self.session.execute('INSERT IGNORE INTO genres (genre) VALUES (:genre);', {
            'genre': self.genre,
        })

class Genre(Base):
    __tablename__ = 'genres'
    genre = sa.Column(sa.String(100), primary_key=True)

@rebuild_cache.register('shows')
def rebuild_shows():
    with new_session() as session:
        for item in session.query(Show).yield_per(10000):
            item.to_elasticsearch()
        session.commit()

@rebuild_cache.register('show_externals')
def rebuild_externals():
    with new_session() as session: 
        for item in session.query(Show_external).yield_per(10000):
            item.cache()
        session.commit()


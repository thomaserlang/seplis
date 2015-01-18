import sqlalchemy as sa
from sqlalchemy import event, orm
from sqlalchemy.orm.attributes import get_history
from seplis.models import JSONEncodedDict
from seplis.api.connections import database
from seplis.api import constants, exceptions
from seplis.api.decorators import auto_pipe
from seplis import utils

class Show(base):
    __tablename__ = 'shows'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    created = sa.Column(sa.DateTime)
    updated = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer, server_default='0', nullable=False)
    fans = sa.Column(sa.Integer, server_default='0')

    title = sa.Column(sa.String(200), unique=True)
    description_text = sa.Column(Text)
    description_title = sa.Column(sa.String(45))
    description_url = sa.Column(sa.String(200))
    premiered = sa.Column(Date)
    ended = sa.Column(Date)
    externals = sa.Column(JSONEncodedDict())
    index_info = sa.Column(sa.String(45))
    index_episodes = sa.Column(sa.String(45))
    index_images = sa.Column(sa.String(45))
    seasons = sa.Column(JSONEncodedDict())
    runtime = sa.Column(sa.Integer)
    genres = sa.Column(JSONEncodedDict())
    alternative_titles = sa.Column(JSONEncodedDict())
    poster_image_id = sa.Column(sa.Integer, ForeignKey('images.id'))
    poster_image = relationship('Image')
    episode_type = sa.Column(sa.Integer, server_default=str(constants.SHOW_EPISODE_TYPE_SEASON_EPISODE))

    _cache_key_show_external = 'shows:external:{external_title}:{external_value}'

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
            'indices': {
                'info': self.index_info,
                'episodes': self.index_episodes,
                'images': self.index_images,
            },
            'externals': self.externals if self.externals else {},
            'status': self.status,
            'runtime': self.runtime,
            'genres': self.genres if self.genres else [],
            'alternative_titles': self.alternative_titles if \
                self.alternative_titles else [],
            'seasons': self.seasons if self.seasons else [],
            'fans': self.fans,
            'updated': self.updated,
            #'poster_image': self.poster_image.serialize(),
            'episode_type': self.episode_type,
        }

    def to_elasticsearch(self):
        '''
        Sends the show's info to ES.

        This method is automatically called after update or insert.

        '''
        if not self.id:
            raise Exception('can\'t add the show to ES without an ID.')
        database.es.index(
            index='shows',
            doc_type='show',
            id=self.id,
            body=utils.json_dumps(self.serialize),
        )

    def update_externals(self):
        '''
        Saves the shows externals to the database and the cache.
        Checks for duplicates.

        This method is automatically called on update or insert
        if the show's externals has been modified.

        :raises: exceptions.Show_external_duplicated()
        '''
        session = orm.Session.object_session(self)
        externals_query = session.query(
            models.Show_external,
        ).filter(
            models.Show_external.show_id == self.id,
        ).all()
        # delete externals where the relation has been removed.
        for external in externals_query:
            name = self._format_cache_key_show_external(
                external_title,
                external_value,
            )
            if (external.title not in self.externals) or \
                self.externals[external.title] != external.value:
                pipe.delete(name, self.id)
            if external.title not in self.externals:
                session.delete(external)
        # update the externals. Raises an exception when there is a another
        # show with and relation to the external.
        for title, value in self.externals.items():
            duplicate_show_id = self.show_id_by_external(title, value)
            if duplicate_show_id and (duplicate_show_id != self.id):
                raise exceptions.Show_external_duplicated(
                    external_title=title,
                    external_value=value,
                    show=self.get(duplicate_show_id),
                )
            external = models.Show_external(
                show_id=self.id,
                title=title,
                value=value,
            )
            self.cache_external(
                pipe=pipe,
                external_title=title,
                external_value=value,
                show_id=self.id,
            )
            session.pipe.set(
                self._format_cache_key_show_external(title, value),
                self.id,
            )
            session.merge(external)

    @property
    def _format_cache_key_show_external(external_title, external_value):
        return self._cache_key_show_external.format(
            external_title=urllib.parse.quote(external_title),
            external_value=urllib.parse.quote(external_value),
        )

    @classmethod
    def show_id_by_external(self, external_title, external_value):
        '''

        :returns: int
        '''
        if not external_value or not external_title:
            return
        show_id = database.redis.get(self._format_cache_key_show_external(
            external_title,
            external_value,
        ))
        if not show_id:
            return
        return int(show_id)

@event.listens_for(Show, 'after_update')
@event.listens_for(Show, 'after_insert')
def _show_after(mapper, connection, target):
    if get_history(target, 'externals')[0] != ():
        target.update_externals()
    target.to_elasticsearch()

def show_episodes_per_season(show_id, session):
    '''
    Counts the number of episodes per season.
    From and to is the episode numbers for the season.

    :returns: list of dict
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
        'show_id': show_id,
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
    return seasons


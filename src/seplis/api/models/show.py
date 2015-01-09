import sqlalchemy as sa
from sqlalchemy import event
from seplis.models import JSONEncodedDict
from seplis.api.connections import database
from seplis.api import constants
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
        database.es.index(
            index='shows',
            doc_type='show',
            id=self.id,
            body=utils.json_dumps(self.serialize),
        )

def _show_before_update(mapper, connection, target):
    pass

def _show_after_update(mapper, connection, target):
    target.to_elasticsearch()

event.listen(Show, 'after_update', _after_update)


def _count_season_episodes(self, session=None):
    '''
    Counts number of episodes per season.

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
    return seasons


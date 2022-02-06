import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import event, orm
from .base import Base
from seplis import utils, config
from seplis.api import rebuild_cache
from seplis.api.decorators import new_session
from datetime import datetime

class Image(Base):
    __tablename__ = 'images'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    relation_type = sa.Column(sa.String(20))
    relation_id = sa.Column(sa.Integer)
    external_name = sa.Column(sa.String(50))
    external_id = sa.Column(sa.String(50))
    height = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    hash = sa.Column(sa.String(64))
    source_title = sa.Column(sa.String(200))
    source_url = sa.Column(sa.String(200))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    type = sa.Column(sa.Integer)

    def serialize(self):
        return {
            'id': self.id,
            'external_name': self.external_name,
            'external_id': self.external_id,
            'height': self.height,
            'width': self.width,
            'hash': self.hash,
            'source_url': self.source_url,
            'source_title': self.source_title,
            'type': self.type,
            'created_at': self.created_at,
            '_relation_type': self.relation_type,
            '_relation_id': self.relation_id,
            'url': config['api']['image_url'] + '/' + self.hash \
                if config['api']['image_url'] and self.hash else self.hash
        }

    def after_upsert(self):
        self.to_elasticsearch()

    def to_elasticsearch(self):
        '''Sends the image's info to ES.

        This method is automatically called after update and insert.
        '''
        if not self.id:
            raise Exception('can\'t add the show to ES without an ID.')
        session = orm.Session.object_session(self)
        session.es_bulk.append({
            '_index': 'images',
            '_id': self.id,
            '_source': utils.json_dumps(self.serialize()),
        })

    def after_delete(self):
        self.delete_from_elasticsearch()

    def delete_from_elasticsearch(self):
        '''Removes the image from ES.

        This method is automatically called after delete.
        '''
        session = orm.Session.object_session(self)
        session.es_bulk.append({
            '_op_type': 'delete',
            '_index': 'images',
            '_id': self.id,
        })


@rebuild_cache.register('images')
def rebuild_images():
    with new_session() as session:
        for item in session.query(Image).yield_per(10000):
            item.to_elasticsearch()
        session.commit()
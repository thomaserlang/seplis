from urllib.parse import urljoin
import sqlalchemy as sa
from .base import Base
from seplis import config
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
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    type = sa.Column(sa.String(50))

    @property
    def url(self):
        return urljoin(config.data.api.image_url, self.hash)
from seplis.decorators import auto_session, auto_pipe
from seplis.api import models, exceptions
from seplis.connections import database
from seplis import utils
from datetime import datetime

class Image(object):

    def __init__(self, id, relation_type, relation_id, external_name,
        external_id, height, width, hash, source_title, source_url, 
        datetime):
        self.id = id
        self.relation_type = relation_type
        self.relation_id = relation_id
        self.external_name = external_name
        self.external_id = external_id
        self.height = height
        self.width = width
        self.hash = hash
        self.source_title = source_title
        self.source_url = source_url
        self.datetime = datetime

    def to_dict(self):
        return self.__dict__

    @classmethod
    def _format_from_row(cls, row):
        if not row:
            return None
        return cls(**models.row_to_dict(row))

    @classmethod
    @auto_session
    def create(cls, relation_type, relation_id, session=None):
        '''

        :param relation_type: str
        :param relation_id: str
        :returns: `Image()`
        '''
        image = models.Image(
            relation_type=relation_type,
            relation_id=relation_id,
            datetime=datetime.utcnow(),
        )
        session.add(image)
        session.flush()
        return cls._format_from_row(image)

    @classmethod
    @auto_session
    def get(cls, id_, session=None):
        image = session.query(models.Image).get(id_)
        return cls._format_from_row(image)

    @classmethod
    @auto_session
    def _by_external(cls, name, id_, image_id, session=None):
        image = session.query(
            models.Image,
        ).filter(
            models.Image.external_name == name,
            models.Image.external_id == id_,
            models.Image.id != image_id,
        ).first()
        return cls._format_from_row(image)        

    @auto_session
    def save(self, session=None):
        image = self._by_external(
            name=self.external_name,
            id_=self.external_id,
            image_id=self.id,
        )
        if image:
            raise exceptions.Image_external_duplicate(image)
        session.query(
            models.Image,
        ).filter(
            models.Image.id == self.id,
        ).update(
            self.__dict__
        )
        self.to_elasticsearch()

    def to_elasticsearch(self):
        database.es.index(
            index='images',
            doc_type='image',
            id=self.id,
            body=utils.json_dumps(self),
        )

    @auto_session
    def delete(self, session=None):
        '''

        :returns: boolean
        '''
        image = session.query(
            models.Image,
        ).filter(
            models.Image.id == self.id,
        ).delete()
        database.es.delete(
            index='images',
            doc_type='image',
            id=self.id,
        )
        if not image:
            return False
        return True
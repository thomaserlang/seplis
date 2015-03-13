import logging
from tornado import gen, concurrent
from seplis import schemas, utils
from seplis.api.handlers import base, file_upload
from seplis.api import constants, models, exceptions
from seplis.api.decorators import authenticated, new_session
from seplis.api.base.pagination import Pagination
from seplis.api.models import Image

class Handler(base.Handler):

    def initialize(self, relation_type=None):
        super(Handler, self).initialize()
        self.relation_type = relation_type

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def post(self, relation_id):
        if not self.relation_type:
            raise Exception('relation_type missing')
        image = yield self._post(relation_id)
        self.write_object(image)

    @concurrent.run_on_executor
    def _post(self, relation_id):
        data = self.validate(schemas.Schema(schemas.Image, required=True))  
        with new_session() as session:
            image = Image()
            image.relation_type = self.relation_type
            image.relation_id = relation_id
            session.add(image)
            self.update_model(image, data)
            session.commit()
            return image.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)    
    @gen.coroutine
    def put(self, relation_id, image_id):
        image = yield self._put(image_id)
        self.write_object(image)

    @concurrent.run_on_executor
    def _put(self, image_id):
        data = self.validate(schemas.Schema(schemas.Image, required=False))
        with new_session() as session:
            image = session.query(Image).get(image_id)
            if not image:
                raise exceptions.Image_unknown()
            self.update_model(image, data)
            session.commit()
            return image.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)    
    @gen.coroutine
    def delete(self, relation_id, image_id):
        yield self._delete(image_id)

    @concurrent.run_on_executor
    def _delete(self, image_id):
        with new_session() as session:
            image = session.query(Image).get(image_id)
            if not image:
                raise exceptions.Image_unknown()
            session.delete(image)
            session.commit()

    @gen.coroutine
    def get(self, relation_id, image_id=None):
        if image_id:
            yield self.get_image(image_id)
        else:
            yield self.get_images(relation_id)

    @gen.coroutine
    def get_image(self, image_id):
        result = yield self.es('/images/image/{}'.format(
            image_id,
        ))
        if not result['found']:
            raise exceptions.Not_found('the image was not found')
        self.write_object(
            self.image_wrapper(
                result['_source']
            )
        )

    @gen.coroutine
    def get_images(self, relation_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'id:asc')
        body = {
            'filter': {
                'and': [
                    {
                        'term': {
                            '_relation_type': self.relation_type,
                        }
                    },
                    {
                        'term': {
                            '_relation_id': int(relation_id),
                        }
                    },
                ]
                                
            }
        }
        if q:
            body.update({
                'query': {
                    'query_string': {
                        'query': q,
                    }
                }
            })
        result = yield self.es(
            '/images/image/_search',
            query={
                'from': ((page - 1) * per_page),
                'size': per_page,
                'sort': sort,
            },           
            body=body,
        )
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total'],
            records=[d['_source'] for d in result['hits']['hits']],
        )
        self.write_object(p)

class Data_handler(file_upload.Handler):

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def put(self, relation_id, image_id):
        files = yield self.save_files()
        if not files:
            raise exceptions.File_upload_no_files()
        yield self._put(image_id, files)

    @concurrent.run_on_executor
    def _put(self, image_id, files):
        with new_session() as session:
            image = session.query(Image).get(image_id)
            if not image:
                raise exceptions.Image_unknown()
            if files[0]['type'] != 'image':
                raise exceptions.File_upload_unrecognized_image()
            image.hash = files[0]['hash']
            image.width = files[0]['width']
            image.height = files[0]['height']
            session.commit()
import logging
from tornado import gen, web
from seplis import schemas, utils
from seplis.api.handlers import base, file_upload
from seplis.api import constants, models, exceptions
from seplis.api.decorators import authenticated
from seplis.api.base.pagination import Pagination
from seplis.api.base.image import Image

class Handler(base.Handler):

    def initialize(self, relation_type=None):
        super(Handler, self).initialize()
        self.relation_type = relation_type

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def post(self, relation_id):
        if not self.relation_type:
            raise Exception('relation_type missing')
        data = self.validate(schemas.Schema(schemas.Image, required=True))
        image = Image.create(self.relation_type, relation_id)
        image.__dict__.update(data)
        image.save()        
        self.write_object(
            self.image_format(image.to_dict())
        )

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def put(self, relation_id, image_id):        
        data = self.validate(schemas.Schema(schemas.Image, required=False))
        image = Image.get(image_id)
        if not image:
            raise exceptions.Image_unknown()
        image.__dict__.update(data)
        image.save()        
        self.write_object(
            image
        )

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def delete(self, relation_id, image_id):
        image = Image.get(image_id)
        if not image:
            raise exceptions.Image_unknown()
        image.delete()

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
            self.image_format(
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
                'term': {
                    'relation_type': self.relation_type,
                    'relation_id': relation_id,
                }
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
            records=self.image_format(
                [d['_source'] for d in result['hits']['hits']]
            ),
        )
        self.write_object(p)

class Data_handler(file_upload.Handler):

    @authenticated(constants.LEVEL_EDIT_SHOW)
    @gen.coroutine
    def put(self, relation_id, image_id):
        image = Image.get(image_id)
        if not image:
            raise exceptions.Not_found('the image was not found')
        files = yield self.save_files()
        if not files:
            raise exceptions.File_upload_no_files()
        if files[0]['type'] != 'image':
            raise exceptions.File_upload_unrecognized_image()
        image.hash = files[0]['hash']
        image.width = files[0]['width']
        image.height = files[0]['height']
        image.save()
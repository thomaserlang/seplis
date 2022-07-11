import logging
import elasticsearch
from tornado import gen, concurrent
from seplis import schemas, utils
from seplis.api.connections import database
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
    async def post(self, relation_id):
        if not self.relation_type:
            raise Exception('relation_type missing')
        image = await self._post(relation_id)
        self.write_object(image)

    @concurrent.run_on_executor
    def _post(self, relation_id):
        logging.info(self.request.body)
        data = self.validate(schemas.Image_required)  
        with new_session() as session:
            image = Image()
            image.relation_type = self.relation_type
            image.relation_id = relation_id
            session.add(image)
            self.update_model(image, data)
            session.commit()
            return image.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def put(self, relation_id, image_id):
        image = await self._put(image_id)
        self.write_object(image)

    @concurrent.run_on_executor
    def _put(self, image_id):
        data = self.validate(schemas.Image_optional)
        with new_session() as session:
            image = session.query(Image).get(image_id)
            if not image:
                raise exceptions.Image_unknown()
            self.update_model(image, data)
            session.commit()
            return image.serialize()

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def delete(self, relation_id, image_id):
        await self._delete(image_id)

    @concurrent.run_on_executor
    def _delete(self, image_id):
        with new_session() as session:
            image = session.query(Image).get(image_id)
            if not image:
                raise exceptions.Image_unknown()
            session.delete(image)
            session.commit()

    async def get(self, relation_id, image_id=None):
        if image_id:
            await self.get_image(image_id)
        else:
            await self.get_images(relation_id)

    async def get_image(self, image_id):
        try:
            result = await database.es_async.get(
                index='images',
                id=image_id,
            )
        except elasticsearch.NotFoundError:
            raise exceptions.Not_found('the image was not found')
        self.write_object(
            self.image_wrapper(
                result['_source']
            )
        )

    async def get_images(self, relation_id):
        q = self.get_argument('q', None)
        per_page = int(self.get_argument('per_page', constants.PER_PAGE))
        page = int(self.get_argument('page', 1))
        sort = self.get_argument('sort', 'id:asc')
        query = {
            'bool': {
                'must': [
                    {'term': {'_relation_type': self.relation_type}},
                    {'term': {'_relation_id': int(relation_id)}},
                ]
            }     
        }
        if q:
            query['bool']['must'].append({
                'query_string': {
                    'default_field': 'title',
                    'query': q,
                }
            })
        result = await database.es_async.search(
            index='images',
            query=query,
            from_=((page - 1) * per_page),
            size=per_page,
            sort=sort,
        )
        p = Pagination(
            page=page,
            per_page=per_page,
            total=result['hits']['total']['value'],
            records=[d['_source'] for d in result['hits']['hits']],
        )
        self.write_object(p)

class Data_handler(file_upload.Handler):
    ASPECT_RATIO = (0.67, 0.68)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    async def put(self, relation_id, image_id):
        files = await self.save_files()
        if not files:
            raise exceptions.File_upload_no_files()
        await self._put(image_id, files)

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
            if image.type == constants.IMAGE_TYPE_POSTER:
                if round(image.width/image.height, 2) not in self.ASPECT_RATIO:
                    raise exceptions.Image_wrong_size(self.ASPECT_RATIO)
            session.commit()
import logging
from tornado import gen
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
        image = Image.create(self.relation_type, relation_id)
        self.update_image(image)
        self.write_image(image)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def put(self, relation_id, image_id):        
        data = self.validate(schemas.Image)
        image = Image.get(image_id)
        if not image:
            raise exceptions.Image_unknown()
        self.update_image(image)
        self.write_image(image)

    @authenticated(constants.LEVEL_EDIT_SHOW)
    def delete(self, relation_id, image_id):
        image = Image.get(image_id)
        if not image:
            raise exceptions.Image_unknown()
        image.delete()

    def get(self, relation_id, image_id):
        image = Image.get(image_id)
        if not image:
            raise exceptions.Not_found('the image was not found')
        self.write_image(image)

    def update_image(self, image):
        data = self.validate(schemas.Image)
        image.external_name = data['external_name']
        image.external_id = data['external_id']
        image.source_title = data['source_title']
        image.source_url = data['source_url']
        image.save()

    remove_keys = (
        'relation_type',
        'relation_id',
    )

    def write_image(self, images):
        '''
        :param images: `Image()` or list of `Image()`
        '''
        if isinstance(images, list):
            for img in images:
                utils.keys_to_remove(
                    self.remove_keys,
                    img.to_dict()
                )
        else:
            utils.keys_to_remove(
                self.remove_keys,
                images.to_dict()
            )
        self.write_object(images)

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
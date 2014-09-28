# coding=UTF-8
import json
import nose
from io import BytesIO
from mock import Mock, patch, MagicMock
from seplis.api.testbase import Testbase
from seplis import utils
from seplis.config import config
from seplis.api import constants
from datetime import datetime, date
import time

class asyncclient_class(MagicMock):

    def fetch(self, request, callback=None, **kwargs):
        callback(
            Mock(
                headers={},
                code=200,
                body=json.dumps([
                    {
                        "stored": True, 
                        "hash": "17fb3ee9dac3969819af794c1fd11fbd0e02ca3d0e86b9f0c0365f13fa27d225",
                        "type": "image",
                        "width": 100,
                        "height": 150,
                    }               
                ])
            )
        )

def httpclient_sim(self):
    return asyncclient_class()

class test_show_image(Testbase):

    def test_post(self):
        self.login(constants.LEVEL_EDIT_SHOW)
        # create an image
        response = self.post('/1/shows/1/images', {
            'external_name': 'google',
            'external_id': '123',
            'source_title': 'Some user',
            'source_url': 'http://google.com',
            'type': constants.IMAGE_TYPE_POSTER,
        })
        self.assertEqual(response.code, 200, response.body)
        image = utils.json_loads(response.body)
        self.assertEqual(image['external_name'], 'google')
        self.assertEqual(image['external_id'], '123')
        self.assertEqual(image['source_title'], 'Some user')
        self.assertEqual(image['source_url'], 'http://google.com')
        self.assertTrue('relation_type' not in image)
        self.assertTrue('relation_id' not in image)
        self.assertTrue(image['id'] > 0)
        self.assertEqual(image['hash'], None)
        self.assertEqual(image['width'], None)
        self.assertEqual(image['height'], None)
        self.assertEqual(image['type'], constants.IMAGE_TYPE_POSTER)


        # Upload the image
        content_type, body = utils.MultipartFormdataEncoder().encode(
            [], 
            [('image', 'test', b'THIS IS AN IMAGE...')]
        )
        with patch('seplis.api.handlers.file_upload.Handler.get_httpclient', httpclient_sim) as m:
            response = self.put(
                '/1/shows/1/images/{}/data'.format(image['id']), 
                data=body, 
                headers={'Content-Type': content_type},
            )
            self.assertEqual(response.code, 200, response.body)

        # verify that the image got updated
        response = self.get('/1/shows/1/images/{}'.format(image['id']))
        self.assertEqual(response.code, 200)
        image = utils.json_loads(response.body)
        self.assertEqual(image['hash'], '17fb3ee9dac3969819af794c1fd11fbd0e02ca3d0e86b9f0c0365f13fa27d225')
        self.assertEqual(image['width'], 100)
        self.assertEqual(image['height'], 150)

        # update the source
        response = self.put('/1/shows/1/images/{}'.format(image['id']), {
            'external_name': 'google 2',
            'external_id': '1234',
            'source_title': 'Some user 2',
            'source_url': 'http://google2.com',
        })
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/1/images/{}'.format(image['id']))
        self.assertEqual(response.code, 200)
        image = utils.json_loads(response.body)
        self.assertEqual(image['external_name'], 'google 2')
        self.assertEqual(image['external_id'], '1234')
        self.assertEqual(image['source_title'], 'Some user 2')
        self.assertEqual(image['source_url'], 'http://google2.com')

        # get all the images        
        self.get('http://{}/images/_refresh'.format(
            config['elasticsearch']
        ))
        response = self.get('/1/shows/1/images')
        self.assertEqual(response.code, 200, response.body)
        images = utils.json_loads(response.body)
        self.assertEqual(images[0]['id'], image['id'])

        # delete the image
        response = self.delete('/1/shows/1/images/{}'.format(image['id']))
        self.assertEqual(response.code, 200)
        response = self.get('/1/shows/1/images/{}'.format(image['id']))
        self.assertEqual(response.code, 404)


if __name__ == '__main__':
    nose.run(defaultTest=__name__)
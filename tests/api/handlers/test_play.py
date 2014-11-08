# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis import utils

class test_play_handler(Testbase):

    def test(self):
        self.login(0)

        # create a new play server
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'address': 'http://example.net',
        })
        self.assertEqual(response.code, 201, response.body)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas')
        self.assertEqual(server['address'], 'http://example.net')
        self.assertTrue(server['created'])
        self.assertFalse(server['updated'])
        self.assertTrue(server['external_id'])
        self.assertEqual(server['user_id'], self.current_user.id)

        # get
        response = self.get('/1/users/{}/play-servers/{}'.format(
            self.current_user.id, 
            server['id']
        ))
        self.assertEqual(response.code, 200)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas')
        self.assertEqual(server['address'], 'http://example.net')
        self.assertFalse(server['updated'])
        self.assertEqual(server['user_id'], self.current_user.id)
        self.assertTrue(isinstance(server['id'], int))

        # edit
        response = self.put('/1/users/{}/play-servers/{}'.format(
            self.current_user.id, 
            server['id']
        ), {
            'name': 'Thomas 2',
            'address': 'http://example2.net',
        })
        self.assertEqual(response.code, 200)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas 2')
        self.assertEqual(server['address'], 'http://example2.net')
        self.assertTrue(server['updated'])

        # delete
        response = self.delete('/1/users/{}/play-servers/{}'.format(
            self.current_user.id, 
            server['id']
        ))
        self.assertEqual(response.code, 200)

        # get
        response = self.get('/1/users/{}/play-servers/{}'.format(
            self.current_user.id, 
            server['id']
        ))
        self.assertEqual(response.code, 404)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
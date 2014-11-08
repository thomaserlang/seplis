# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis.api.base.user import User
from seplis import utils

class test_play_handler(Testbase):

    def test_single(self):
        self.login(0)

        # create a new play server
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'address': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas')
        self.assertEqual(server['address'], 'http://example.net')
        self.assertEqual(server['secret'], 'SOME SECRET')
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
        self.assertEqual(server['secret'], 'SOME SECRET')
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
            'secret': 'SOME SECRET 2',
        })
        self.assertEqual(response.code, 200)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas 2')
        self.assertEqual(server['address'], 'http://example2.net')
        self.assertEqual(server['secret'], 'SOME SECRET 2')
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

    def test_multiple(self):
        self.login(0) 
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'address': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server1 = utils.json_loads(response.body)
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas 2',
            'address': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server2 = utils.json_loads(response.body)

        # get the servers
        response = self.get('/1/users/{}/play-servers'.format(
            self.current_user.id
        ))
        self.assertEqual(response.code, 200, response.body)
        servers = utils.json_loads(response.body)
        self.assertEqual(len(servers), 2)
        self.assertEqual(servers[0]['external_id'], server1['external_id'])
        self.assertEqual(servers[1]['external_id'], server2['external_id'])

class test_user_access_handler(Testbase):

    def test(self):
        self.login(3)
        user = User.new(
            name='testuser2',
            email='test2@example.com',
            level=0,
        )
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'address': 'http://example.net',
            'secret': 'SOME SECRET',
        })

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
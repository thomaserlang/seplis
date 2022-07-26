# coding=UTF-8
import json
import logging
import nose
from seplis.api.testbase import Testbase
from seplis import utils

class test_play_handler(Testbase):

    def test_single(self):
        self.login(0)

        # create a new play server
        response = self.post('/1/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server = utils.json_loads(response.body)
        logging.info(server)
        self.assertEqual(server['name'], 'Thomas')
        self.assertEqual(server['url'], 'http://example.net')
        self.assertEqual(server['secret'], 'SOME SECRET')
        self.assertTrue(server['created'])
        self.assertTrue(server['updated'])
        self.assertTrue(server['external_id'])
        self.assertEqual(server['user_id'], self.current_user.id)

        # get
        response = self.get('/1/play-servers/{}'.format( 
            server['id']
        ))

        self.assertEqual(response.code, 200)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas')
        self.assertEqual(server['url'], 'http://example.net')
        self.assertEqual(server['secret'], 'SOME SECRET')
        self.assertTrue(server['updated'])
        self.assertEqual(server['user_id'], self.current_user.id)
        self.assertTrue(isinstance(server['id'], int))

        # edit
        response = self.put('/1/play-servers/{}'.format( 
            server['id']
        ), {
            'name': 'Thomas 2',
            'url': 'http://example2.net',
            'secret': 'SOME SECRET 2',
        })
        self.assertEqual(response.code, 200)
        server = utils.json_loads(response.body)
        self.assertEqual(server['name'], 'Thomas 2')
        self.assertEqual(server['url'], 'http://example2.net')
        self.assertEqual(server['secret'], 'SOME SECRET 2')
        self.assertTrue(server['updated'])

        # delete
        response = self.delete('/1/play-servers/{}'.format( 
            server['id']
        ))
        self.assertEqual(response.code, 204)

        # get
        response = self.get('/1/play-servers/{}'.format( 
            server['id']
        ))
        self.assertEqual(response.code, 404)

    def test_multiple(self):
        self.login(0) 
        response = self.post('/1/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server1 = utils.json_loads(response.body)
        response = self.post('/1/play-servers'.format(self.current_user.id), {
            'name': 'Thomas 2',
            'url': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201, response.body)
        server2 = utils.json_loads(response.body)

        # get the servers
        response = self.get('/1/play-servers'.format(
            self.current_user.id
        ))
        self.assertEqual(response.code, 200, response.body)
        servers = utils.json_loads(response.body)
        self.assertEqual(len(servers), 2)
        self.assertEqual(response.headers['X-Total-Count'], '2')
        self.assertEqual(servers[0]['external_id'], server1['external_id'])
        self.assertEqual(servers[1]['external_id'], server2['external_id'])
        self.assertTrue('secret' not in servers[0])
        self.assertTrue('secret' not in servers[1])

        # test that deleting a server removes it from the list
        response = self.delete('/1/play-servers/{}'.format( 
            servers[0]['id']
        ))
        self.assertEqual(response.code, 204)
        response = self.get('/1/play-servers')
        servers = utils.json_loads(response.body)
        self.assertEqual(len(servers), 1, response.body)

class test_user_access_handler(Testbase):

    def test(self):
        self.login(3)
        user = self.new_user(
            name='testuser2',
            email='test2@example.com',
            level=0,
        )
        response = self.post('/1/play-servers', {
            'name': 'Thomas',
            'url': 'http://example.net',
            'secret': 'SOME SECRET',
        })
        self.assertEqual(response.code, 201)
        server = utils.json_loads(response.body)

        # Test that only the user who created the server has access
        response = self.get('/1/play-servers/{}/users'.format(
            server['id'],
        ))
        self.assertEqual(response.code, 200, response.body)
        users = utils.json_loads(response.body)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['id'], self.current_user.id)

        # Lets give the user access to the play server
        response = self.put('/1/play-servers/{}/users/{}'.format(
            server['id'],
            user.id,
        ))
        self.assertEqual(response.code, 204, response.body)

        # Now the user should have access
        response = self.get('/1/play-servers/{}/users'.format(
            server['id'],
        ))
        self.assertEqual(response.code, 200, response.body)
        users = utils.json_loads(response.body)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[1]['id'], user.id)

        # Remove the user from the server access list        
        response = self.delete('/1/play-servers/{}/users/{}'.format(
            server['id'],
            user.id,
        ))

        response = self.get('/1/play-servers/{}/users'.format(
            server['id'],
        ))
        self.assertEqual(response.code, 200, response.body)
        users = utils.json_loads(response.body)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['id'], self.current_user.id)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
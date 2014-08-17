# coding=UTF-8
import nose
import json
from seplis.api.testbase import Testbase
from seplis.api.base.app import App
from seplis.api import constants

class test_user(Testbase):

    def test_post(self):
        response = self.post('/1/users', {
            'name': 'testø',
            'email': 'wrongemail',
            'password': 'hej',
        })
        self.assertEqual(response.code, 400)
        error = json.loads(response.body.decode('utf-8'))
        for error in error['errors']:
            if error['message'] == 'required key not provided':
                continue
            if error['field'] == 'name':
                self.assertEqual(error['message'], 'must only contain a-z, 0-9, _ and - for dictionary value')
            elif error['field'] == 'email':
                self.assertEqual(error['message'], 'this email is invalid for dictionary value')
            elif error['field'] == 'password':
                self.assertEqual(error['message'], 'length of value must be at least 6 for dictionary value')

        response = self.post('/1/users', {
            'name': 'test',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = json.loads(response.body.decode('utf-8'))
        self.assertEqual(user['name'], 'test')
        self.assertEqual(user['email'], 'test@email.com')
        self.assertTrue('password' not in user)
        self.assertTrue('created' in user)

    def test_get(self):
        # new user
        response = self.post('/1/users', {
            'name': 'test',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = json.loads(response.body.decode('utf-8'))

        # we should not be able to retrieve any users without being logged in
        response = self.get('/1/users/{}'.format(user['id']))
        self.assertEqual(response.code, 401)

        # login and test that we can retrieve the user.
        # because our user does not have a high enough level to view the email
        # it should not be there.
        self.login(user_level=2)
        response = self.get('/1/users/{}'.format(user['id']))
        self.assertEqual(response.code, 200)
        user2 = json.loads(response.body.decode('utf-8'))
        self.assertEqual(user2['name'], 'test')
        self.assertFalse('email' in user2)
        user.pop('email')
        self.assertEqual(user2, user)

        # check that we can get the current user.
        # when we retrieve our own user name the email 
        # should be visible.
        response = self.get('/1/users/current')
        self.assertEqual(response.code, 200)
        user3 = json.loads(response.body.decode('utf-8'))
        self.assertEqual(user3['email'], self.current_user.email)

    def test_token(self):
        response = self.post('/1/users', {
            'name': 'test',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = json.loads(response.body.decode('utf-8'))

        # test wrong grant type
        response = self.post('/1/token', {
            'grant_type': 'wrong',
        })
        self.assertEqual(response.code, 400)

        # test wrong client_id
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@email.com',
            'password': '123456',
            'client_id': 'wrong'
        })
        self.assertEqual(response.code, 400)

        # test wrong app level
        app = App.new(
            user_id=user['id'],
            name='test app 2',
            redirect_uri='',
            level=1, # system
        )
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@email.com',
            'password': '123456',
            'client_id': app.client_id,
        })
        self.assertEqual(response.code, 403)

        app = App.new(
            user_id=user['id'],
            name='test app',
            redirect_uri='',
            level=constants.app_level_root, # system
        )
        # test wrong password
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@email.com',
            'password': 'thisiswrong',
            'client_id': app.client_id,
        })
        self.assertEqual(response.code, 401)

        # test successfully login
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@email.com',
            'password': '123456',
            'client_id': app.client_id,
        })
        self.assertEqual(response.code, 200)

        token = json.loads(response.body.decode('utf-8'))
        self.assertTrue('access_token' in token)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
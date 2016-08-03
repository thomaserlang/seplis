# coding=UTF-8
import nose
import json
from seplis.api.testbase import Testbase
from seplis.api import constants, models
from seplis.api.decorators import new_session
from seplis import utils, config
from datetime import datetime, timedelta

class test_user(Testbase):

    def test_post(self):
        response = self.post('/1/users', {
            'name': 'testø',
            'email': 'wrongemail',
            'password': 'hej',
        })
        self.assertEqual(response.code, 400)
        error = utils.json_loads(response.body)
        for error in error['errors']:
            if error['message'] == 'required key not provided':
                continue
            if error['field'] == 'name':
                self.assertEqual(error['message'], 'must only contain a-z, 0-9, _ and -')
            elif error['field'] == 'email':
                self.assertEqual(error['message'], 'this is an invalid email address')
            elif error['field'] == 'password':
                self.assertEqual(error['message'], 'Too few values (6 is the least)')

        response = self.post('/1/users', {
            'name': 'test___',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = utils.json_loads(response.body)
        self.assertEqual(user['name'], 'test___')
        self.assertEqual(user['email'], 'test@email.com')
        self.assertTrue('password' not in user)
        self.assertTrue('created_at' in user)

    def test_get(self):
        # new user
        response = self.post('/1/users', {
            'name': 'test___',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = utils.json_loads(response.body)

        # login and test that we can retrieve the user.
        # because our user does not have a high enough level to view the email
        # it should not be there.
        self.login(user_level=2)
        response = self.get('/1/users/{}'.format(user['id']))
        self.assertEqual(response.code, 200)
        user2 = utils.json_loads(response.body)
        self.assertEqual(user2['name'], 'test___')
        self.assertFalse('email' in user2)

        # check that we can get the current user.
        # when we retrieve our own user name the email 
        # should be visible.
        response = self.get('/1/users/current')
        self.assertEqual(response.code, 200)
        user3 = utils.json_loads(response.body)
        self.assertEqual(user3['email'], self.current_user.email)

    def test_token(self):
        response = self.post('/1/users', {
            'name': 'test___',
            'email': 'test@email.com',
            'password': '123456',
        })
        self.assertEqual(response.code, 201)
        user = utils.json_loads(response.body)

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
        app = self.new_app(
            user_id=user['id'],
            name='test app 2',
            redirect_uri='',
            level=1,
        )
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@email.com',
            'password': '123456',
            'client_id': app.client_id,
        })
        self.assertEqual(response.code, 403)

        app = self.new_app(
            user_id=user['id'],
            name='test app',
            redirect_uri='',
            level=constants.LEVEL_GOD, # system
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

        token = utils.json_loads(response.body)
        self.assertTrue('access_token' in token)

    def test_seplis_old_password(self):
        from seplis.api.models.user import seplis_v2_password_validate
        old_password = 'seplis_old:818a4bd6aa76c2c1b72ad7b0355d9a4f5661f249a8642e6a64a776edc717cb30:3d418e9bd42c27529d3ba67af6b162fc7035763582ae3e9311197727a6be971adcbb3f32105021b55ae8f3f86061b5f0f949623e12538e86364ab6ce6fefb628'
        self.assertTrue(
            seplis_v2_password_validate(
                'hejhej123',
                old_password
            )
        )

        # test successfully login with a password in the old format
        user = self.new_user(
            name='test___',
            email='test@example.net',
            password=old_password,
            level=0,
        )
        app = self.new_app(
            user_id=user.id,
            name='test app',
            redirect_uri='',
            level=constants.LEVEL_GOD,
        )
        response = self.post('/1/token', {
            'grant_type': 'password',
            'email': 'test@example.net',
            'password': 'hejhej123',
            'client_id': app.client_id,
        })
        self.assertEqual(response.code, 200)

    def test_user_search(self):
        users = []
        users.append(self.new_user(
            name='test___',
            email='test___@example.net',
            password='123',
            level=0,
        ))
        users.append(self.new_user(
            name='test___2',
            email='test___2@example.net',
            password='123',
            level=0,
        ))
        self.refresh_es()
        response = self.get('/1/users')
        self.assertEqual(response.code, 200, response.body)
        self.assertEqual(len(utils.json_loads(response.body)), 2)
        
        # test that we can search for a user
        response = self.get('/1/users?q=test___2')
        self.assertEqual(response.code, 200, response.body) 
        user = utils.json_loads(response.body)[0]
        self.assertEqual(user['name'], 'test___2')
        # test that the user search does not leak emails
        self.assertTrue('email' not in user)

class Test_progress_token_handler(Testbase):

    def test(self):
        self.login()

        response = self.get('/1/progress-token')
        self.assertEqual(response.code, 200)
        d = utils.json_loads(response.body)

        self.access_token = d['token']

        response = self.get('/1/users/current')
        self.assertEqual(response.code, 403, response.body)
        d = utils.json_loads(response.body)
        self.assertEqual(d['extra']['user_level'], -1)

class Test_change_password(Testbase):

    def test(self):
        self.login()
        models.User.change_password(
            user_id=self.current_user.id,
            new_password='password',
        )

        # Test wrong password
        response = self.post('/1/users/current/change-password', {
            'password': 'wrong',
            'new_password': 'password123',
        })
        self.assertEqual(response.code, 401, response.body)

        # Test correct password
        response = self.post('/1/users/current/change-password', {
            'password': 'password',
            'new_password': 'password123',
        })
        self.assertEqual(response.code, 200, response.body)

        # Test that our session has not expired
        response = self.get('/1/users/current')
        self.assertEqual(response.code, 200)

        # Test that all other tokens than the current one will
        # expire on password change
        with new_session() as session:
            token = models.Token(
                app_id=None,
                user_id=self.current_user.id,
                user_level=constants.LEVEL_USER,
                expires=datetime.utcnow()+timedelta(days=1),
            )
            session.add(token)
            session.commit()

            tokens = session.query(models.Token).filter(
                models.Token.user_id == self.current_user.id
            ).all()
            self.assertEqual(len(tokens), 2)
        response = self.post('/1/users/current/change-password', {
            'password': 'password123',
            'new_password': 'password321',
        })
        self.assertEqual(response.code, 200, response.body)
        with new_session() as session:
            tokens = session.query(models.Token).filter(
                models.Token.user_id == self.current_user.id
            ).all()
            self.assertEqual(len(tokens), 1)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
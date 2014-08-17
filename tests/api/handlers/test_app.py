# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase
from seplis.utils import json_dumps

class test_app(Testbase):

    def test(self):
        self.login()

        # test create
        response = self.post('/1/apps', {
            'name': 'thomas app',
            'redirect_uri': '#',
        })
        self.assertEqual(response.code, 201, response.body)
        app = json.loads(response.body.decode('utf-8'))
        self.assertTrue(app['client_id']!=None)
        self.assertTrue(app['client_secret']!=None)
        self.assertTrue(app['user_id'], self.current_user.id)
        self.assertEqual(app['level'], 0)
        self.assertEqual(app['name'], 'thomas app')

        # test get
        response = self.get('/1/apps/{}'.format(app['id']))
        self.assertEqual(response.code, 200, response.body)
        app2 = json.loads(response.body.decode('utf-8'))
        self.assertTrue(app2['client_id']!=None)
        self.assertTrue(app2['client_secret']!=None)
        self.assertTrue(app2['user_id'], self.current_user.id)
        self.assertEqual(app2['level'], 0)
        self.assertEqual(app2['name'], 'thomas app')
        self.assertEqual(app2['id'], app['id'])
        
if __name__ == '__main__':
    nose.run(defaultTest=__name__)
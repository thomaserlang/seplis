# coding=UTF-8
import json
import nose
from seplis.api.testbase import Testbase

class test_play_handler(Testbase):

    def test(self):
        self.login(0)

        # create a new play server
        response = self.post('/1/users/{}/play-servers'.format(self.current_user.id), {
            'name': 'Thomas',
            'address': 'http://example.net',
        })
        self.assertEqual(response.code, 201, response.body)



if __name__ == '__main__':
    nose.run(defaultTest=__name__)
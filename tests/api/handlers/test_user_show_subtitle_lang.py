# coding=UTF-8
import json
from seplis.api.testbase import Testbase
from seplis import utils
from seplis.api.decorators import new_session

class Test_handler(Testbase):

    def test(self):
        show_id = self.new_show()
        url = '/1/shows/{}/user-subtitle-lang'.format(show_id)
        response = self.get(url)
        self.assertEqual(response.code, 204)

        response = self.put(url, {
            'subtitle_lang': 'eng',
            'audio_lang': 'jpn',
        })
        self.assertEqual(response.code, 204)

        response = self.get(url)
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['subtitle_lang'], 'eng')
        self.assertEqual(data['audio_lang'], 'jpn')

        # Check that put will overwrite values with `None` if not sepcified
        # in the request.
        response = self.put(url, {
            'subtitle_lang': 'eng',
        })
        self.assertEqual(response.code, 204)
        response = self.get(url)
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['subtitle_lang'], 'eng')
        self.assertEqual(data['audio_lang'], None)

        # Check that patch will not overwrite values not sepcified in the
        # request
        response = self.patch(url, {
            'audio_lang': 'jpn',
        })
        self.assertEqual(response.code, 204)
        response = self.get(url)
        self.assertEqual(response.code, 200)
        data = utils.json_loads(response.body)
        self.assertEqual(data['subtitle_lang'], 'eng')
        self.assertEqual(data['audio_lang'], 'jpn')

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
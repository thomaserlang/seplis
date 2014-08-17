import requests
import json

class Fanart:
    __url__ = 'http://api.fanart.tv/webservice/series/{apikey}/{id}/'

    def __init__(self, apikey):
        self.apikey = apikey

    def get_photos_urls(self, id_):
        r = requests.get(
            url=self.__url__.format(
                apikey=self.apikey,
                id=id_,
            )
        )
        if r.status_code == 200:
            data = json.loads(r.content)
            if data:
                photos = []
                for title, value in data.iteritems():
                    for type_, values in value.iteritems():
                        if isinstance(values, list):
                            for photo in values:
                                photos.append(photo['url'])
                return photos
        return []
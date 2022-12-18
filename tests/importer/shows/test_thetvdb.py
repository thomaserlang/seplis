# coding=UTF-8
import mock
import responses
from unittest import TestCase
from seplis.importer.series.thetvdb import Thetvdb
from seplis import schemas
from seplis.api import constants

class Test_thetvdb(TestCase):

    updates = '''
    {
        "data": [
            {
              "id": 298704,
              "lastUpdated": 1501428983
            },
            {
              "id": 307674,
              "lastUpdated": 1501428986
            }
        ]
    }
    '''

    show = u'''{
        "data": {
            "id": 321285,
            "seriesName": "Boruto: Naruto Next Generations",
            "aliases": [],
            "banner": "graphical/321285-g2.jpg",
            "seriesId": "",
            "status": "Continuing",
            "firstAired": "2017-04-05",
            "network": "TV Tokyo",
            "networkId": "",
            "runtime": "25",
            "genre": [
                "Action",
                "Adventure",
                "Animation"
            ],
            "overview": "The Hidden Leaf Village has entered an era of peace and modernity. Tall buildings line the streets, giant screens flash with images, and the Thunder Rail runs through the village, connecting each district together. Though it's still a ninja village, the number of civilians has increased and the life of the shinobi is beginning to change.\\r\\n \\r\\nBoruto Uzumaki, son of Seventh Hokage Naruto Uzumaki, has enrolled in the Ninja Academy to learn the ways of the ninja. The other students are ready to dismiss him as \\"just the son of the Hokage,” but Boruto’s heart and character blow all their assumptions away.\\r\\n \\r\\nAs a series of mysterious events begins to unfold, it’s up to Boruto and his new friends to handle them. Like a gale-force wind, Boruto makes his own way into everyone's hearts; his story is about to begin!\\r\\n",
            "lastUpdated": 1501231969,
            "airsDayOfWeek": "Wednesday",
            "airsTime": "17:55",
            "rating": "",
            "imdbId": "tt6342474",
            "zap2itId": "",
            "added": "2016-12-17 07:59:09",
            "addedBy": 430859,
            "siteRating": 9.6,
            "siteRatingCount": 5
        }
    }'''

    episodes = '''{
      "links": {
        "first": 1,
        "last": 4,
        "next": null,
        "prev": null
      },
      "data": [
        {
          "absoluteNumber": null,
          "airedEpisodeNumber": 1,
          "airedSeason": 0,
          "airedSeasonID": 19575,
          "dvdEpisodeNumber": null,
          "dvdSeason": null,
          "episodeName": "Navy NCIS: The Beginning (1)",
          "firstAired": "2003-04-22",
          "id": 74097,
          "language": {
            "episodeName": "en",
            "overview": "en"
          },
          "lastUpdated": 1462790046,
          "overview": "The pilot that aired a few weeks after the show's premiere, and called \\"Navy NCIS: The Beginning\\". It was originally aired as a JAG episode known as S08E20 \\"Ice Queen (1)\\""
        },
        {
          "absoluteNumber": 1,
          "airedEpisodeNumber": 1,
          "airedSeason": 1,
          "airedSeasonID": 3513,
          "dvdEpisodeNumber": 1,
          "dvdSeason": 1,
          "episodeName": "Yankee White",
          "firstAired": "2003-09-23",
          "id": 74098,
          "language": {
            "episodeName": "en",
            "overview": "en"
          },
          "lastUpdated": 1473558075,
          "overview": "While on Air Force One, a Navy commanding officer dies.  Agents from the Navy NCIS decide to take the investigation into their own hands and also force a Secret Service Agent to help.  Now the NCIS team has to figure out if the Navy Officer's death was of natural causes or not."
        }
      ]
    }
    '''

    images = '''{
      "data": [
        {
          "id": 1174797,
          "keyType": "poster",
          "subKey": "",
          "fileName": "posters/321285-1.jpg",
          "resolution": "680x1000",
          "ratingsInfo": {
            "average": 10,
            "count": 1
          },
          "thumbnail": "_cache/posters/321285-1.jpg"
        }
      ]
    }
    '''

    login = '{"token": "asd123"}'
    
    @responses.activate
    def test_info(self):
        show_id = 32
        responses.add(responses.POST, Thetvdb._url+'/login',
                  body=self.login, status=200, content_type='application/json')        
        responses.add(responses.GET, Thetvdb._url+'/series/{}'.format(show_id),
                  body=self.show, status=200, content_type='application/json')
        thetvdb = Thetvdb()
        show = thetvdb.info(show_id)
        schemas.validate(schemas.Show_schema, show)
        self.assertEqual(show['premiered'].isoformat(), '2017-04-05')
        self.assertEqual(show['title'], 'Boruto: Naruto Next Generations')

    @responses.activate
    def test_episodes(self):
        show_id = 32
        responses.add(responses.POST, Thetvdb._url+'/login',
                  body=self.login, status=200, content_type='application/json')
        responses.add(responses.GET, Thetvdb._url+'/series/{}/episodes'.format(show_id),
                  body=self.episodes, status=200, content_type='application/json')
        thetvdb = Thetvdb()
        episodes = thetvdb.episodes(show_id)

        schemas.validate([schemas.Episode_schema], episodes)
        self.assertEqual(episodes[0]['air_date'].isoformat(), '2003-09-23')

    @responses.activate
    def test_incremental_updates(self):
        responses.add(responses.POST, Thetvdb._url+'/login',
                  body=self.login, status=200, content_type='application/json')
        responses.add(responses.GET, Thetvdb._url+'/updated/query',
                  body=self.updates, status=200, content_type='application/json')
        thetvdb = Thetvdb()
        thetvdb.last_update_timestamp = mock.Mock(return_value=1)
        ids = thetvdb.incremental_updates()
        self.assertTrue('298704' in ids)
        self.assertTrue('307674' in ids)

    @responses.activate
    def test_images(self):
        show_id = 32
        responses.add(responses.POST, Thetvdb._url+'/login',
                  body=self.login, status=200, content_type='application/json')
        responses.add(responses.GET, Thetvdb._url+'/series/{}/images/query'.format(show_id),
                  body=self.images, status=200, content_type='application/json')
        thetvdb = Thetvdb()
        images = thetvdb.images(show_id)
        image = images[0]
        schemas.validate(schemas.Image_required, image)
        self.assertEqual('TheTVDB', image['source_title'])
        self.assertEqual('thetvdb', image['external_name'])
        self.assertEqual('1174797', image['external_id'])
        self.assertEqual(constants.IMAGE_TYPE_POSTER, image['type'])

if __name__ == '__main__':
    from seplis.api.testbase import run_file
    run_file(__file__)
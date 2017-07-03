# coding=UTF-8
import responses
import nose
import mock
import xmltodict
from datetime import datetime
from unittest import TestCase
from seplis.importer.shows.tvmaze import Tvmaze
from seplis import schemas
from seplis.api import constants

class test_tvmaze(TestCase):
    show = '''{
        "id": 32,
        "url": "http://www.tvmaze.com/shows/32/fargo",
        "name": "Fargo",
        "type": "Scripted",
        "language": "English",
        "genres": ["Drama", "Crime"],
        "status": "Running",
        "runtime": 60,
        "premiered": "2014-04-15",
        "schedule": {
            "time": "22:00",
            "days": ["Monday"]
        },
        "rating": {
            "average": 9
        },
        "weight": 6,
        "network": {
            "id": 13,
            "name": "FX",
            "country": {
                "name": "United States",
                "code": "US",
                "timezone": "America/New_York"
            }
        },
        "webChannel": null,
        "externals": {
            "tvrage": 35276,
            "thetvdb": 269613,
            "imdb": "tt2802850"
        },
        "image": {
            "medium": "http://tvmazecdn.com/uploads/images/medium_portrait/34/86243.jpg",
            "original": "http://tvmazecdn.com/uploads/images/original_untouched/34/86243.jpg"
        },
        "summary": "<p><strong><em>\\"Fargo\\"</em></strong> is an american crime drama with some dark comical elements inspired by the film Fargo written by the Coen brothers. It was met with considerable acclaim as insurance salesman Lester Nygaard faces off against the psychopath Lorne Malvo. The second season will revolve around a different story.</p>",
        "updated": 1453681507,
        "_links": {
            "self": {
                "href": "http://api.tvmaze.com/shows/32"
            },
            "previousepisode": {
                "href": "http://api.tvmaze.com/episodes/203279"
            }
        }
    }'''

    episodes = '''[{
        "id": 1610,
        "url": "http://www.tvmaze.com/episodes/1610/fargo-1x01-the-crocodiles-dilemma",
        "name": "The Crocodile's Dilemma",
        "season": 1,
        "number": 1,
        "airdate": "2014-04-15",
        "airtime": "22:00",
        "airstamp": "2014-04-15T22:00:00-04:00",
        "runtime": 60,
        "image": {
            "medium": "http://tvmazecdn.com/uploads/images/medium_landscape/10/26415.jpg",
            "original": "http://tvmazecdn.com/uploads/images/original_untouched/10/26415.jpg"
        },
        "summary": "<p>A rootless, manipulative man  meets a small town insurance salesman  and sets him on a path of destruction. </p>",
        "_links": {
            "self": {
                "href": "http://api.tvmaze.com/episodes/1610"
            }
        }
    }, {
        "id": 1611,
        "url": "http://www.tvmaze.com/episodes/1611/fargo-1x02-the-rooster-prince",
        "name": "The Rooster Prince",
        "season": 1,
        "number": 2,
        "airdate": "2014-04-22",
        "airtime": "22:00",
        "airstamp": "2014-04-22T22:00:00-04:00",
        "runtime": 60,
        "image": {
            "medium": "http://tvmazecdn.com/uploads/images/medium_landscape/10/26416.jpg",
            "original": "http://tvmazecdn.com/uploads/images/original_untouched/10/26416.jpg"
        },
        "summary": "<p>Molly begins to suspect that Lester is involved with the murders, but her new boss points her in a different direction. Meanwhile, Malvo investigates the blackmail plot against a man known as the Supermarket King. </p>",
        "_links": {
            "self": {
                "href": "http://api.tvmaze.com/episodes/1611"
            }
        }
    }]'''

    @responses.activate
    def test_info(self):
        show_id = 32
        responses.add(responses.GET, Tvmaze._url.format(show_id=show_id),
                  body=self.show, status=200, content_type='application/json')
        tvmaze = Tvmaze()
        show = tvmaze.info(show_id)
        schemas.validate(schemas.Show_schema, show)
        self.assertTrue('premiered' in show)

    @responses.activate
    def test_episodes(self):
        show_id = 32
        responses.add(responses.GET, Tvmaze._url_episodes.format(show_id=show_id),
                  body=self.episodes, status=200, content_type='application/json')
        tvmaze = Tvmaze()
        episodes = tvmaze.episodes(show_id)
        schemas.validate([schemas.Episode_schema], episodes)
        self.assertEqual(episodes[0]['air_date'], datetime(2014, 4, 16).date())
        self.assertEqual(episodes[0]['air_time'], datetime(2014, 4, 16, 2).time())

    @responses.activate
    def test_incremental_updates(self):
        responses.add(responses.GET, Tvmaze._url_update,
                  body='{"1": 5, "2": 10}', status=200, content_type='application/json')
        tvmaze = Tvmaze()
        tvmaze.last_update_timestamp = mock.Mock(return_value=1)
        ids = tvmaze.incremental_updates()
        self.assertTrue('1' in ids)
        self.assertTrue('2' in ids)

        tvmaze.last_update_timestamp = mock.Mock(return_value=6)
        ids = tvmaze.incremental_updates()
        self.assertFalse('1' in ids)
        self.assertTrue('2' in ids)

    @responses.activate
    def test_images(self):
        show_id = 32
        responses.add(responses.GET, Tvmaze._url.format(show_id=show_id),
                  body=self.show, status=200, content_type='application/json')
        tvmaze = Tvmaze()
        images = tvmaze.images(show_id)
        image = images[0]
        schemas.validate(schemas.Image_required, image)
        self.assertEqual('TVmaze', image['source_title'])
        self.assertEqual('tvmaze', image['external_name'])
        self.assertEqual('32', image['external_id'])
        self.assertEqual(constants.IMAGE_TYPE_POSTER, image['type'])

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
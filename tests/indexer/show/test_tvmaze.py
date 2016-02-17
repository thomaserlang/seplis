# coding=UTF-8
import responses
import nose
import mock
import xmltodict
from unittest import TestCase
from seplis.indexer.show.tvmaze import Tvmaze
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
    def test_get_show(self):
        show_id = 1
        responses.add(responses.GET, Tvmaze._url.format(show_id=show_id),
                  body=self.show, status=200, content_type='application/json')
        tvmaze = Tvmaze()
        show = tvmaze.get_show(show_id)
        schemas.validate(schemas.Show_schema, show)

    @responses.activate
    def test_get_episodes(self):
        show_id = 1
        responses.add(responses.GET, Tvmaze._url_episodes.format(show_id=show_id),
                  body=self.episodes, status=200, content_type='application/json')
        tvmaze = Tvmaze()
        episodes = tvmaze.get_episodes(show_id)
        schemas.validate([schemas.Episode_schema], episodes)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)
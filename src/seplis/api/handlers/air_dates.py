import copy
import good
from . import base
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from datetime import datetime, timedelta
from collections import OrderedDict

class Handler(base.Handler):

    __arguments_schema__ = good.Schema({
        'days_back': good.Any(
            good.All(good.Coerce(int), good.Range(min=0, max=7)),
            good.Default(1),
        ),
        'days_ahead': good.Any(
            good.All(good.Coerce(int), good.Range(min=0, max=14)),
            good.Default(7)
        ),
    }, default_keys=good.Required)

    async def get(self, user_id):        
        episodes = await self.get_episodes(user_id)
        if not episodes:
            self.write_object([])
            return
        ids = []
        [ids.append(episode['show_id']) for episode in episodes \
            if episode['show_id'] not in ids]
        shows = await self.get_shows(ids)
        shows = {show['id']: show for show in shows}
        airdates = OrderedDict()
        airdate_shows = OrderedDict()
        prev = None
        for ep in episodes:
            if prev == None:
                prev = ep['air_date']
            if prev != ep['air_date']:
                airdates[prev] = list(airdate_shows.values())
                prev = ep['air_date']
                airdate_shows = {}
            if ep['show_id'] not in airdate_shows:
                airdate_shows[ep['show_id']] = copy.copy(
                    shows[ep['show_id']]
                )
            show = airdate_shows[ep['show_id']]
            show.setdefault('episodes', [])
            show['episodes'].append(
                self.episode_wrapper(ep)
            )
        if episodes:
            airdates[prev] = list(airdate_shows.values())
        self.write_object([{'air_date': ad, 'shows': airdates[ad]}\
            for ad in airdates])

    async def get_episodes(self, user_id):
        args = self.validate_arguments()
        show_ids = models.Show_fan.get_all(user_id)
        if not show_ids:
            return []
        now = datetime.utcnow().date()
        episodes = await self.es('/episodes/episode/_search',
            body={
                'query': {
                    'bool': {
                        'filter': [
                            {'terms': { 'show_id': show_ids }},
                            {'range': {
                                'air_date': {
                                    'gte': (now - \
                                        timedelta(days=args['days_back'])).isoformat(),
                                    'lte': (now + \
                                        timedelta(days=args['days_ahead'])).isoformat(),
                                }
                            }}
                        ]
                    }
                }
            },
            query={
                'from': 0,
                'size': 1000,
                'sort': 'air_date:asc,show_id:asc,number:asc',
            },
        )
        return [episode['_source'] \
            for episode in episodes['hits']['hits']]
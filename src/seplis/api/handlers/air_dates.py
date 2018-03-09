import copy
import good
from . import base
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from seplis.api.decorators import run_on_executor, new_session
from datetime import datetime, timedelta
from collections import OrderedDict

class Handler(base.Handler):

    __arguments_schema__ = good.Schema({
        'days_back': good.Any(
            good.All(good.Coerce(int), good.Range(min=0, max=7)),
            good.Default(2),
        ),
        'days_ahead': good.Any(
            good.All(good.Coerce(int), good.Range(min=0, max=14)),
            good.Default(7)
        ),
    }, default_keys=good.Required)

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id)   
        shows_episodes = await self.get_shows_episodes(user_id)
        if not shows_episodes:
            self.write_object([])
            return
        ids = []
        shows = {se[0]['id']: se[0] for se in shows_episodes}
        airdates = OrderedDict()
        airdate_shows = OrderedDict()
        prev = None
        for se in shows_episodes:
            if prev == None:
                prev = se[1]['air_date']
            if prev != se[1]['air_date']:
                airdates[prev] = list(airdate_shows.values())
                prev = se[1]['air_date']
                airdate_shows = {}
            if se[1]['show_id'] not in airdate_shows:
                airdate_shows[se[1]['show_id']] = copy.copy(
                    shows[se[1]['show_id']]
                )
            show = airdate_shows[se[1]['show_id']]
            show.setdefault('episodes', [])
            show['episodes'].append(
                self.episode_wrapper(se[1])
            )
        if shows_episodes:
            airdates[prev] = list(airdate_shows.values())
        self.write_object([{'air_date': ad, 'shows': airdates[ad]}\
            for ad in airdates])

    @run_on_executor
    def get_shows_episodes(self, user_id):
        args = self.validate_arguments()
        now = datetime.utcnow()
        from_ = (now - timedelta(days=args['days_back'])).isoformat()
        to_ = (now + timedelta(days=args['days_ahead'])).isoformat()
        with new_session() as session:
            rows = session.query(models.Episode, models.Show).filter(
                models.Show_fan.user_id == user_id,
                models.Show_fan.show_id == models.Show.id,
                models.Episode.show_id == models.Show.id,
                models.Episode.air_date >= from_,
                models.Episode.air_date <= to_,
            ).order_by(
                models.Episode.air_date, 
                models.Episode.air_time, 
                models.Show.id,
            ).all()
            return [(r.Show.serialize(), r.Episode.serialize()) for r in rows]
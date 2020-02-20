import good, logging
import sqlalchemy as sa
from . import base, user_fan_of
from seplis import schemas, utils
from seplis.api import constants, exceptions, models
from seplis.api.decorators import authenticated, new_session, run_on_executor
from seplis.api.connections import database

class Handler(base.Pagination_handler):

    __arguments_schema__ = good.Schema({
        'genre': [str],
        'expand': [str],
        'sort': [str],
    }, default_keys=good.Optional, extra_keys=good.Allow)

    async def get(self, user_id):
        user_id = self.user_id_or_current(user_id) 
        super().get()
        r = await self.get_shows(user_id)
        self.write_object(r)

    @run_on_executor
    def get_shows(self, user_id):
        args = self.validate_arguments()
        with new_session() as session:
            elw = models.Episode_watching
            ew = models.Episode_watched
            query = session.query(
                models.Show,
                models.Episode_watched,
                models.Episode,
            ).filter(
                elw.user_id == user_id,
                ew.user_id == elw.user_id,
                ew.show_id == elw.show_id,
                ew.episode_number == elw.episode_number,            
                models.Show.id == elw.show_id,
                models.Episode.show_id == elw.show_id,
                models.Episode.number == elw.episode_number,
            )

            sort = args.get('sort', ['watched_at'])[0]            
            if sort == 'user_rating':
                query = query.outerjoin(
                    (models.User_show_rating, sa.and_(
                        models.User_show_rating.show_id == models.Show.id,
                        models.User_show_rating.user_id == user_id,
                    ))
                ).order_by(
                    sa.desc(models.User_show_rating.rating),
                    sa.desc(ew.watched_at), 
                    sa.desc(elw.show_id)
                )
            else:
                query = query.order_by(
                    sa.desc(ew.watched_at), 
                    sa.desc(elw.show_id)
                )

            genres = list(filter(None, args.get('genre', [])))
            if genres:
                query = query.filter(
                    models.Show_genre.show_id == models.Show.id,
                    models.Show_genre.genre.in_(genres),
                )

            p = query.paginate(self.page, self.per_page)

            records = []
            for r in p.records:
                d = r.Show.serialize()
                d['user_watching'] = r.Episode_watched.serialize()
                d['user_watching']['episode'] = r.Episode.serialize()
                records.append(d)

            expand = args.get('expand', [])
            if 'user_rating' in expand:
                self.expand_user_rating(records, user_id)

            p.records = records
            return p
from sqlalchemy import select
from seplis.api import schemas, models
from seplis.api.handlers import base
from seplis.utils.sqlalchemy import paginate

class Handler(base.Handler):

    __arguments_schema__ = schemas.Pagination_schema

    async def get(self, user_id=None):
        user_id = self.user_id_or_current(user_id)
        args: schemas.Pagination_schema = self.validate_arguments()
        async with self.async_session() as session:
            query = select(models.Movie, models.Movie_watched).where(
                models.Movie_watched.user_id == user_id,
                models.Movie.id == models.Movie_watched.movie_id,
            ).order_by(
                models.Movie_watched.watched_at.desc()
            )
            p = await paginate(session, query, page=args.page[0], per_page=args.per_page[0], scalars=False)
            records = []
            for r in p.records:
                d = r.Movie.to_dict()
                d['user_watched'] = r.Movie_watched.to_dict()
                records.append(d)
            p.records = records
            self.write_object(p)
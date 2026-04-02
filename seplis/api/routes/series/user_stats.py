import sqlalchemy as sa
from fastapi import Depends, Security

from ... import models, schemas
from ...dependencies import AsyncSession, authenticated, get_session
from .router import router


@router.get('/{series_id}/user-stats', response_model=schemas.Series_user_stats,
            description='''
            **Scope required:** `user:view_stats`
            ''')
async def get_user_stats(
    series_id: int,    
    session: AsyncSession = Depends(get_session),
    user: schemas.User_authenticated = Security(authenticated, scopes=['user:view_stats']),
):
    q = await session.execute(sa.select(
        sa.func.ifnull(sa.func.sum(models.MEpisodeWatched.times), 0).label('episodes_watched'),
        sa.func.ifnull(sa.func.sum(
            models.MEpisodeWatched.times * \
                sa.func.ifnull(
                    models.MEpisode.runtime,
                    sa.func.ifnull(models.MSeries.runtime, 0),
                )
        ), 0).label('episodes_watched_minutes'),
    ).where(        
        models.MEpisodeWatched.user_id == user.id,
        models.MEpisodeWatched.series_id == series_id,
        models.MEpisode.series_id == models.MEpisodeWatched.series_id,
        models.MEpisode.number == models.MEpisodeWatched.episode_number,
        models.MSeries.id == models.MEpisodeWatched.series_id,
    ))
    return schemas.Series_user_stats.model_validate(q.first())
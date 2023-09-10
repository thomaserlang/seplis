from fastapi import Depends, Security
import sqlalchemy as sa
from ...dependencies import authenticated, get_session, AsyncSession
from ... import models, schemas
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
        sa.func.ifnull(sa.func.sum(models.Episode_watched.times), 0).label('episodes_watched'),
        sa.func.ifnull(sa.func.sum(
            models.Episode_watched.times * \
                sa.func.ifnull(
                    models.Episode.runtime,
                    sa.func.ifnull(models.Series.runtime, 0),
                )
        ), 0).label('episodes_watched_minutes'),
    ).where(        
        models.Episode_watched.user_id == user.id,
        models.Episode_watched.series_id == series_id,
        models.Episode.series_id == models.Episode_watched.series_id,
        models.Episode.number == models.Episode_watched.episode_number,
        models.Series.id == models.Episode_watched.series_id,
    ))
    return schemas.Series_user_stats.model_validate(q.first())
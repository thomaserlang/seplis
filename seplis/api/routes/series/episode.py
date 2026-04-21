import sqlalchemy as sa
from fastapi import Depends, HTTPException, Security

from ... import models, schemas
from ...dependencies import (
    AsyncSession,
    authenticated,
    get_current_user_no_raise,
    get_expand,
    get_session,
)
from ...expand.episodes import expand_episodes
from .router import router


@router.get('/{series_id}/episodes/{number}', response_model=schemas.Episode)
async def get_episode(
    series_id: int,
    number: int,
    expand: list[str] | None = Depends(get_expand),
    user: User_authenticated | None = Depends(get_current_user_no_raise),
    session: AsyncSession = Depends(get_session),
):
    episode = await session.scalar(
        sa.select(models.MEpisode).where(
            models.MEpisode.series_id == series_id,
            models.MEpisode.number == number,
        )
    )
    if not episode:
        raise HTTPException(404, 'Unknown episode')

    episode = schemas.Episode.model_validate(episode)
    await expand_episodes(
        episodes=[episode], series_id=series_id, user=user, expand=expand
    )
    return episode


@router.delete(
    '/{series_id}/episodes/{number}',
    status_code=204,
    description="""
            **Scope required:** `series:edit`
            """,
)
async def delete_episode(
    series_id: int,
    number: int,
    session: AsyncSession = Depends(get_session),
    user: User_authenticated = Security(authenticated, scopes=['series:edit']),
) -> None:
    await session.execute(
        sa.delete(models.MEpisode).where(
            models.MEpisode.series_id == series_id,
            models.MEpisode.number == number,
        )
    )

import sqlalchemy as sa
from fastapi import Body, Depends, Response, Security

from ... import models, schemas
from ...dependencies import AsyncSession, UserAuthenticated, authenticated, get_session
from .router import router


@router.get(
    '/{movie_id}/watched-position',
    response_model=schemas.Movie_watched,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def get_position(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
    user: UserAuthenticated = Security(authenticated, scopes=['user:progress']),
):
    ew = await session.scalar(
        sa.select(models.MMovieWatched).where(
            models.MMovieWatched.movie_id == movie_id,
            models.MMovieWatched.user_id == user.id,
        )
    )
    if not ew:
        return Response(status_code=204)
    return schemas.Movie_watched.model_validate(ew)


@router.put(
    '/{movie_id}/watched-position',
    status_code=204,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def set_position(
    movie_id: int,
    position: int = Body(..., embed=True, ge=0, le=86400),
    user: UserAuthenticated = Security(authenticated, scopes=['user:progress']),
) -> None:
    await models.MMovieWatched.set_position(
        user_id=user.id,
        movie_id=movie_id,
        position=position,
    )


@router.delete(
    '/{movie_id}/watched-position',
    status_code=204,
    description="""
            **Scope required:** `user:progress`
            """,
)
async def delete_position(
    movie_id: int,
    user: UserAuthenticated = Security(authenticated, scopes=['user:progress']),
) -> None:
    await models.MMovieWatched.reset_position(
        user_id=user.id,
        movie_id=movie_id,
    )

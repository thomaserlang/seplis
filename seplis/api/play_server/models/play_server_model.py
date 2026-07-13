from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis import utils
from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MPlayServer(Base):
    __tablename__ = 'play_servers'

    id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime | None] = mapped_column(UtcDateTime)
    user_id: Mapped[int | None] = mapped_column()
    name: Mapped[str] = mapped_column(sa.String(45))
    url: Mapped[str | None] = mapped_column(sa.String(200))
    secret: Mapped[str | None] = mapped_column(sa.String(200))


class MPlayServerAccess(Base):
    """Users with access to the play server"""

    __tablename__ = 'play_server_access'

    play_server_id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID, primary_key=True)
    user_id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime | None] = mapped_column(UtcDateTime)


class MPlayServerInvite(Base):
    __tablename__ = 'play_server_invites'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'),
        primary_key=True,
    )
    invite_id: Mapped[str] = mapped_column(utils.sqlalchemy.UUID)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MPlayServerMovie(Base):
    __tablename__ = 'play_server_movies'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    movie_id: Mapped[int] = mapped_column(
        sa.ForeignKey('movies.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)


class MPlayServerEpisode(Base):
    __tablename__ = 'play_server_episodes'

    play_server_id: Mapped[str] = mapped_column(
        utils.sqlalchemy.UUID,
        sa.ForeignKey('play_servers.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
    )
    series_id: Mapped[int] = mapped_column(
        sa.ForeignKey('series.id', onupdate='cascade', ondelete='cascade'),
        primary_key=True,
        autoincrement=False,
    )
    episode_number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    updated_at: Mapped[datetime] = mapped_column(UtcDateTime)

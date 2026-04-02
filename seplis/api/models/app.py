from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis import utils
from seplis.utils import datetime_now
from seplis.utils.sqlalchemy import UtcDateTime

from .base import Base


class MApp(Base):
    __tablename__ = 'apps'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column()
    name: Mapped[str | None] = mapped_column(sa.String(45))
    client_id: Mapped[str | None] = mapped_column(sa.String(45))
    client_secret: Mapped[str | None] = mapped_column(sa.String(45))
    redirect_uri: Mapped[str | None] = mapped_column(sa.String(45))
    level: Mapped[int | None] = mapped_column()
    created: Mapped[datetime | None] = mapped_column(UtcDateTime, default=datetime_now)
    updated: Mapped[datetime | None] = mapped_column(UtcDateTime, onupdate=datetime_now)

    def __init__(self, user_id, name, level, redirect_uri=None) -> None:
        """
        :param user_id: int
        :param name: str
        :param level: int
        :param redirect_uri: str
        """
        self.user_id = user_id
        self.name = name
        self.level = level
        self.redirect_uri = redirect_uri
        self.client_id = utils.random_key()
        self.client_secret = utils.random_key()
        self.created = datetime_now()

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis import utils
from seplis.api.models.base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MUserPublic(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(45), unique=True)
    created_at: Mapped[datetime] = mapped_column(UtcDateTime, default=utils.datetime_now)


class MUser(MUserPublic):
    email: Mapped[str] = mapped_column(sa.String(100), unique=True)
    password: Mapped[str] = mapped_column(sa.String(200))
    scopes: Mapped[str] = mapped_column(sa.String(2000), server_default='me')

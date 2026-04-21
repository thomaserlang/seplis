from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.models.base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MToken(Base):
    __tablename__ = 'tokens'

    user_id: Mapped[int | None] = mapped_column(sa.Integer)
    app_id: Mapped[int | None] = mapped_column(sa.Integer)
    token: Mapped[str] = mapped_column(sa.String(2000), primary_key=True)
    expires: Mapped[datetime | None] = mapped_column(UtcDateTime)
    scopes: Mapped[str] = mapped_column(sa.String(2000), server_default='me')

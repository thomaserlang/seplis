from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MResetPassword(Base):
    __tablename__ = 'reset_password'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    key: Mapped[str] = mapped_column(sa.String, primary_key=True)
    expires: Mapped[datetime | None] = mapped_column(UtcDateTime)

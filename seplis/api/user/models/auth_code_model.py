from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.models import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MAuthCode(Base):
    __tablename__ = 'auth_codes'

    code: Mapped[str] = mapped_column(sa.String(255), primary_key=True)
    user_id: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime)
    scopes: Mapped[str] = mapped_column(sa.String(255))

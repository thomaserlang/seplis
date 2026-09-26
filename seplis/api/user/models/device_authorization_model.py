from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis.api.model_base import Base
from seplis.utils.sqlalchemy import UtcDateTime


class MDeviceAuthorization(Base):
    __tablename__ = 'device_authorizations'

    device_code_hash: Mapped[str] = mapped_column(sa.String(64), primary_key=True)
    user_code: Mapped[str] = mapped_column(sa.String(6), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('users.id', ondelete='cascade'), index=True
    )
    scopes: Mapped[str] = mapped_column(sa.String(255))
    created_at: Mapped[datetime] = mapped_column(UtcDateTime)
    expires_at: Mapped[datetime] = mapped_column(UtcDateTime, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(UtcDateTime)

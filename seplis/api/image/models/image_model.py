import urllib.parse
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from seplis import config
from seplis.api.model_base import Base
from seplis.utils import datetime_now
from seplis.utils.sqlalchemy import UtcDateTime


class MImage(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    relation_type: Mapped[str | None] = mapped_column(sa.String(20))
    relation_id: Mapped[int | None] = mapped_column()
    external_name: Mapped[str | None] = mapped_column(sa.String(50))
    external_id: Mapped[str | None] = mapped_column(sa.String(50))
    height: Mapped[int | None] = mapped_column()
    width: Mapped[int | None] = mapped_column()
    file_id: Mapped[str | None] = mapped_column(sa.String(64))
    created_at: Mapped[datetime | None] = mapped_column(UtcDateTime, default=datetime_now)
    type: Mapped[str | None] = mapped_column(sa.String(50))

    @property
    def url(self) -> str:
        return urllib.parse.urljoin(str(config.api.image_url), self.file_id)

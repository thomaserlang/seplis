import sqlalchemy as sa
import io
import urllib.parse
from fastapi import UploadFile
from seplis.utils.sqlalchemy import UtcDateTime
from .base import Base
from ... import config, utils, logger
from .. import schemas, exceptions, models
from ..database import database
from datetime import datetime

class Image(Base):
    __tablename__ = 'images'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    relation_type = sa.Column(sa.String(20))
    relation_id = sa.Column(sa.Integer)
    external_name = sa.Column(sa.String(50))
    external_id = sa.Column(sa.String(50))
    height = sa.Column(sa.Integer)
    width = sa.Column(sa.Integer)
    hash = sa.Column(sa.String(64))
    created_at = sa.Column(UtcDateTime, default=datetime.utcnow)
    type = sa.Column(sa.String(50))

    @property
    def url(self):
        return urllib.parse.urljoin(config.data.api.image_url, self.hash)

    async def save(relation_type: str, relation_id: str, image_data: schemas.Image_import) -> schemas.Image:
        from ..dependencies import httpx_client

        async with database.session() as session:
            if image_data.external_name or image_data.external_id:
                q = await session.scalar(sa.select(models.Image).where(
                    models.Image.external_name == image_data.external_name,
                    models.Image.external_id == image_data.external_id,
                ))
                if q:
                    logger.debug(f'Duplicate image with `external_name`: {image_data.external_name} and `external_id`: {image_data.external_id}, returning stored image')
                    return schemas.Image.from_orm(q)

            if not image_data.file and not image_data.source_url:
                raise exceptions.File_upload_no_files()

            if not image_data.file:
                r = await httpx_client.get(image_data.source_url, follow_redirects=True)
                if r.status_code != 200:
                    logger.error(f'File download of image failed: {r.content}')
                    raise exceptions.API_exception(500, 0, 'Unable to store the image')
                image_data.file = UploadFile(io.BytesIO(r.content), filename=urllib.parse.urlparse(image_data.source_url).path)

            async def upload_bytes():
                while content := await image_data.file.read(128*1024):
                    yield content

            r = await httpx_client.post(
                urllib.parse.urljoin(config.data.api.storitch, '/store/session'),
                headers={
                    'X-Storitch': utils.json_dumps({
                        'finished': True,
                        'filename': image_data.file.filename,
                    }),
                    'content-type': 'application/octet-stream',
                },
                content=upload_bytes()
            )
            if r.status_code != 200:
                logger.error(f'File upload failed: {r.content}')
                raise exceptions.API_exception(500, 0, 'Unable to store the image')
            
            file = utils.json_loads(r.content)
            if file['type'] != 'image':
                raise exceptions.Image_no_data()


            r = await session.execute(sa.insert(models.Image).values(
                relation_type=relation_type,
                relation_id=relation_id,
                external_name=image_data.external_name,
                external_id=image_data.external_id,
                height=file['height'],
                width=file['width'],
                hash=file['hash'],
                type=image_data.type,
            ))
            image = await session.scalar(sa.select(models.Image).where(models.Image.id == r.lastrowid))
            await session.commit()
            return schemas.Image.from_orm(image)
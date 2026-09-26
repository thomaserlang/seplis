import io
import urllib.parse
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, cast

import sqlalchemy as sa
from fastapi import UploadFile
from sqlalchemy.engine import RowMapping

from seplis import config, logger, utils
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.api.dependencies import httpx_client
from seplis.utils import datetime_now

from ..models.image_model import MImage
from ..schemas.image_schemas import IMAGE_TYPES, Image, ImageImport


def image_columns(prefix: str = 'image_') -> tuple[Any, ...]:
    return tuple(
        column.label(f'{prefix}{column.name}') for column in MImage.__table__.columns
    )


def image_mapper(image: RowMapping | MImage, prefix: str = '') -> Image:
    if isinstance(image, MImage):
        file_id = image.file_id or ''
        return Image(
            id=image.id,
            height=image.height or 0,
            width=image.width or 0,
            file_id=file_id,
            type=cast(IMAGE_TYPES, image.type),
            created_at=image.created_at or datetime_now(),
            url=urllib.parse.urljoin(str(config.api.image_url), file_id),
            external_name=image.external_name,
            external_id=image.external_id,
        )

    file_id = image[f'{prefix}file_id'] or ''
    return Image(
        id=image[f'{prefix}id'],
        height=image[f'{prefix}height'] or 0,
        width=image[f'{prefix}width'] or 0,
        file_id=file_id,
        type=cast(IMAGE_TYPES, image[f'{prefix}type']),
        created_at=image[f'{prefix}created_at'] or datetime_now(),
        url=urllib.parse.urljoin(str(config.api.image_url), file_id),
        external_name=image[f'{prefix}external_name'],
        external_id=image[f'{prefix}external_id'],
    )


async def save_image(
    relation_type: str,
    relation_id: str | int,
    image_data: ImageImport,
    session: AsyncSession | None = None,
) -> Image:
    data = dict(image_data)
    async with get_session(session) as session:
        if data.get('external_name') or data.get('external_id'):
            existing = (
                (
                    await session.execute(
                        sa.select(MImage.__table__).where(
                            MImage.external_name == data.get('external_name'),
                            MImage.external_id == data.get('external_id'),
                        )
                    )
                )
                .mappings()
                .first()
            )
            if existing:
                logger.debug(
                    'Duplicate image with `external_name`: '
                    f'{data.get("external_name")} and `external_id`: '
                    f'{data.get("external_id")}, returning stored image'
                )
                return image_mapper(existing)

        file = cast(UploadFile | None, data.get('file'))
        source_url = cast(str | None, data.get('source_url'))

        if not file and not source_url:
            raise exceptions.FileUploadNoFiles()

        if not file and source_url:
            response = await httpx_client.get(source_url, follow_redirects=True)
            if response.status_code != 200:
                logger.error(f'File download of image failed: {response.content}')
                raise exceptions.APIException(500, 0, 'Unable to store the image')
            file = UploadFile(
                io.BytesIO(response.content),
                filename=urllib.parse.urlparse(source_url).path,
            )

        if not file:
            raise exceptions.FileUploadNoFiles()

        async def upload_bytes() -> AsyncIterator[bytes]:
            while content := await file.read(128 * 1024):
                yield content

        response = await httpx_client.post(
            urllib.parse.urljoin(str(config.api.storitch_host), '/store/session'),
            headers={
                'X-Storitch': utils.json_dumps(
                    {
                        'finished': True,
                        'filename': file.filename,
                    }
                ),
                'content-type': 'application/octet-stream',
                'authorization': config.api.storitch_api_key,
            },
            content=upload_bytes(),
        )
        if response.status_code >= 400:
            logger.error(f'File upload failed: {response.content}')
            raise exceptions.APIException(500, 0, 'Unable to store the image')

        stored_file = utils.json_loads(response.content)
        if stored_file['type'] != 'image':
            raise exceptions.ImageNoData()

        result = cast(
            Any,
            await session.execute(
                sa.insert(cast(sa.Table, MImage.__table__)).values(
                    relation_type=relation_type,
                    relation_id=relation_id,
                    external_name=data.get('external_name'),
                    external_id=data.get('external_id'),
                    height=stored_file['height'],
                    width=stored_file['width'],
                    file_id=stored_file['file_id'],
                    type=data['type'],
                    created_at=datetime.now().astimezone(),
                )
            ),
        )
        image = (
            (
                await session.execute(
                    sa.select(MImage.__table__).where(MImage.id == result.lastrowid)
                )
            )
            .mappings()
            .first()
        )
        if not image:
            raise exceptions.ImageUnknown()
        return image_mapper(image)

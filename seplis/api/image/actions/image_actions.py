import io
import urllib.parse
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, cast

import sqlalchemy as sa
from fastapi import UploadFile

from seplis import config, logger, utils
from seplis.api import exceptions
from seplis.api.contexts import AsyncSession, get_session
from seplis.utils import datetime_now

from ..models.image_model import MImage
from ..schemas.image_schemas import IMAGE_TYPES, Image, ImageImport


def image_mapper(image: MImage) -> Image:
    return Image(
        id=image.id,
        height=image.height or 0,
        width=image.width or 0,
        file_id=image.file_id or '',
        type=cast(IMAGE_TYPES, image.type),
        created_at=image.created_at or datetime_now(),
        url=image.url,
        external_name=image.external_name,
        external_id=image.external_id,
    )


async def save_image(
    relation_type: str,
    relation_id: str | int,
    image_data: ImageImport,
    session: AsyncSession | None = None,
) -> Image:
    from seplis.api.dependencies import httpx_client

    data = dict(image_data)
    async with get_session(session) as session:
        if data.get('external_name') or data.get('external_id'):
            existing = await session.scalar(
                sa.select(MImage).where(
                    MImage.external_name == data.get('external_name'),
                    MImage.external_id == data.get('external_id'),
                )
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
                sa.insert(MImage.__table__).values(  # type: ignore
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
        image = await session.scalar(
            sa.select(MImage).where(MImage.id == result.lastrowid)
        )
        if not image:
            raise exceptions.ImageUnknown()
        return image_mapper(image)

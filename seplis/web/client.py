from httpx import AsyncClient

from seplis import config

client = AsyncClient(
    base_url=str(config.client.api_url),
)
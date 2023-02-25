from httpx import AsyncClient
from seplis import config, logger

client = AsyncClient(
    base_url=config.data.client.api_url,
)
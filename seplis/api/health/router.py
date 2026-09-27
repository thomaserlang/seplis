from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('')
async def check_health() -> dict[str, str]:
    return {'status': 'ok'}

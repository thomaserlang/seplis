from fastapi import APIRouter, HTTPException
from . import transcoders

router = APIRouter()

@router.get('/close-session/{session}', status_code=204)
async def get_close_session(session: str):    
    if session not in transcoders.video.sessions:
        raise HTTPException(404, 'Unknown session')

    transcoders.video.close_session(session)
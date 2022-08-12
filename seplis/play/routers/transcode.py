from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from ..dependencies import get_metadata
from ..transcoders.video import Transcode_settings, Transcoder
from ..transcoders import dash, pipe, hls

router = APIRouter()

@router.get('/transcode')
async def start_transcode(
    source_index: int, 
    metadata = Depends(get_metadata), 
    settings: Transcode_settings = Depends(),
):
    if not metadata:
        raise HTTPException(404, 'No metadata')
    
    if settings.format == 'hls':
        cls = hls.Hls_transcoder
    elif settings.format == 'dash':
        cls = dash.Dash_transcoder
    else:
        raise HTTPException(400, 'Unknown format')
    
    player: Transcoder = cls(settings=settings, metadata=list(metadata)[source_index])
    ready = await player.start()
    if ready == False:
        raise HTTPException(400, 'Transcode failed to start')
    return RedirectResponse(f'/files/{settings.session}/{player.media_name}')

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import logging

from app.services.terminal import TerminalService, TerminalResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/terminal", tags=["Terminal"])

class TerminalRequest(BaseModel):
    command: str
    shell: str = "bash"
    user_id: str = "unknown"
    role: str = "Unauthorized"

@router.post("/exec", response_model=TerminalResponse)
async def execute_command(request: TerminalRequest):
    """
    Execute a system command safely using the Semantic Shell engine.
    """
    logger.info(f"🐚 Terminal Execution Request: '{request.command}' (Role: {request.role})")
    
    service = TerminalService()
    result = await service.execute(
        command=request.command,
        shell_type=request.shell,
        user_role=request.role
    )
    
    return result

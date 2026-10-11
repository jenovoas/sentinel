"""
AI Autonomous Tools - File System & Command Execution
Provides the AI with controlled access to read/write files and execute commands.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import subprocess
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai/tools", tags=["AI Tools"])

# Security: Only allow operations within Sentinel directory
ALLOWED_BASE_PATH = Path("/home/jnovoas/sentinel")

# Dangerous commands that should never be executed
BLOCKED_COMMANDS = [
    'rm -rf /',
    'dd if=',
    'mkfs',
    ':(){:|:&};:',  # Fork bomb
    'chmod -R 777 /',
    '> /dev/sda',
    'wget http',  # Block arbitrary downloads
    'curl http',  # Block arbitrary requests (use SEARCH instead)
]


class WriteFileRequest(BaseModel):
    path: str
    content: str


class ExecuteCommandRequest(BaseModel):
    command: str
    cwd: Optional[str] = None


class ReadFileRequest(BaseModel):
    path: str


def validate_path(path: str) -> Path:
    """Validate that path is within allowed directory"""
    abs_path = Path(path).resolve()
    
    if not str(abs_path).startswith(str(ALLOWED_BASE_PATH)):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Path must be within {ALLOWED_BASE_PATH}"
        )
    
    return abs_path


def validate_command(command: str) -> None:
    """Validate that command is not dangerous"""
    command_lower = command.lower()
    
    for blocked in BLOCKED_COMMANDS:
        if blocked in command_lower:
            raise HTTPException(
                status_code=403,
                detail=f"Blocked dangerous command pattern: {blocked}"
            )


@router.post("/write")
async def write_file(request: WriteFileRequest):
    """
    Write content to a file.
    
    Security:
    - Only allows writing within /home/jnovoas/sentinel
    - Creates parent directories if needed
    """
    try:
        file_path = validate_path(request.path)
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path.write_text(request.content)
        
        logger.info(f"AI wrote file: {file_path}")
        
        return {
            "status": "success",
            "path": str(file_path),
            "bytes_written": len(request.content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/read")
async def read_file(request: ReadFileRequest):
    """
    Read content from a file.
    
    Security:
    - Only allows reading within /home/jnovoas/sentinel
    """
    try:
        file_path = validate_path(request.path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        content = file_path.read_text()
        
        logger.info(f"AI read file: {file_path}")
        
        return {
            "status": "success",
            "path": str(file_path),
            "content": content,
            "size_bytes": len(content)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_command(request: ExecuteCommandRequest):
    """
    Execute a shell command.
    
    Security:
    - Blocks dangerous commands
    - 30 second timeout
    - Only executes within Sentinel directory
    """
    try:
        validate_command(request.command)
        
        # Validate working directory
        cwd = ALLOWED_BASE_PATH
        if request.cwd:
            cwd = validate_path(request.cwd)
            if not cwd.is_dir():
                raise HTTPException(status_code=400, detail="Working directory does not exist")
        
        logger.info(f"AI executing command: {request.command} in {cwd}")
        
        # Execute command
        result = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cwd)
        )
        
        return {
            "status": "success",
            "command": request.command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "cwd": str(cwd)
        }
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timeout (30s)")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list_dir")
async def list_directory(path: str = "/home/jnovoas/sentinel"):
    """
    List contents of a directory.
    
    Security:
    - Only allows listing within /home/jnovoas/sentinel
    """
    try:
        dir_path = validate_path(path)
        
        if not dir_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        # List directory contents
        entries = []
        for item in dir_path.iterdir():
            entries.append({
                "name": item.name,
                "path": str(item),
                "is_file": item.is_file(),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None
            })
        
        return {
            "status": "success",
            "path": str(dir_path),
            "entries": entries,
            "count": len(entries)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

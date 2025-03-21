from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.modules.system import SystemModule
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Initialize system module
system_module = SystemModule()

# Request and response models
class CommandRequest(BaseModel):
    command: str
    timeout: Optional[int] = None
    shell: bool = True

class ApplicationRequest(BaseModel):
    app_name: str

class SystemInfoResponse(BaseModel):
    success: bool
    cpu: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None
    disk: Optional[Dict[str, Any]] = None
    platform: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ProcessesResponse(BaseModel):
    success: bool
    processes: List[Dict[str, Any]] = []
    count: int = 0
    error: Optional[str] = None

class ApplicationsResponse(BaseModel):
    success: bool
    applications: List[Dict[str, Any]] = []
    count: int = 0
    error: Optional[str] = None

# Endpoints
@router.post("/execute")
async def execute_command(request: CommandRequest):
    """Execute a system command"""
    try:
        logger.info(f"Executing command: {request.command}")
        result = system_module.execute_command(
            command=request.command,
            timeout=request.timeout,
            shell=request.shell
        )
        return result
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@router.post("/launch")
async def launch_application(request: ApplicationRequest):
    """Launch an application"""
    try:
        logger.info(f"Launching application: {request.app_name}")
        result = system_module.launch_application(request.app_name)
        return result
    except Exception as e:
        logger.error(f"Error launching application: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to launch application: {str(e)}")

@router.get("/applications", response_model=ApplicationsResponse)
async def list_applications():
    """List installed applications"""
    try:
        logger.info("Listing installed applications")
        result = system_module.list_applications()
        return result
    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}", exc_info=True)
        return ApplicationsResponse(
            success=False,
            error=str(e),
            applications=[],
            count=0
        )

@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info():
    """Get system information"""
    try:
        logger.info("Getting system information")
        result = system_module.get_system_info()
        return result
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}", exc_info=True)
        return SystemInfoResponse(
            success=False,
            error=str(e)
        )

@router.get("/processes", response_model=ProcessesResponse)
async def get_running_processes():
    """Get list of running processes"""
    try:
        logger.info("Getting running processes")
        result = system_module.get_running_processes()
        return result
    except Exception as e:
        logger.error(f"Error getting running processes: {str(e)}", exc_info=True)
        return ProcessesResponse(
            success=False,
            error=str(e),
            processes=[],
            count=0
        )

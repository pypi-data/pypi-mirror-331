"""
API routes for system information and server health
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Tuple
import time
import psutil
import torch
import platform
from datetime import datetime
import gc

from ..logger import get_logger
from ..logger.logger import get_request_count, get_uptime_seconds
from ..core.app import model_manager, start_time
from ..ui.banners import print_system_resources
from ..config import system_instructions
from ..utils.system import get_gpu_info as utils_get_gpu_info
from ..utils.networking import get_public_ip, get_network_interfaces

# Get logger
logger = get_logger("locallab.routes.system")

# Create router
router = APIRouter(tags=["System"])


class SystemInfoResponse(BaseModel):
    """Response model for system information"""
    cpu_usage: float
    memory_usage: float
    gpu_info: Optional[List[Dict[str, Any]]] = None
    active_model: Optional[str] = None
    uptime: float
    request_count: int


class SystemInstructionsRequest(BaseModel):
    """Request model for updating system instructions"""
    instructions: str
    model_id: Optional[str] = None


class SystemResourcesResponse(BaseModel):
    """Response model for system resources"""
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    gpu: Optional[List[Dict[str, Any]]] = None
    disk: Dict[str, Any]
    platform: str
    server_uptime: float
    api_requests: int


class MemoryStatsResponse(BaseModel):
    """Response model for detailed memory statistics"""
    ram: Dict[str, Any]
    gpu: Optional[List[Dict[str, Any]]] = None
    model_memory: Optional[Dict[str, Any]] = None
    peak_usage: Dict[str, Any]
    loading_stats: Optional[Dict[str, Any]] = None


class MemoryHistoryResponse(BaseModel):
    """Response model for memory history data"""
    timestamps: List[float]
    ram_usage: List[float]
    gpu_usage: List[float]
    interval_seconds: int
    points_count: int
    monitoring_active: bool


def get_gpu_memory() -> Optional[Tuple[int, int]]:
    """Get GPU memory info in MB"""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return (info.total // 1024 // 1024, info.free // 1024 // 1024)
    except Exception as e:
        logger.debug(f"Failed to get GPU memory: {str(e)}")
        return None


@router.post("/system/instructions")
async def update_system_instructions(request: SystemInstructionsRequest) -> Dict[str, str]:
    """Update system instructions"""
    try:
        if request.model_id:
            system_instructions.set_model_instructions(request.model_id, request.instructions)
            return {"message": f"Updated system instructions for model {request.model_id}"}
        else:
            system_instructions.set_global_instructions(request.instructions)
            return {"message": "Updated global system instructions"}
    except Exception as e:
        logger.error(f"Failed to update system instructions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/instructions")
async def get_system_instructions(model_id: Optional[str] = None) -> Dict[str, Any]:
    """Get current system instructions"""
    return {
        "instructions": system_instructions.get_instructions(model_id),
        "model_id": model_id if model_id else "global"
    }


@router.post("/system/instructions/reset")
async def reset_system_instructions(model_id: Optional[str] = None) -> Dict[str, str]:
    """Reset system instructions to default"""
    system_instructions.reset_instructions(model_id)
    return {
        "message": f"Reset system instructions for {'model ' + model_id if model_id else 'all models'}"
    }


@router.get("/system/info", response_model=SystemInfoResponse)
async def get_system_info():
    """Get system information including CPU, memory, GPU usage, and server stats"""
    try:
        # Get CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get GPU info if available
        gpu_info = utils_get_gpu_info() if torch.cuda.is_available() else None
        
        # Get server stats
        uptime = time.time() - start_time
        
        # Return combined info
        return SystemInfoResponse(
            cpu_usage=cpu_percent,
            memory_usage=memory_percent,
            gpu_info=gpu_info,
            active_model=model_manager.current_model,
            uptime=uptime,
            request_count=get_request_count()  # Use the function from logger.logger instead
        )
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/startup-status")
async def startup_status() -> Dict[str, Any]:
    """Get detailed startup status including model loading progress"""
    return {
        "server_ready": True,
        "model_loading": model_manager.is_loading() if hasattr(model_manager, "is_loading") else False,
        "current_model": model_manager.current_model,
        "uptime": time.time() - start_time
    }


@router.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with basic server information"""
    from .. import __version__
    
    # Get system resources
    resources = get_system_resources()
    
    # Print system resources to console
    print_system_resources(resources)
    
    # Return server info
    return {
        "name": "LocalLab",
        "version": __version__,
        "status": "running",
        "model": model_manager.current_model,
        "uptime": time.time() - start_time,
        "resources": resources
    }


@router.get("/resources", response_model=SystemResourcesResponse)
async def get_system_resources() -> SystemResourcesResponse:
    """Get system resource information"""
    disk = psutil.disk_usage('/')
    uptime = time.time() - start_time
    
    # Get detailed GPU information
    gpu_info = utils_get_gpu_info()
    
    return SystemResourcesResponse(
        cpu={
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "usage": psutil.cpu_percent(interval=0.1),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
        },
        memory={
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent
        },
        gpu=gpu_info,
        disk={
            "total": disk.total,
            "free": disk.free,
            "used": disk.used,
            "percent": disk.percent
        },
        platform=platform.platform(),
        server_uptime=uptime,
        api_requests=get_request_count()
    )


@router.get("/network", response_model=Dict[str, Any])
async def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    try:
        public_ip = await get_public_ip()
    except:
        public_ip = "Unknown"
        
    return {
        "public_ip": public_ip,
        "hostname": platform.node(),
        "interfaces": get_network_interfaces()
    }


def get_system_resources() -> Dict[str, Any]:
    """Get system resource information"""
    try:
        import torch
        torch_available = True
    except ImportError:
        torch_available = False
    
    # Get memory information
    virtual_memory = psutil.virtual_memory()
    ram_gb = virtual_memory.total / 1024 / 1024 / 1024
    ram_available_gb = virtual_memory.available / 1024 / 1024 / 1024
    
    resources = {
        "ram_gb": ram_gb,
        "ram_available_gb": ram_available_gb, 
        "ram_used_percent": virtual_memory.percent,
        "cpu_count": psutil.cpu_count(),
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "gpu_available": torch_available and torch.cuda.is_available() if torch_available else False,
        "gpu_info": []
    }
    
    # Use the new gpu_info function from utils.system for more detailed GPU info
    if resources['gpu_available']:
        resources['gpu_info'] = utils_get_gpu_info()
    
    return resources


@router.get("/memory-stats", response_model=MemoryStatsResponse)
async def get_memory_stats() -> MemoryStatsResponse:
    """
    Get detailed memory usage statistics for the server and models
    
    Returns:
        Detailed memory usage statistics including RAM, GPU, and model memory
    """
    from ..utils.system import get_memory_info, get_gpu_info
    from ..core.app import model_manager
    import gc
    import torch
    import sys
    
    # Get basic memory information
    memory_info = get_memory_info()
    
    # Get GPU information if available
    gpu_info = None
    try:
        gpu_info = get_gpu_info()
    except Exception as e:
        logger.warning(f"Failed to get GPU info: {str(e)}")
    
    # Get model memory information if a model is loaded
    model_memory = None
    if model_manager.model is not None and model_manager.current_model:
        # More accurate model memory calculation
        try:
            # Calculate model size in parameters
            parameter_count = sum(p.numel() for p in model_manager.model.parameters())
            
            # Calculate model size in bytes (more accurately)
            model_size_bytes = sum(p.numel() * p.element_size() for p in model_manager.model.parameters())
            model_size_mb = model_size_bytes / (1024 * 1024)
            
            # Get activation memory by multiplying parameters by a constant factor (estimate)
            activation_memory_mb = model_size_mb * 0.2  # Rough estimate for activation memory
            
            # Memory consumption with gradient (if training enabled)
            gradient_memory_mb = model_size_mb if any(p.requires_grad for p in model_manager.model.parameters()) else 0
            
            # Total model memory consumption
            total_model_memory_mb = model_size_mb + activation_memory_mb + gradient_memory_mb
            
            model_memory = {
                "model_id": model_manager.current_model,
                "parameter_count": parameter_count,
                "parameters_millions": parameter_count / 1_000_000,
                "model_size_mb": round(model_size_mb, 2),
                "activation_memory_mb": round(activation_memory_mb, 2),
                "gradient_memory_mb": round(gradient_memory_mb, 2),
                "total_model_memory_mb": round(total_model_memory_mb, 2),
                "loaded_time": time.time() - model_manager.last_used if hasattr(model_manager, "last_used") else None,
            }
            
            # Add tokenizer memory if available
            if hasattr(model_manager, "tokenizer") and model_manager.tokenizer is not None:
                # Rough estimate of tokenizer size
                tokenizer_size = sys.getsizeof(model_manager.tokenizer) / (1024 * 1024)
                model_memory["tokenizer_size_mb"] = round(tokenizer_size, 2)
                
        except Exception as e:
            logger.warning(f"Error calculating detailed model memory: {str(e)}")
            
            # Fallback to basic model size calculation
            try:
                model_size = sys.getsizeof(model_manager.model) / (1024 * 1024)
                model_memory = {
                    "model_id": model_manager.current_model,
                    "parameter_count": model_manager.parameter_count if hasattr(model_manager, "parameter_count") else None,
                    "model_size_mb": round(model_size, 2)
                }
            except Exception as inner_e:
                logger.warning(f"Fallback model size calculation also failed: {str(inner_e)}")
    
    # Get peak memory usage
    peak_usage = {
        "ram_mb": memory_info["percent_used"],
    }
    
    # Add GPU peak if available
    if gpu_info and len(gpu_info) > 0:
        peak_usage["gpu_mb"] = max([gpu["memory_used"] for gpu in gpu_info]) if gpu_info else 0
    
    # Get loading statistics if tracked
    loading_stats = None
    if hasattr(model_manager, "loading_stats"):
        loading_stats = model_manager.loading_stats
    
    # Check for potential memory leaks
    memory_leak_detected = False
    leak_info = None
    
    # Check memory trend from memory history
    from ..core.app import memory_history
    if len(memory_history["ram_usage"]) > 10:
        # Get last 10 measurements
        last_10_ram = memory_history["ram_usage"][-10:]
        # Check if RAM has been steadily increasing
        if all(last_10_ram[i] < last_10_ram[i+1] for i in range(len(last_10_ram)-1)):
            memory_leak_detected = True
            leak_info = {
                "description": "Possible memory leak detected - RAM usage has been steadily increasing",
                "last_values_mb": last_10_ram,
                "increase_percent": ((last_10_ram[-1] - last_10_ram[0]) / last_10_ram[0]) * 100 if last_10_ram[0] > 0 else 0
            }
    
    # Add leak info to the response
    if memory_leak_detected and leak_info:
        peak_usage["leak_detected"] = True
        peak_usage["leak_info"] = leak_info
    
    # Force garbage collection to report accurate memory 
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return MemoryStatsResponse(
        ram=memory_info,
        gpu=gpu_info,
        model_memory=model_memory,
        peak_usage=peak_usage,
        loading_stats=loading_stats
    )


@router.get("/memory-history", response_model=MemoryHistoryResponse)
async def get_memory_history() -> MemoryHistoryResponse:
    """
    Get historical memory usage data for monitoring
    
    Returns:
        Historical memory usage data including timestamps, RAM usage, and GPU usage
    """
    from ..core.app import memory_history, monitoring_active, monitoring_interval
    
    return MemoryHistoryResponse(
        timestamps=memory_history["timestamps"],
        ram_usage=memory_history["ram_usage"],
        gpu_usage=memory_history["gpu_usage"],
        interval_seconds=monitoring_interval,
        points_count=len(memory_history["timestamps"]),
        monitoring_active=monitoring_active
    )


@router.post("/memory-monitor/toggle", response_model=Dict[str, Any])
async def toggle_memory_monitoring(
    active: bool = True,
    interval: Optional[int] = None
) -> Dict[str, Any]:
    """
    Toggle memory monitoring on/off and adjust monitoring interval
    
    Args:
        active: Whether to activate memory monitoring
        interval: Monitoring interval in seconds (optional)
        
    Returns:
        Updated monitoring status
    """
    from ..core.app import memory_history
    import sys
    
    # Import as module attributes, not globals in this function
    from ..core.app import monitoring_active as app_monitoring_active
    from ..core.app import monitoring_interval as app_monitoring_interval
    
    # Update monitoring status in the app module
    # We're accessing the module's globals directly to avoid using global in this function
    import locallab.core.app
    locallab.core.app.monitoring_active = active
    
    # Update interval if provided
    if interval is not None and interval > 0:
        locallab.core.app.monitoring_interval = interval
    
    # Clear history if monitoring is being turned off
    if not active:
        memory_history["timestamps"] = []
        memory_history["ram_usage"] = []
        memory_history["gpu_usage"] = []
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    return {
        "monitoring_active": locallab.core.app.monitoring_active,
        "interval_seconds": locallab.core.app.monitoring_interval,
        "memory_history_points": len(memory_history["timestamps"]),
        "python_version": sys.version
    }
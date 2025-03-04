"""
Core FastAPI application setup for LocalLab
"""

import time
import logging
import asyncio
import gc
import torch
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import contextmanager
from colorama import Fore, Style
from ..logger import get_logger
from ..logger.logger import log_request, log_model_loaded, log_model_unloaded, get_request_count, SERVER_START_TIME
from ..model_manager import ModelManager
from ..config import (
    ENABLE_CORS,
    CORS_ORIGINS,
    DEFAULT_MODEL,
    ENABLE_COMPRESSION,
    QUANTIZATION_TYPE,
)

# Try to import FastAPICache, but don't fail if not available
try:
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.inmemory import InMemoryBackend
    FASTAPI_CACHE_AVAILABLE = True
except ImportError:
    FASTAPI_CACHE_AVAILABLE = False
    # Create dummy FastAPICache to avoid errors
    class DummyFastAPICache:
        @staticmethod
        def init(backend, **kwargs):
            pass
    FastAPICache = DummyFastAPICache

from .. import __version__
from ..logger import get_logger
from ..logger.logger import log_request, log_model_loaded, log_model_unloaded, get_request_count
from ..model_manager import ModelManager
from ..config import (
    ENABLE_CORS,
    CORS_ORIGINS,
    DEFAULT_MODEL,
    ENABLE_COMPRESSION,
    QUANTIZATION_TYPE,
)

# Get the logger
logger = get_logger("locallab.app")

# Track server start time
start_time = time.time()

# Create a semaphore to limit concurrent model operations
model_semaphore = asyncio.Semaphore(1)  # Allow only one model operation at a time

# Memory monitoring variables
memory_history = {
    "timestamps": [],
    "ram_usage": [],
    "gpu_usage": []
}
monitoring_active = False
monitoring_interval = 300  # seconds (5 minutes)

# Initialize FastAPI app
app = FastAPI(
    title="LocalLab",
    description="A lightweight AI inference server for running models locally or in Google Colab",
    version=__version__
)

# Configure CORS
if ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add GZip compression middleware for large responses
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses larger than 1KB

# Initialize model manager (imported by routes)
model_manager = ModelManager()

# Import all routes (after app initialization to avoid circular imports)
from ..routes.models import router as models_router
from ..routes.generate import router as generate_router
from ..routes.system import router as system_router

# Include all routers
app.include_router(models_router)
app.include_router(generate_router)
app.include_router(system_router)


@app.on_event("startup")
async def startup_event():
    """Initialization tasks when the server starts"""
    logger.debug("Initializing LocalLab server...")
    
    # Initialize cache if available
    if FASTAPI_CACHE_AVAILABLE:
        FastAPICache.init(InMemoryBackend(), prefix="locallab-cache")
        logger.info("FastAPICache initialized")
    else:
        logger.warning("FastAPICache not available, caching disabled")
    
    # Check for model specified in environment variables (prioritize HUGGINGFACE_MODEL)
    model_to_load = os.environ.get("HUGGINGFACE_MODEL", DEFAULT_MODEL)
    
    # Log model configuration
    logger.debug("Model configuration:")
    logger.debug(" - Model to load: %s", model_to_load)
    logger.debug(f" - Quantization: {'Enabled - ' + os.environ.get('LOCALLAB_QUANTIZATION_TYPE', QUANTIZATION_TYPE) if os.environ.get('LOCALLAB_ENABLE_QUANTIZATION', '').lower() == 'true' else 'Disabled'}")
    logger.debug(f" - Attention slicing: {'Enabled' if os.environ.get('LOCALLAB_ENABLE_ATTENTION_SLICING', '').lower() == 'true' else 'Disabled'}")
    logger.debug(f" - Flash attention: {'Enabled' if os.environ.get('LOCALLAB_ENABLE_FLASH_ATTENTION', '').lower() == 'true' else 'Disabled'}")
    logger.debug(f" - Better transformer: {'Enabled' if os.environ.get('LOCALLAB_ENABLE_BETTERTRANSFORMER', '').lower() == 'true' else 'Disabled'}")
    
    # Start loading the model in background if specified
    if model_to_load:
        try:
            # This will run asynchronously without blocking server startup
            asyncio.create_task(load_model_in_background(model_to_load))
        except Exception as e:
            logger.error(f"Error starting model loading task: {str(e)}")
    else:
        logger.warning("No model specified to load on startup. Use the /models/load endpoint to load a model.")

    # Start memory monitoring in the background
    asyncio.create_task(periodic_memory_monitor())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks when the server shuts down"""
    logger.info(f"{Fore.YELLOW}Shutting down server...{Style.RESET_ALL}")
    
    # Unload model to free GPU memory
    try:
        # Get current model ID before unloading
        current_model = model_manager.current_model
        
        # Unload the model
        if hasattr(model_manager, 'unload_model'):
            model_manager.unload_model()
        else:
            # Fallback if unload_model method doesn't exist
            model_manager.model = None
            model_manager.current_model = None
            
        # Clean up memory
        torch.cuda.empty_cache()
        gc.collect()
        
        # Log model unloading
        if current_model:
            log_model_unloaded(current_model)
            
        logger.info("Model unloaded and memory freed")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")
    
    logger.info(f"{Fore.GREEN}Server shutdown complete{Style.RESET_ALL}")

    global monitoring_active
    monitoring_active = False


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to track request processing time"""
    start_time = time.time()
    
    # Extract path and some basic params for logging
    path = request.url.path
    method = request.method
    client = request.client.host if request.client else "unknown"
    
    # Skip detailed logging for health check endpoints to reduce noise
    is_health_check = path.endswith("/health") or path.endswith("/startup-status")
    
    if not is_health_check:
        log_request(f"{method} {path}", {"client": client})
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    # Add request stats to response headers
    response.headers["X-Request-Count"] = str(get_request_count())
    
    # Log slow requests for performance monitoring (if not a health check)
    if process_time > 1.0 and not is_health_check:
        logger.warning(f"Slow request: {method} {path} took {process_time:.2f}s")
        
    return response


async def load_model_in_background(model_id: str):
    """Load the model asynchronously in the background"""
    logger.info(f"Loading model {model_id} in background...")
    start_time = time.time()
    
    try:
        # Use semaphore to prevent multiple concurrent model loads
        async with model_semaphore:
            logger.info(f"Acquired model semaphore, starting to load {model_id}...")
            
            # Wait for the model to load
            await model_manager.load_model(model_id)
            
            # Calculate load time
            load_time = time.time() - start_time
            
            # We don't need to call log_model_loaded here since it's already done in the model_manager
            logger.info(f"{Fore.GREEN}Model {model_id} loaded successfully in {load_time:.2f} seconds!{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Failed to load model {model_id}: {str(e)}")


async def periodic_memory_monitor():
    """Periodically monitor memory usage to identify potential memory leaks"""
    global monitoring_active, memory_history
    
    if monitoring_active:
        return
        
    monitoring_active = True
    logger.info("Starting periodic memory monitoring")
    
    try:
        while monitoring_active:
            # Record current memory usage
            try:
                import psutil
                process = psutil.Process()
                ram_usage = process.memory_info().rss / (1024 * 1024)  # MB
                
                gpu_usage = 0
                if torch.cuda.is_available():
                    try:
                        from ..utils.system import get_gpu_memory
                        gpu_mem = get_gpu_memory()
                        if gpu_mem and len(gpu_mem) > 0:
                            gpu_usage = gpu_mem[1] if len(gpu_mem) > 1 else gpu_mem[0]  # Used memory
                    except Exception as e:
                        logger.warning(f"Failed to get GPU memory during monitoring: {str(e)}")
                
                # Add to history - use server_start_time which is defined at module level
                timestamp = time.time() - SERVER_START_TIME  # seconds since server start
                memory_history["timestamps"].append(timestamp)
                memory_history["ram_usage"].append(ram_usage)
                memory_history["gpu_usage"].append(gpu_usage)
                
                # Keep only the last 1000 measurements to avoid memory buildup
                if len(memory_history["timestamps"]) > 1000:
                    memory_history["timestamps"] = memory_history["timestamps"][-1000:]
                    memory_history["ram_usage"] = memory_history["ram_usage"][-1000:]
                    memory_history["gpu_usage"] = memory_history["gpu_usage"][-1000:]
                
                # Check if memory is steadily increasing (possible leak)
                if len(memory_history["ram_usage"]) > 10:
                    # Check last 10 measurements
                    last_10_ram = memory_history["ram_usage"][-10:]
                    if all(last_10_ram[i] < last_10_ram[i+1] for i in range(len(last_10_ram)-1)):
                        # RAM usage has been steadily increasing for the last 10 measurements
                        logger.warning(f"Possible memory leak detected! RAM usage has been steadily increasing: {last_10_ram[-1]:.2f}MB")
                        # Try to free memory
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                
            except Exception as e:
                logger.error(f"Error in memory monitoring: {str(e)}")
            
            # Wait for next interval
            await asyncio.sleep(monitoring_interval)
            
    except asyncio.CancelledError:
        logger.info("Memory monitoring task cancelled")
    finally:
        monitoring_active = False 
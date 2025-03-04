"""
Server startup and management functionality for LocalLab
"""

import asyncio
import signal
import sys
import time
import threading
import traceback
import socket
import uvicorn
import os
from colorama import Fore, Style, init
init(autoreset=True)

from typing import Optional, Dict, List, Tuple
from . import __version__
from .utils.networking import is_port_in_use, setup_ngrok
from .ui.banners import (
    print_initializing_banner, 
    print_running_banner, 
    print_system_resources,
    print_model_info,
    print_api_docs,
    print_system_instructions
)
from .logger import get_logger
from .logger.logger import set_server_status, log_request
from .utils.system import get_gpu_memory
from .config import (
    MIN_FREE_MEMORY
)

# Import torch - handle import error gracefully
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Get the logger instance
logger = get_logger("locallab.server")


def check_environment() -> List[Tuple[str, str, bool]]:
    """
    Check the environment for potential issues
    
    Returns:
        List of (issue, suggestion, is_critical) tuples
    """
    issues = []
    
    # Check Python version
    py_version = sys.version_info
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        issues.append((
            f"Python version {py_version.major}.{py_version.minor} is below recommended 3.8+",
            "Consider upgrading to Python 3.8 or newer for better compatibility",
            False
        ))
    
    # Check for Colab environment
    try:
        import google.colab
        in_colab = True
    except ImportError:
        in_colab = False
    
    # Check for ngrok token if in Colab
    if in_colab:
        if not os.environ.get("NGROK_AUTH_TOKEN"):
            issues.append((
                "Running in Google Colab without NGROK_AUTH_TOKEN set",
                "Set os.environ['NGROK_AUTH_TOKEN'] = 'your_token' for public URL access. Get your token from https://dashboard.ngrok.com/get-started/your-authtoken",
                True
            ))
        
        # Check Colab runtime type for GPU
        if TORCH_AVAILABLE and not torch.cuda.is_available():
            issues.append((
                "Running in Colab without GPU acceleration",
                "Change runtime type to GPU: Runtime > Change runtime type > Hardware accelerator > GPU",
                True
            ))
        elif not TORCH_AVAILABLE:
            issues.append((
                "PyTorch is not installed",
                "Install PyTorch with: pip install torch",
                True
            ))
    
    # Check for CUDA and GPU availability
    if TORCH_AVAILABLE:
        if not torch.cuda.is_available():
            issues.append((
                "CUDA is not available - using CPU for inference",
                "This will be significantly slower. Consider using a GPU for better performance",
                False
            ))
        else:
            # Check GPU memory
            try:
                gpu_info = get_gpu_memory()
                if gpu_info:
                    total_mem, free_mem = gpu_info
                    if free_mem < 2000:  # Less than 2GB free
                        issues.append((
                            f"Low GPU memory: Only {free_mem}MB available",
                            "Models may require 2-6GB of GPU memory. Consider closing other applications or using a smaller model",
                            True if free_mem < 1000 else False
                        ))
            except Exception as e:
                logger.warning(f"Failed to check GPU memory: {str(e)}")
    else:
        issues.append((
            "PyTorch is not installed",
            "Install PyTorch with: pip install torch",
            True
        ))
    
    # Check system memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024 * 1024 * 1024)
        available_gb = memory.available / (1024 * 1024 * 1024)
        
        if available_gb < MIN_FREE_MEMORY / 1024:  # Convert MB to GB
            issues.append((
                f"Low system memory: Only {available_gb:.1f}GB available",
                "Models may require 2-8GB of system memory. Consider closing other applications",
                True
            ))
    except Exception as e:
        pass  # Skip if psutil isn't available
    
    # Check for required dependencies
    try:
        import transformers
    except ImportError:
        issues.append((
            "Transformers library is not installed",
            "Install with: pip install transformers",
            True
        ))
    
    # Check disk space for model downloads
    try:
        import shutil
        _, _, free = shutil.disk_usage("/")
        free_gb = free / (1024 * 1024 * 1024)
        
        if free_gb < 5.0:  # Less than 5GB free
            issues.append((
                f"Low disk space: Only {free_gb:.1f}GB available",
                "Models may require 2-5GB of disk space for downloading and caching",
                True if free_gb < 2.0 else False
            ))
    except Exception as e:
        pass  # Skip if disk check fails
    
    return issues


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    print(f"\n{Fore.YELLOW}Received signal {signum}, shutting down server...{Style.RESET_ALL}")
    
    # Update server status
    set_server_status("shutting_down")
    
    # Attempt to run shutdown tasks
    try:
        # Import here to avoid circular imports
        from .core.app import shutdown_event
        
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.create_task(shutdown_event())
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    
    # Exit after a short delay to allow cleanup
    def delayed_exit():
        time.sleep(2)  # Give some time for cleanup
        sys.exit(0)
        
    threading.Thread(target=delayed_exit, daemon=True).start()


def start_server(
    host: str = None,
    port: int = None,
    use_ngrok: bool = False,
    ngrok_auth_token: str = None,
    **kwargs
):
    """Start the FastAPI server with optional ngrok tunnel"""
    from .config import HOST, PORT
    
    host = host or HOST
    port = port or PORT
    
    public_url = None
    
    # Set up ngrok if requested
    if use_ngrok:
        try:
            # Import pyngrok
            from pyngrok import ngrok, conf
            import nest_asyncio
            
            # Apply nest_asyncio for Colab environment
            nest_asyncio.apply()
            
            # Set ngrok auth token if provided
            if ngrok_auth_token:
                ngrok.set_auth_token(ngrok_auth_token)
            
            # Start ngrok tunnel
            public_url = ngrok.connect(port).public_url
            print(f"Ngrok tunnel established! Public URL: {public_url}")
            
            # Store the public URL in environment variables for access across modules
            os.environ["LOCALLAB_PUBLIC_URL"] = public_url
            
        except ImportError:
            print("Error: pyngrok not installed. Install with 'pip install pyngrok'.")
            return
        except Exception as e:
            print(f"Error setting up ngrok: {str(e)}")
            return
    
    # Set up uvicorn config with public_url for on_startup function to access
    from .core.app import app
    
    # Inject public_url into app state for use in on_startup
    app.state.public_url = public_url
    
    # Start uvicorn server
    import uvicorn
    uvicorn.run(
        "locallab.core.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        **kwargs
    )

async def on_startup():
    """Initialize server and display startup banner"""
    from .core.app import app
    from .logger import update_server_status, get_logger
    
    # Get logger
    logger = get_logger("locallab.server")
    
    # Update server status
    update_server_status("running")
    
    # Determine server URL - check app.state first for ngrok url
    server_url = getattr(app.state, "public_url", None)
    
    if not server_url:
        # Check environment variable
        server_url = os.environ.get("LOCALLAB_PUBLIC_URL")
        
    # If still no URL, use the local URL
    if not server_url:
        from .config import HOST, PORT
        server_url = f"http://{HOST}:{PORT}"
    
    # Log server URL
    logger.info(f"Server running at: {server_url}")
    
    # Print system instructions and banners
    from .ui.banners import print_startup_banner, print_system_instructions, print_model_info, print_api_docs
    
    print_startup_banner()
    print_system_instructions(server_url)
    
    # Print model info if a model is already loaded
    from .core.app import model_manager
    if model_manager.current_model:
        print_model_info(model_manager.current_model)
    
    # Print API docs with the correct server URL
    print_api_docs(server_url)

def cli():
    """Command line interface entry point for the package"""
    import click
    
    @click.command()
    @click.option('--use-ngrok', is_flag=True, help='Enable ngrok for public access')
    @click.option('--port', default=8000, help='Port to run the server on')
    @click.option('--ngrok-auth-token', help='Ngrok authentication token')
    def run(use_ngrok, port, ngrok_auth_token):
        """Run the LocalLab server"""
        start_server(use_ngrok=use_ngrok, port=port, ngrok_auth_token=ngrok_auth_token)
    
    run()

if __name__ == "__main__":
    cli() 
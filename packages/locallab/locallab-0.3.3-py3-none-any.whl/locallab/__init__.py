"""
LocalLab: Run LLMs locally with a friendly API similar to OpenAI
"""

__version__ = "0.3.3" 

from typing import Dict, Any, Optional
import logging

# Export commonly used components
try:
    from .config import MODEL_REGISTRY, can_run_model
    from .server import start_server
except ImportError as e:
    logging.error(f"Error importing LocalLab components: {str(e)}")
    # Provide fallback
    MODEL_REGISTRY = {}
    def can_run_model(*args, **kwargs): return False
    def start_server(*args, **kwargs): 
        raise ImportError("LocalLab failed to initialize properly")

__all__ = ["start_server", "MODEL_REGISTRY", "can_run_model"]

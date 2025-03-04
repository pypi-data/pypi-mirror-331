import os
import json
import logging
from typing import Dict, Any, Optional, List, Type, Union
import torch
import psutil
from huggingface_hub import model_info, HfApi
from pathlib import Path
from dataclasses import dataclass
from ..logger import get_logger

# Get the logger instance
logger = get_logger("locallab.config")

def get_env_var(key: str, *, default: Any = None, var_type: Type = str) -> Any:
    """Get environment variable with type conversion and validation.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        var_type: Type to convert to (str, int, float, bool)
        
    Returns:
        Converted and validated value
    """
    value = os.environ.get(key)
    
    if value is None:
        return default
        
    try:
        if var_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        return var_type(value)
    except (ValueError, TypeError):
        logging.warning(f"Invalid value for {key}, using default: {default}")
        return default

# Server settings - Using standardized environment variable names
HOST = get_env_var("LOCALLAB_HOST", default="0.0.0.0")
PORT = get_env_var("LOCALLAB_PORT", default=8000, var_type=int)

# CORS settings
ENABLE_CORS = get_env_var("LOCALLAB_ENABLE_CORS", default=True, var_type=bool)
CORS_ORIGINS = get_env_var("LOCALLAB_CORS_ORIGINS", default="*").split(",")

# Model settings
DEFAULT_MODEL = get_env_var("DEFAULT_MODEL", default="microsoft/phi-2")
DEFAULT_MAX_LENGTH = get_env_var("DEFAULT_MAX_LENGTH", default=2048, var_type=int)
DEFAULT_TEMPERATURE = get_env_var("DEFAULT_TEMPERATURE", default=0.7, var_type=float)
DEFAULT_TOP_P = get_env_var("DEFAULT_TOP_P", default=0.9, var_type=float)
DEFAULT_TOP_K = 50  # Default value for top_k parameter
DEFAULT_REPETITION_PENALTY = 1.0  # Default value for repetition penalty

# Optimization settings
ENABLE_QUANTIZATION = get_env_var("LOCALLAB_ENABLE_QUANTIZATION", default=True, var_type=bool)
QUANTIZATION_TYPE = get_env_var("LOCALLAB_QUANTIZATION_TYPE", default="int8")
ENABLE_FLASH_ATTENTION = get_env_var("LOCALLAB_ENABLE_FLASH_ATTENTION", default=False, var_type=bool)
ENABLE_ATTENTION_SLICING = get_env_var("LOCALLAB_ENABLE_ATTENTION_SLICING", default=True, var_type=bool)
ENABLE_CPU_OFFLOADING = get_env_var("LOCALLAB_ENABLE_CPU_OFFLOADING", default=False, var_type=bool)
ENABLE_BETTERTRANSFORMER = get_env_var("LOCALLAB_ENABLE_BETTERTRANSFORMER", default=False, var_type=bool)
ENABLE_COMPRESSION = get_env_var("LOCALLAB_ENABLE_COMPRESSION", default=False, var_type=bool)

# Resource management
UNLOAD_UNUSED_MODELS = get_env_var("LOCALLAB_UNLOAD_UNUSED_MODELS", default=True, var_type=bool)
MODEL_TIMEOUT = get_env_var("LOCALLAB_MODEL_TIMEOUT", default=3600, var_type=int)

# Ngrok settings
NGROK_AUTH_TOKEN = get_env_var("NGROK_AUTH_TOKEN", default="")
USE_NGROK = get_env_var("LOCALLAB_USE_NGROK", default=False, var_type=bool)

# Model registry
MODEL_REGISTRY = {
    "microsoft/phi-2": {
        "name": "Phi-2",
        "description": "Microsoft's 2.7B parameter model",
        "size": "2.7B",
        "requirements": {
            "min_ram": 8,  # GB
            "min_vram": 6  # GB if using GPU
        }
    },
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {
        "name": "TinyLlama Chat",
        "description": "Lightweight 1.1B chat model",
        "size": "1.1B",
        "requirements": {
            "min_ram": 4,
            "min_vram": 3
        }
    }
}

# Environment variables for model configuration
HUGGINGFACE_MODEL = os.environ.get("HUGGINGFACE_MODEL", "")
CUSTOM_MODEL = os.environ.get("CUSTOM_MODEL", "")

def can_run_model(model_id: str) -> bool:
    """Check if system meets model requirements"""
    if model_id not in MODEL_REGISTRY:
        return False
    
    import psutil
    import torch
    
    model = MODEL_REGISTRY[model_id]
    requirements = model["requirements"]
    
    # Check RAM
    available_ram = psutil.virtual_memory().available / (1024 ** 3)  # Convert to GB
    if available_ram < requirements["min_ram"]:
        return False
    
    # Check VRAM if GPU available
    if torch.cuda.is_available():
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            available_vram = info.free / (1024 ** 3)  # Convert to GB
            if available_vram < requirements["min_vram"]:
                return False
        except:
            pass
    
    return True

def estimate_model_requirements(model_id: str) -> Optional[Dict[str, Any]]:
    """Estimate model resource requirements more accurately"""
    # First try the enhanced estimation method
    try:
        from .utils.system import estimate_model_memory_requirements
        
        # Get quantization setting from environment
        quant = os.getenv("QUANT", "none").lower()
        
        # Use the enhanced memory estimation method
        estimation = estimate_model_memory_requirements(model_id, quantization=quant)
        
        if estimation:
            return {
                "name": model_id,
                "vram": estimation["gpu_memory_required"],  # Already in MB
                "ram": estimation["cpu_memory_required"],   # Already in MB
                "max_length": 2048,  # Default, could be improved by checking model config
                "architecture": "Transformer",  # Default
                "quantization": quant,
                "description": f"Model with approximately {estimation['params_billions']}B parameters",
                "tags": ["custom"],
                "params_billions": estimation["params_billions"],
                "memory_details": {
                    "fp16_gb": estimation["fp16_memory_gb"],
                    "int8_gb": estimation["int8_memory_gb"],
                    "int4_gb": estimation["int4_memory_gb"],
                    "with_buffer_gb": estimation["with_buffer_gb"]
                }
            }
    except Exception as e:
        logging.warning(f"Enhanced memory estimation failed, falling back to basic estimation: {str(e)}")
    
    # Fallback to the original estimation method
    try:
        info = model_info(model_id)
        
        # Get model config if available
        config = {}
        try:
            api = HfApi()
            files = api.list_repo_files(model_id)
            if "config.json" in files:
                config = json.loads(api.hf_hub_download(model_id, "config.json"))
        except:
            pass
        
        # Get model size and parameters
        model_size_bytes = info.size or info.safetensors_size or 0
        num_parameters = config.get("num_parameters", model_size_bytes / 4)  # Rough estimate if not in config
        
        # Calculate requirements
        base_vram = 2000  # Base VRAM requirement in MB
        param_size_factor = 4 if QUANTIZATION_TYPE == "fp16" else (2 if QUANTIZATION_TYPE == "int8" else 1)
        vram_per_param = (num_parameters * param_size_factor) / (1024 * 1024)  # MB
        
        requirements = {
            "name": model_id,
            "vram": int(base_vram + vram_per_param),
            "ram": int((base_vram + vram_per_param) * 1.5),  # RAM needs more headroom
            "max_length": config.get("max_position_embeddings", 2048),
            "architecture": config.get("architectures", ["Unknown"])[0],
            "quantization": QUANTIZATION_TYPE,
            "description": info.description or f"Custom model: {model_id}",
            "tags": info.tags or ["custom"],
            "fallback": "phi-2" if model_id != "microsoft/phi-2" else None
        }
        
        return requirements
    except Exception as e:
        logging.error(f"Error estimating requirements for {model_id}: {str(e)}")
        return None

# Add custom model if specified
try:
    if CUSTOM_MODEL:
        requirements = estimate_model_requirements(CUSTOM_MODEL)
        if requirements:
            MODEL_REGISTRY[CUSTOM_MODEL] = {
                "name": CUSTOM_MODEL.split("/")[-1],
                "requirements": {
                    "min_ram": requirements.get("ram", 8000),  # Using correct keys from the requirements dict
                    "min_vram": requirements.get("vram", 4000)  # Using correct keys from the requirements dict
                },
                "size": requirements.get("architecture", "Unknown"),
                "description": requirements.get("description", f"Custom model: {CUSTOM_MODEL}"),
                "type": "custom",
                "recommended": False
            }
except Exception as e:
    # Log error but don't crash on initialization
    logging.getLogger("locallab.config").warning(f"Failed to add custom model to registry: {str(e)}")

# Model Loading Settings
PRELOAD_MODELS = get_env_var("LOCALLAB_PRELOAD_MODELS", default=False, var_type=bool)  # Set to True to preload models at startup
LAZY_LOADING = get_env_var("LOCALLAB_LAZY_LOADING", default=True, var_type=bool)  # Load model components only when needed
UNLOAD_UNUSED_MODELS = get_env_var("LOCALLAB_UNLOAD_UNUSED_MODELS", default=True, var_type=bool)  # Automatically unload unused models
MODEL_TIMEOUT = get_env_var("LOCALLAB_MODEL_TIMEOUT", default=1800, var_type=int)  # Unload model after 30 minutes of inactivity

# Server Configuration
WORKERS = 1  # Number of worker processes
ENABLE_COMPRESSION = True

# Security Settings
MAX_TOKENS_PER_REQUEST = 4096
RATE_LIMIT = {
    "requests_per_minute": 60,
    "burst_size": 10
}
ENABLE_REQUEST_VALIDATION = True

# System instructions configuration
DEFAULT_SYSTEM_INSTRUCTIONS = """You are a helpful virtual assistant. Your responses should be:
1. Concise and direct - Get straight to the point
2. Professional and polite - Maintain a helpful tone
3. Relevant to the user's question - Stay on topic
4. Task-focused and practical - Provide actionable information

Keep responses short unless specifically asked for detailed information.
Respond directly to greetings with simple, friendly responses."""

def get_model_generation_params(model_id: Optional[str] = None) -> dict:
    """Get model generation parameters, optionally specific to a model.
    
    Args:
        model_id: Optional model ID to get specific parameters for
        
    Returns:
        Dictionary of generation parameters
    """
    # Base parameters (defaults)
    params = {
        "max_length": get_env_var("LOCALLAB_MODEL_MAX_LENGTH", default=DEFAULT_MAX_LENGTH, var_type=int),
        "temperature": get_env_var("LOCALLAB_MODEL_TEMPERATURE", default=DEFAULT_TEMPERATURE, var_type=float),
        "top_p": get_env_var("LOCALLAB_MODEL_TOP_P", default=DEFAULT_TOP_P, var_type=float),
        "top_k": get_env_var("LOCALLAB_TOP_K", default=DEFAULT_TOP_K, var_type=int),
        "repetition_penalty": get_env_var("LOCALLAB_REPETITION_PENALTY", default=DEFAULT_REPETITION_PENALTY, var_type=float),
    }
    
    # If model_id is provided and exists in MODEL_REGISTRY, use model-specific parameters
    if model_id and model_id in MODEL_REGISTRY:
        model_config = MODEL_REGISTRY[model_id]
        # Override with model-specific parameters if available
        if "max_length" in model_config:
            params["max_length"] = model_config["max_length"]
        
        # Add any other model-specific parameters from the registry
        for param in ["temperature", "top_p", "top_k", "repetition_penalty"]:
            if param in model_config:
                params[param] = model_config[param]
    
    return params

class SystemInstructions:
    def __init__(self):
        self.config_dir = Path.home() / ".locallab"
        self.config_file = self.config_dir / "system_instructions.json"
        self.global_instructions = DEFAULT_SYSTEM_INSTRUCTIONS
        self.model_instructions: Dict[str, str] = {}
        self.load_config()

    def load_config(self):
        """Load system instructions from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.global_instructions = config.get('global', DEFAULT_SYSTEM_INSTRUCTIONS)
                    self.model_instructions = config.get('models', {})
        except Exception as e:
            logger.warning(f"Failed to load system instructions: {e}")

    def save_config(self):
        """Save system instructions to config file"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({
                    'global': self.global_instructions,
                    'models': self.model_instructions
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save system instructions: {e}")

    def get_instructions(self, model_id: Optional[str] = None) -> str:
        """Get system instructions for a model"""
        if model_id and model_id in self.model_instructions:
            return self.model_instructions[model_id]
        return self.global_instructions

    def set_global_instructions(self, instructions: str):
        """Set global system instructions"""
        self.global_instructions = instructions
        self.save_config()

    def set_model_instructions(self, model_id: str, instructions: str):
        """Set model-specific system instructions"""
        self.model_instructions[model_id] = instructions
        self.save_config()

    def reset_instructions(self, model_id: Optional[str] = None):
        """Reset instructions to default"""
        if model_id:
            self.model_instructions.pop(model_id, None)
        else:
            self.global_instructions = DEFAULT_SYSTEM_INSTRUCTIONS
            self.model_instructions.clear()
        self.save_config()

# Initialize system instructions
system_instructions = SystemInstructions()

# Add a helper method to safely check model registry
def get_model_info(model_id: str, fallback: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Safely get model information from the registry with fallback
    
    Args:
        model_id: The model ID to look up
        fallback: Optional fallback model ID if the requested one is not found
        
    Returns:
        Model info dictionary or None if not found
    """
    if model_id in MODEL_REGISTRY:
        return MODEL_REGISTRY[model_id]
    
    if fallback and fallback in MODEL_REGISTRY:
        return MODEL_REGISTRY[fallback]
    
    return None

MIN_FREE_MEMORY = 2000  # Minimum free memory in MB

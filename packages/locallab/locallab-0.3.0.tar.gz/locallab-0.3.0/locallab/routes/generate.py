"""
API routes for text generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Generator, Tuple, AsyncGenerator
import json
from fastapi import status

from ..logger import get_logger
from ..logger.logger import get_request_count
from ..core.app import model_manager
from ..config import (
    DEFAULT_SYSTEM_INSTRUCTIONS,
    DEFAULT_MAX_LENGTH,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    get_model_generation_params
)

# Get logger
logger = get_logger("locallab.routes.generate")

# Create router
router = APIRouter(tags=["Generation"])


class GenerationRequest(BaseModel):
    """Request model for text generation"""
    prompt: str
    max_tokens: int = Field(default=DEFAULT_MAX_LENGTH, ge=1, le=32000)
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(default=DEFAULT_TOP_P, ge=0.0, le=1.0)
    system_prompt: Optional[str] = Field(default=DEFAULT_SYSTEM_INSTRUCTIONS)
    stream: bool = Field(default=False)


class BatchGenerationRequest(BaseModel):
    """Request model for batch text generation"""
    prompts: List[str]
    max_tokens: int = Field(default=DEFAULT_MAX_LENGTH, ge=1, le=32000)
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(default=DEFAULT_TOP_P, ge=0.0, le=1.0)
    system_prompt: Optional[str] = Field(default=DEFAULT_SYSTEM_INSTRUCTIONS)


class ChatMessage(BaseModel):
    """Message model for chat requests"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for chat completion"""
    messages: List[ChatMessage]
    max_tokens: int = Field(default=DEFAULT_MAX_LENGTH, ge=1, le=32000)
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(default=DEFAULT_TOP_P, ge=0.0, le=1.0)
    stream: bool = Field(default=False)


class GenerationResponse(BaseModel):
    """Response model for text generation"""
    text: str
    model: str


class ChatResponse(BaseModel):
    """Response model for chat completion"""
    choices: List[Dict[str, Any]]


class BatchGenerationResponse(BaseModel):
    """Response model for batch text generation"""
    responses: List[str]


def format_chat_messages(messages: List[ChatMessage]) -> str:
    """
    Format a list of chat messages into a prompt string that the model can understand
    
    Args:
        messages: List of ChatMessage objects with role and content
        
    Returns:
        Formatted prompt string
    """
    formatted_messages = []
    
    for msg in messages:
        role = msg.role.strip().lower()
        
        if role == "system":
            # System messages get special formatting
            formatted_messages.append(f"# System Instruction\n{msg.content}\n")
        elif role == "user":
            formatted_messages.append(f"User: {msg.content}")
        elif role == "assistant":
            formatted_messages.append(f"Assistant: {msg.content}")
        else:
            # Default formatting for other roles
            formatted_messages.append(f"{role.capitalize()}: {msg.content}")
    
    # Join all messages with newlines
    return "\n\n".join(formatted_messages)


@router.post("/generate", response_model=GenerationResponse)
async def generate_text(request: GenerationRequest) -> GenerationResponse:
    """
    Generate text from a prompt
    
    Args:
        request: The generation request
        
    Returns:
        The generated text
    """
    # Check if a model is loaded
    if not model_manager.current_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "error_type": "NO_MODEL_LOADED",
                "message": "No model is currently loaded. Use POST /models/load first.",
                "request_id": get_request_count()
            }
        )
    
    # If stream is requested, use the streaming endpoint
    if request.stream:
        return StreamingResponse(
            generate_stream(
                request.prompt, 
                request.max_tokens, 
                request.temperature, 
                request.top_p, 
                request.system_prompt
            ),
            media_type="text/event-stream"
        )
    
    # Get model-specific generation parameters (max_length, etc.)
    model_params = get_model_generation_params(model_manager.current_model)
    
    # Use model_params as defaults but override with request values if provided
    generation_params = {
        # Special case for max_tokens/max_new_tokens
        "max_new_tokens": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p
    }
    
    try:
        # Generate text using the model manager
        generated_text = await model_manager.generate_text(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            **generation_params
        )
        
        return GenerationResponse(
            text=generated_text,
            model=model_manager.current_model
        )
    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        error_details = {
            "error_type": type(e).__name__,
            "message": str(e),
            "request_id": get_request_count()
        }
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_details)


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """
    Chat completion API that formats messages into a prompt and returns the response
    """
    if not model_manager.current_model:
        raise HTTPException(status_code=400, detail="No model is currently loaded")
    
    # Format messages into a prompt
    formatted_prompt = format_chat_messages(request.messages)
    
    # If streaming is requested, return a streaming response
    if request.stream:
        return StreamingResponse(
            stream_chat(formatted_prompt, request.max_tokens, request.temperature, request.top_p),
            media_type="text/event-stream"
        )
    
    try:
        # Get model-specific generation parameters
        model_params = get_model_generation_params(model_manager.current_model)
        
        # Prepare generation parameters
        generation_params = {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p
        }
        
        # Merge model-specific params with request params
        generation_params.update(model_params)
        
        # Generate completion
        generated_text = await model_manager.generate_text(
            prompt=formatted_prompt,
            **generation_params
        )
        
        # Format response
        return ChatResponse(
            choices=[{
                "message": {
                    "role": "assistant",
                    "content": generated_text
                },
                "index": 0,
                "finish_reason": "stop"
            }]
        )
    except Exception as e:
        logger.error(f"Chat completion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_stream(
    prompt: str, 
    max_tokens: int, 
    temperature: float, 
    top_p: float, 
    system_prompt: Optional[str]
) -> AsyncGenerator[str, None]:
    """
    Generate text in a streaming fashion and return as server-sent events
    """
    try:
        # Get model-specific generation parameters
        model_params = get_model_generation_params(model_manager.current_model)
        
        # Update with request parameters
        generation_params = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        
        # Merge model-specific params with request params
        generation_params.update(model_params)
        
        # Get the stream generator
        stream_generator = model_manager.generate_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            **generation_params
        )
        
        # Stream tokens
        async for token in stream_generator:
            # Format as server-sent event
            data = token.replace("\n", "\\n")
            yield f"data: {data}\n\n"
            
        # End of stream
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Streaming generation failed: {str(e)}")
        yield f"data: [ERROR] {str(e)}\n\n"


async def stream_chat(
    formatted_prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float
) -> AsyncGenerator[str, None]:
    """
    Stream chat completion responses as server-sent events
    """
    try:
        # Get model-specific generation parameters
        model_params = get_model_generation_params(model_manager.current_model)
        
        # Update with request parameters
        generation_params = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        # Merge model-specific params with request params
        generation_params.update(model_params)
        
        # Generate streaming tokens - properly await the async generator
        stream_generator = model_manager.generate_stream(
            prompt=formatted_prompt,
            **generation_params
        )
        
        async for token in stream_generator:
            # Format as a server-sent event with the structure expected by chat clients
            data = json.dumps({"role": "assistant", "content": token})
            yield f"data: {data}\n\n"
            
        # End of stream marker
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Streaming generation failed: {str(e)}")
        error_data = json.dumps({"error": str(e)})
        yield f"data: {error_data}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/generate/batch", response_model=BatchGenerationResponse)
async def batch_generate(request: BatchGenerationRequest) -> BatchGenerationResponse:
    """
    Generate text for multiple prompts in a single request
    """
    if not model_manager.current_model:
        raise HTTPException(status_code=400, detail="No model is currently loaded")
    
    try:
        # Get model-specific generation parameters
        model_params = get_model_generation_params(model_manager.current_model)
        
        # Update with request parameters
        generation_params = {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        }
        
        # Merge model-specific params with request params
        generation_params.update(model_params)
        
        responses = []
        for prompt in request.prompts:
            generated_text = await model_manager.generate_text(
                prompt=prompt,
                system_prompt=request.system_prompt,
                **generation_params
            )
            responses.append(generated_text)
        
        return BatchGenerationResponse(responses=responses)
    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
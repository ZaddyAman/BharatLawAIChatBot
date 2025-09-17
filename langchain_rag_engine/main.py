import asyncio
import json
import time
import hmac
import hashlib
import uuid
import os
from typing import Dict, Optional, List, Set
from collections import defaultdict

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# --- Local Imports ---
# RAG system will be accessed through dependency injection
from api.acts import router as acts_router
from api.auth import router as auth_router, get_current_user, get_db
from api.feedback import router as feedback_router
from db.database import init_db
from db import crud, schemas, models

# --- Configuration and Dependency Injection ---
from config import get_config, validate_config_for_environment
from services.dependency_container import init_container, get_rag_system, get_registry

config = get_config()

# Validate configuration and show warnings
config_warnings = validate_config_for_environment()
if config_warnings:
    print("📋 Configuration Validation Results:")
    for warning in config_warnings:
        print(f"   {warning}")
    print()

container = init_container(config)

SECRET_KEY = config.secret_key
API_BASE_URL = config.api_base_url
MAX_CONCURRENT_STREAMS = config.max_concurrent_streams

# Get service instances from container
registry = get_registry()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="BharatLaw AI API",
    description="AI-powered legal assistant for Indian law with real-time streaming.",
    version="1.2.0", # Incremented version
    docs_url="/docs",
    redoc_url="/redoc"
)

init_db()

# --- Security & Performance Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# --- Static Files ---
# Create symlink from Railway volume to app directory
from pathlib import Path
import os

# Find the Railway volume
volume_base = Path("/var/lib/containers/railwayapp/bind-mounts")
uploads_target = Path("uploads")

if volume_base.exists():
    # Find volume directories
    volume_dirs = list(volume_base.glob("*/vol_*"))
    if volume_dirs:
        actual_volume = volume_dirs[0]
        print(f"📁 Found Railway volume: {actual_volume}")
        
        # Remove existing uploads directory/link
        if uploads_target.exists():
            if uploads_target.is_symlink():
                uploads_target.unlink()
            elif uploads_target.is_dir():
                import shutil
                shutil.rmtree(uploads_target)
        
        # Create symlink: uploads -> actual volume location
        try:
            uploads_target.symlink_to(actual_volume, target_is_directory=True)
            print(f"✅ Created symlink: uploads -> {actual_volume}")
            
            # Now mount static files
            app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
            print("✅ Static files mounted successfully")
            
        except Exception as e:
            print(f"❌ Could not create symlink: {e}")
            print("ℹ️  File uploads will work but static file serving may not")
    else:
        print("⚠️  No Railway volume directories found")
else:
    print("⚠️  Railway volume base directory not found")

print("🚀 BharatLaw AI backend started successfully")
    

# --- Signed URL Logic ---
def sign_payload(payload: str) -> str:
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def verify_signed_payload(signed: str) -> Dict:
    try:
        payload, sig = signed.rsplit(":", 1)
        expected_sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, sig):
            raise ValueError("Invalid signature")
        request_id, user_id, exp = payload.split("|")
        if time.time() > float(exp):
            raise ValueError("Signed URL has expired")
        return {"request_id": request_id, "user_id": user_id}
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired signed URL: {e}")


# --- Pydantic Models ---
class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None

class StartStreamResponse(BaseModel):
    signed_url: str
    request_id: str

class CancelRequest(BaseModel):
    request_id: str

# --- Streaming Endpoints ---

@app.post("/chat/start", response_model=StartStreamResponse)
async def start_chat_stream(
    payload: ChatRequest,
    current_user: schemas.User = Depends(get_current_user)
):
    user_id = str(current_user.id)
    
    # Enforce concurrent stream limit (check database for active streams)
    active_streams = registry.get_active_stream_count(user_id)
    if active_streams >= MAX_CONCURRENT_STREAMS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"You have reached the maximum of {MAX_CONCURRENT_STREAMS} concurrent streams. Please close one to start another."
        )

    request_id = str(uuid.uuid4())

    # Create stream session in database
    registry.create_stream_session(
        request_id=request_id,
        user_id=int(user_id),
        question=payload.question,
        conversation_id=payload.conversation_id
    )

    signed_payload_str = f"{request_id}|{user_id}|{int(time.time() + 60)}"
    signed_token = sign_payload(signed_payload_str)
    
    stream_url = f"{API_BASE_URL}/chat/stream?signed={signed_token}"
    
    return {"signed_url": stream_url, "request_id": request_id}


@app.get("/chat/stream")
async def chat_stream(signed: str, db: Session = Depends(get_db)):
    try:
        payload = verify_signed_payload(signed)
        request_id = payload["request_id"]
        user_id = payload["user_id"]
    except HTTPException as e:
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': e.detail})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    # Get request context from database
    request_context = registry.get_stream_session(request_id)
    if not request_context:
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid request or already processed.'})}\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    question = request_context["question"]
    conversation_id = request_context["conversation_id"]

    async def generator():
        # Register task in database
        registry.register_task(str(id(asyncio.current_task())), request_id, "streaming")

        try:
            conversation = None
            actual_conversation_id = conversation_id  # Initialize with the passed value

            if conversation_id:
                conversation = crud.get_conversation(db, conversation_id)
                if not conversation or conversation.owner_id != int(user_id):
                    raise HTTPException(status_code=404, detail="Conversation not found")
            else:
                conversation = crud.create_conversation(db, int(user_id), title=question[:50])
                print(f"[STREAM] Created new conversation: {conversation.id}")
                # Update conversation_id for new conversations
                actual_conversation_id = conversation.id

            meta = {"type": "meta", "request_id": request_id, "user_id": user_id, "conversation_id": actual_conversation_id}
            yield f"data: {json.dumps(meta, ensure_ascii=False)}\n\n"

            crud.create_message(db, conversation.id, "user", question)
            print(f"[STREAM] Saved user message to conversation: {conversation.id}")
            
            recent_messages = crud.get_messages_for_conversation(db, conversation.id)
            conversation_history = [
                {'role': msg.type, 'content': msg.content} for msg in recent_messages[:-1]
            ]

            full_answer = ""
            source = "error"
            rag_system = get_rag_system()
            async for chunk in rag_system.stream_legal_assistant(question, conversation_history):
                payload_str = json.dumps(chunk, ensure_ascii=False).replace("\n", "\\n")
                yield f"data: {payload_str}\n\n"

                # Handle different event types
                if chunk.get("type") == "chunk":
                    # Accumulate streaming chunks from LLM
                    full_answer += chunk.get("content", "")
                elif chunk.get("type") == "final_answer":
                    # Use the final answer content (may include accumulated chunks)
                    if chunk.get("content"):
                        full_answer = chunk.get("content", "")
                    source = chunk.get("source", "advanced_rag_pinecone")
                elif chunk.get("type") == "complete":
                    source = chunk.get("source", "unknown")
                    # If complete event has content, use it
                    if chunk.get("content"):
                        full_answer = chunk.get("content")

            if full_answer:
                print(f"[STREAM] Saving assistant message to conversation {conversation.id}")
                crud.create_message(db, conversation.id, "assistant", full_answer, source)
                print(f"[STREAM] Assistant message saved successfully")

                # Send completion event with conversation_id and full answer
                completion = {
                    "type": "complete",
                    "request_id": request_id,
                    "conversation_id": actual_conversation_id,
                    "source": source,
                    "content": full_answer  # Include the full answer
                }
                print(f"[STREAM] Sending completion event: {completion}")
                yield f"data: {json.dumps(completion, ensure_ascii=False)}\n\n"

        except asyncio.CancelledError:
            registry.update_stream_session_status(request_id, "cancelled")
            yield f"data: {json.dumps({'type': 'cancelled', 'request_id': request_id})}\n\n"
            raise
        except Exception as e:
            registry.update_stream_session_status(request_id, "error")
            error_payload = {"type": "error", "message": f"An unexpected error occurred: {str(e)}"}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
        finally:
            # Clean up registries
            registry.update_stream_session_status(request_id, "completed")

    return StreamingResponse(generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    })


@app.post("/chat/cancel")
async def cancel_chat_stream(payload: CancelRequest):
    request_id = payload.request_id

    # Update session status to cancelled
    success = registry.update_stream_session_status(request_id, "cancelled")

    if not success:
        raise HTTPException(status_code=404, detail="Stream session not found or already completed.")

    return {"status": "cancellation_requested"}


# --- Conversation History Endpoints ---

@app.get("/conversations", response_model=List[schemas.Conversation], tags=["Conversations"])
async def get_user_conversations(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = crud.get_conversations(db, user_id=current_user.id)
    return conversations

@app.get("/conversations/{conversation_id}/messages", response_model=List[schemas.Message], tags=["Conversations"])
async def get_conversation_messages(conversation_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation or conversation.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or not owned by user")
    messages = crud.get_messages_for_conversation(db, conversation_id)
    return messages

@app.delete("/conversations/{conversation_id}", status_code=204, tags=["Conversations"])
async def delete_user_conversation(
    conversation_id: int,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation or conversation.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found or not owned by user")

    crud.delete_conversation(db, conversation_id)
    return


# --- Other Endpoints ---

app.include_router(acts_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(feedback_router, prefix="/api")

@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Railway health check endpoint"""
    try:
        # Quick database connectivity check
        user_count = db.query(models.User).count()
        return {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/", tags=["Health"])
async def root(db: Session = Depends(get_db)):
    # Check database connectivity
    try:
        user_count = db.query(models.User).count()
        conversation_count = db.query(models.Conversation).count()
        message_count = db.query(models.Message).count()

        # Get RAG system status
        rag_system = get_rag_system()
        rag_status = rag_system.get_system_status()

        return {
            "status": "Legal AI Backend with Advanced RAG is running ✅",
            "version": "2.0.0 (Advanced RAG + Pinecone)",
            "database": {
                "connected": True,
                "users": user_count,
                "conversations": conversation_count,
                "messages": message_count
            },
            "rag_system": {
                "engine": rag_status.get("system", "Unknown"),
                "pinecone_configured": rag_status.get("pinecone_configured", False),
                "pinecone_index": rag_status.get("pinecone_index", "N/A"),
                "search_engine_ready": rag_status.get("search_engine_ready", False),
                "reasoning_engine_ready": rag_status.get("reasoning_engine_ready", False),
                "streaming_enabled": rag_status.get("streaming_enabled", False)
            },
            "features": [
                "🔍 Hybrid Search (Semantic + Keyword + Metadata)",
                "🧠 Chain-of-Thought Reasoning (8-step legal analysis)",
                "📊 Real-time Performance Analytics",
                "🎯 Domain-specific Legal Reasoning",
                "⚡ Streaming Responses",
                "🔗 Pinecone Vector Database Integration"
            ]
        }
    except Exception as e:
        return {
            "status": "Legal AI Backend is running ❌",
            "database": {
                "connected": False,
                "error": str(e)
            },
            "rag_system": {
                "status": "Error checking RAG system",
                "error": str(e)
            }
        }


@app.post("/chat", tags=["Legacy"])
async def chat_with_user_legacy(
    payload: ChatRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    rag_system = get_rag_system()
    result = await rag_system.query_legal_assistant(question)
    return result

# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    print("--- Starting BharatLaw AI Server ---")
    print(f"SECRET_KEY is set: {bool(SECRET_KEY and SECRET_KEY != 'super-secret-key-that-is-not-safe-for-prod')}")
    print(f"Max concurrent streams per user: {MAX_CONCURRENT_STREAMS}")
    print("Starting Uvicorn server...")

    # Start cleanup task
    asyncio.create_task(get_registry().start_cleanup_task())

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        loop="uvloop",
        http="h11",
        log_level="info"
    )

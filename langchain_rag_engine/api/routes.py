# backend/api/routes.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from langchain_rag_engine.rag.query_engine import query_legal_assistant

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source: str  # e.g., "vector_db" or "fallback_llm"

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        question = payload.question.strip()
        if not question:
            return ChatResponse(answer="⚠️ Please enter a valid legal question.", source="fallback_llm")

        print(f"[Agent] User question: {question}")
        result = await query_legal_assistant(question)
        print(f"[Agent] Response Source: {result['source']}")
        return ChatResponse(answer=result['answer'], source=result['source'])
    except Exception as e:
        print(f"❌ Error in /chat endpoint: {e}")
        raise

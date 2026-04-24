from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from typing import Any

from app.models.chat import ChatRequest, ChatResponse
from app.services.agent import process_user_input

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> dict[str, Any]:
    try:
        response = process_user_input(
            payload.message, 
            mode=payload.mode,
            session_id=payload.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

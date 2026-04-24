from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's query")
    mode: str = Field("guided", description="Mode of operation: 'guided' or 'explore'")


class ChatResponse(BaseModel):
    intent: str
    persona: str
    response: str
    title: str
    next_step: str
    confidence: float
    source: str
    calendar_option: bool = False
    event_title: str | None = None
    event_description: str | None = None
    event_date: str | None = None
    calendar_event: str | None = None

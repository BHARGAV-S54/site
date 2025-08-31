from pydantic import BaseModel, model_validator
from typing import Optional

class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None

    @model_validator(mode="after")
    def _ensure_one_field(self):
        if not self.message and not self.question:
            raise ValueError("Provide 'message' or 'question'.")
        return self

    def normalized_text(self) -> str:
        return self.message or self.question  # one is guaranteed to be set

class ChatResponse(BaseModel):
    reply: str
    success: bool

class IngestEvent(BaseModel):
    site_id: int
    user_id_owner: int
    visibility_scope: str
    group_id: Optional[int] = None
    other_user_id: Optional[int] = None
    direction: str
    content: str
    created_at: str
    message_hash: str

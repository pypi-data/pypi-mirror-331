from typing import List, Literal, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionOptions(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    min_p: Optional[float] = None
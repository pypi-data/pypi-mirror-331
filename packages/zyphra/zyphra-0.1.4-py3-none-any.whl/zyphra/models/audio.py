from typing import Optional, Literal
from pydantic import BaseModel, Field

# Define supported models
SupportedModel = Literal['zonos-v0.1-transformer', 'zonos-v0.1-hybrid']

class EmotionWeights(BaseModel):
    happiness: float = Field(default=0.6, ge=0, le=1)
    sadness: float = Field(default=0.05, ge=0, le=1)
    disgust: float = Field(default=0.05, ge=0, le=1)
    fear: float = Field(default=0.05, ge=0, le=1)
    surprise: float = Field(default=0.05, ge=0, le=1)
    anger: float = Field(default=0.05, ge=0, le=1)
    other: float = Field(default=0.5, ge=0, le=1)
    neutral: float = Field(default=0.6, ge=0, le=1)

class TTSParams(BaseModel):
    text: str
    speaker_audio: Optional[str] = None
    speaking_rate: Optional[float] = Field(default=15.0, ge=5, le=35)
    fmax: Optional[int] = Field(default=22050, ge=0, le=24000)
    vqscore: Optional[float] = Field(default=0.78, ge=0.6, le=0.8)
    pitch_std: Optional[float] = Field(default=45.0, ge=0, le=500)
    emotion: Optional[EmotionWeights] = None
    language_iso_code: Optional[str] = None
    mime_type: Optional[str] = None
    model: Optional[SupportedModel] = Field(default='zonos-v0.1-transformer')
    speaker_noised: Optional[bool] = Field(default=True)
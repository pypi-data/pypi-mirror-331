# zyphra/types/models.py
from enum import Enum
from typing import Literal

class ModelType(str, Enum):
    # Speech models
    ZAUDIO = "zaudio"
    # Text models
    ZAMBA2_7B = "zamba2-7b-instruct"
    ZAMBA2_2_7B = "zamba2-2.7b-instruct"

    @property
    def is_speech_model(self) -> bool:
        return self in {self.ZAUDIO}

    @property
    def is_text_model(self) -> bool:
        return self in {self.ZAMBA2_7B, self.ZAMBA2_2_7B}
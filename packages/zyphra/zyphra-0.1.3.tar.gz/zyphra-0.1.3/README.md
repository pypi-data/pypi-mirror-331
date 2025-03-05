# Zyphra Python Client

A Python client library for interacting with Zyphra's text-to-speech API.

## Installation

```bash
pip install zyphra
```

## Quick Start

```python
from zyphra import ZyphraClient

# Initialize the client
client = ZyphraClient(api_key="your-api-key")

# Generate speech and save to file
output_path = client.audio.speech.create(
    text="Hello, world!",
    speaking_rate=15,
    model="zonos-v0.1-transformer",  # Default model
    output_path="output.webm"
)

# Or get audio data as bytes
audio_data = client.audio.speech.create(
    text="Hello, world!",
    speaking_rate=15
)
```

## Features

- Text-to-speech generation with customizable parameters
- Support for multiple languages and audio formats
- Voice cloning capabilities
- Multiple TTS models with specialized capabilities
- Both synchronous and asynchronous operations
- Streaming support for audio responses
- Built-in type hints and validation

## Requirements

- Python 3.8+
- `aiohttp` for async operations
- `pydantic` for data validation
- `requests` for synchronous operations

## Detailed Usage

### Synchronous Client

```python
from zyphra import ZyphraClient

with ZyphraClient(api_key="your-api-key") as client:
    # Save directly to file
    output_path = client.audio.speech.create(
        text="Hello, world!",
        speaking_rate=15,
        model="zonos-v0.1-transformer",
        output_path="output.webm"
    )
    
    # Get audio data as bytes
    audio_data = client.audio.speech.create(
        text="Hello, world!",
        speaking_rate=15
    )
```

### Asynchronous Client

```python
from zyphra import AsyncZyphraClient

async with AsyncZyphraClient(api_key="your-api-key") as client:
    audio_data = await client.audio.speech.create(
        text="Hello, world!",
        speaking_rate=15,
        model="zonos-v0.1-transformer"
    )
```

### Supported TTS Models

The API supports the following TTS models:

- `zonos-v0.1-transformer` (Default): A standard transformer-based TTS model suitable for most applications.
- `zonos-v0.1-hybrid`: An advanced model with:
  - Better support for certain languages (especially Japanese)
  - Additional parameters (`speaker_noised` and `vqscore`)
  - Improved voice quality in some scenarios

### Advanced Options

The text-to-speech API supports various parameters to control the output:

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field

# Define supported models
SupportedModel = Literal['zonos-v0.1-transformer', 'zonos-v0.1-hybrid']

class TTSParams:
    text: str                      # The text to convert to speech (required)
    speaker_audio: Optional[str]   # Base64 audio for voice cloning
    speaking_rate: Optional[float] # Speaking rate (5-35, default: 15.0)
    fmax: Optional[int]            # Frequency max (0-24000, default: 22050)
    vqscore: Optional[float]       # VQ score (0.6-0.8, default: 0.78)
    pitch_std: Optional[float]     # Pitch standard deviation (0-500, default: 45.0)
    emotion: Optional[EmotionWeights] # Emotional weights
    language_iso_code: Optional[str] # Language code (e.g., "en-us", "fr-fr")
    mime_type: Optional[str]       # Output audio format (e.g., "audio/webm")
    model: Optional[SupportedModel] # TTS model (default: 'zonos-v0.1-transformer')
    speaker_noised: Optional[bool] # Add noise to improve stability (hybrid model only)
```

```python
class EmotionWeights:
    happiness: float = 0.6   # default: 0.6
    sadness: float = 0.05    # default: 0.05
    disgust: float = 0.05    # default: 0.05
    fear: float = 0.05       # default: 0.05
    surprise: float = 0.05   # default: 0.05
    anger: float = 0.05      # default: 0.05
    other: float = 0.5       # default: 0.5
    neutral: float = 0.6     # default: 0.6
```

### Supported Languages

The text-to-speech API supports the following languages:
- English (US) - `en-us`
- French - `fr-fr`
- German - `de`
- Japanese - `ja` (recommended to use with `zonos-v0.1-hybrid` model)
- Korean - `ko`
- Mandarin Chinese - `cmn`

### Supported Audio Formats

The API supports multiple output formats through the `mime_type` parameter:
- WebM (default) - `audio/webm`
- Ogg - `audio/ogg`
- WAV - `audio/wav`
- MP3 - `audio/mp3` or `audio/mpeg`
- MP4/AAC - `audio/mp4` or `audio/aac`

### Language and Format Examples

```python
# Generate French speech in MP3 format
audio_data = client.audio.speech.create(
    text="Bonjour le monde!",
    language_iso_code="fr-fr",
    mime_type="audio/mp3",
    speaking_rate=15
)

# Generate Japanese speech in WAV format with hybrid model (recommended)
audio_data = client.audio.speech.create(
    text="こんにちは世界！",
    language_iso_code="ja",
    mime_type="audio/wav",
    speaking_rate=15,
    model="zonos-v0.1-hybrid"  # Better for Japanese
)
```

### Model-Specific Parameters

For the hybrid model (`zonos-v0.1-hybrid`), you can utilize additional parameters:

```python
# Using the hybrid model with its specific parameters
audio_data = client.audio.speech.create(
    text="This uses the hybrid model with special parameters.",
    model="zonos-v0.1-hybrid",
    vqscore=0.7,            # Controls voice quality vs. speaker similarity (0.6-0.8)
    speaker_noised=True,    # Adds noise to improve stability
    speaking_rate=15
)
```

### Emotion Control

You can adjust the emotional tone of the speech:

```python
from zyphra.models.audio import EmotionWeights

# Create custom emotion weights
emotions = EmotionWeights(
    happiness=0.8,  # Increase happiness
    neutral=0.3,    # Decrease neutrality
    # Other emotions use default values
)

# Generate speech with emotional tone
audio_data = client.audio.speech.create(
    text="This is a happy message!",
    emotion=emotions,
    speaking_rate=15,
    model="zonos-v0.1-transformer"
)
```

### Voice Cloning

You can clone voices by providing a reference audio file:

```python
import base64

# Read and encode audio file
with open("reference_voice.wav", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode('utf-8')

# Generate speech with cloned voice
audio_data = client.audio.speech.create(
    text="This will use the cloned voice",
    speaker_audio=audio_base64,
    speaking_rate=15,
    model="zonos-v0.1-transformer"
)
```

### Error Handling

```python
from zyphra import ZyphraError

try:
    client.audio.speech.create(
        text="Hello, world!",
        speaking_rate=15,
        model="zonos-v0.1-transformer"
    )
except ZyphraError as e:
    print(f"Error: {e.status_code} - {e.response_text}")
```

## Available Models

### Speech Models
- `zonos-v0.1-transformer`: Default transformer-based TTS model
- `zonos-v0.1-hybrid`: Advanced hybrid TTS model with enhanced language support

## License

MIT License
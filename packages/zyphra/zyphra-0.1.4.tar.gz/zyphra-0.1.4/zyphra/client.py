import aiohttp
import requests
import json
import logging
from typing import AsyncGenerator, Optional, Union, Generator, Callable, Literal
from pathlib import Path
from .models.chat import ChatCompletionOptions
from .models.audio import TTSParams
from dataclasses import dataclass

logger = logging.getLogger(__name__)

API_BASE_URL = "http"
ENDPOINTS = {
    "chat": "s://llmapi.gabriel-clark.com/chat/completions",
    "tts": "://api.zyphra.com/v1/audio/text-to-speech"
}

# Define supported models
SupportedModel = Literal['zonos-v0.1-transformer', 'zonos-v0.1-hybrid']

class ZyphraError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} (Status: {status_code}, Response: {response_text})")

# Base Classes
class BaseClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self._headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

# Audio Stream Options
@dataclass
class AudioStreamOptions:
    on_chunk: Optional[Callable[[bytes], None]] = None
    on_progress: Optional[Callable[[int], None]] = None
    on_complete: Optional[Callable[[bytes], None]] = None

# Async Classes
class AsyncChatCompletions:
    def __init__(self, client: "AsyncZyphraClient"):
        self._client = client

    async def create(self, **kwargs) -> Union[AsyncGenerator[dict, None], dict]:
        await self._client._ensure_session()
        options = ChatCompletionOptions(**kwargs)
        response = await self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['chat']}",
            json=options.model_dump(exclude_unset=True)
        )
        
        if not response.ok:
            error_text = await response.text()
            raise ZyphraError(
                f"API request failed: {ENDPOINTS['chat']}",
                response.status,
                error_text
            )

        if kwargs.get('stream', False):
            return self._handle_stream(response)
        return await response.json()

    async def _handle_stream(self, response: aiohttp.ClientResponse) -> AsyncGenerator[dict, None]:
        async for line in response.content:
            line = line.decode('utf-8').strip()
            if not line or not line.startswith('data: '):
                continue
            data = line[6:].strip()
            if data == '[DONE]':
                break
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse chunk: {data}")

class AsyncSpeech:
    def __init__(self, client: "AsyncZyphraClient"):
        self._client = client

    async def create(
        self, 
        text: str, 
        output_path: Optional[Path] = None,
        options: Optional[AudioStreamOptions] = None,
        **kwargs
    ) -> Union[bytes, Path]:
        await self._client._ensure_session()
        params = TTSParams(text=text, **kwargs)
        
        async with self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['tts']}",
            json=params.model_dump(exclude_unset=True)
        ) as response:
            if not response.ok:
                error_text = await response.text()
                raise ZyphraError(
                    f"API request failed: {ENDPOINTS['tts']}",
                    response.status,
                    error_text
                )

            chunks = []
            total_bytes = 0

            async for chunk in response.content.iter_chunks():
                chunk_data = chunk[0]  # chunk is a tuple of (bytes, bool_is_end)
                chunks.append(chunk_data)
                total_bytes += len(chunk_data)

                if options and options.on_chunk:
                    options.on_chunk(chunk_data)
                
                if options and options.on_progress:
                    options.on_progress(total_bytes)

            audio_data = b''.join(chunks)
            
            if not audio_data:
                raise ZyphraError("Received empty audio response")
            
            if options and options.on_complete:
                options.on_complete(audio_data)

            if output_path:
                output_path = Path(output_path)
                output_path.write_bytes(audio_data)
                return output_path
                
            return audio_data

    async def create_stream(
        self, 
        text: str,
        **kwargs
    ) -> AsyncGenerator[bytes, None]:
        await self._client._ensure_session()
        params = TTSParams(text=text, **kwargs)
        
        async with self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['tts']}",
            json=params.model_dump(exclude_unset=True)
        ) as response:
            if not response.ok:
                error_text = await response.text()
                raise ZyphraError(
                    f"API request failed: {ENDPOINTS['tts']}",
                    response.status,
                    error_text
                )

            async for chunk in response.content.iter_chunks():
                yield chunk[0]  # chunk is a tuple of (bytes, bool_is_end)

class AsyncAudio:
    def __init__(self, client: "AsyncZyphraClient"):
        self._client = client
        self.speech = AsyncSpeech(client)

class AsyncChat:
    def __init__(self, client: "AsyncZyphraClient"):
        self._client = client
        self.completions = AsyncChatCompletions(client)

# Sync Classes
class ChatCompletions:
    def __init__(self, client: "ZyphraClient"):
        self._client = client

    def create(self, **kwargs) -> Union[Generator[dict, None, None], dict]:
        options = ChatCompletionOptions(**kwargs)
        response = self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['chat']}",
            json=options.model_dump(exclude_unset=True),
            stream=kwargs.get('stream', False)
        )
        
        if not response.ok:
            raise ZyphraError(
                f"API request failed: {ENDPOINTS['chat']}",
                response.status_code,
                response.text
            )

        if kwargs.get('stream', False):
            return self._handle_stream(response)
        return response.json()

    def _handle_stream(self, response: requests.Response) -> Generator[dict, None, None]:
        for line in response.iter_lines():
            if not line:
                continue
            line = line.decode('utf-8')
            if not line.startswith('data: '):
                continue
            data = line[6:].strip()
            if data == '[DONE]':
                break
            try:
                yield json.loads(data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse chunk: {data}")

class Speech:
    def __init__(self, client: "ZyphraClient"):
        self._client = client

    def create(
        self, 
        text: str, 
        output_path: Optional[Path] = None,
        options: Optional[AudioStreamOptions] = None,
        **kwargs
    ) -> Union[bytes, Path]:
        params = TTSParams(text=text, **kwargs)
        response = self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['tts']}",
            json=params.model_dump(exclude_unset=True),
            stream=True
        )
        
        if not response.ok:
            raise ZyphraError(
                f"API request failed: {ENDPOINTS['tts']}",
                response.status_code,
                response.text
            )
        
        chunks = []
        total_bytes = 0

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunks.append(chunk)
                total_bytes += len(chunk)

                if options and options.on_chunk:
                    options.on_chunk(chunk)
                
                if options and options.on_progress:
                    options.on_progress(total_bytes)

        audio_data = b''.join(chunks)
        
        if not audio_data:
            raise ZyphraError("Received empty audio response")
        
        if options and options.on_complete:
            options.on_complete(audio_data)

        if output_path:
            output_path = Path(output_path)
            output_path.write_bytes(audio_data)
            return output_path
            
        return audio_data

    def create_stream(
        self, 
        text: str,
        **kwargs
    ) -> Generator[bytes, None, None]:
        params = TTSParams(text=text, **kwargs)
        response = self._client._session.post(
            f"{API_BASE_URL}{ENDPOINTS['tts']}",
            json=params.model_dump(exclude_unset=True),
            stream=True
        )
        
        if not response.ok:
            raise ZyphraError(
                f"API request failed: {ENDPOINTS['tts']}",
                response.status_code,
                response.text
            )

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

class Audio:
    def __init__(self, client: "ZyphraClient"):
        self._client = client
        self.speech = Speech(client)

class Chat:
    def __init__(self, client: "ZyphraClient"):
        self._client = client
        self.completions = ChatCompletions(client)

# Main Client Classes
class ZyphraClient(BaseClient):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._session = requests.Session()
        self._session.headers.update(self._headers)
        self.chat = Chat(self)
        self.audio = Audio(self)

    def close(self):
        if self._session:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class AsyncZyphraClient(BaseClient):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._session: Optional[aiohttp.ClientSession] = None
        self.chat = AsyncChat(self)
        self.audio = AsyncAudio(self)

    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers)

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
# mygemini/gemini_handler.py

import asyncio
import base64
import numpy as np
from typing import AsyncGenerator, Literal
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    PrebuiltVoiceConfig,
    SpeechConfig,
    VoiceConfig,
    Content,
    Part,
)
from fastrtc import AsyncStreamHandler, wait_for_item

def encode_audio(data: np.ndarray) -> str:
    """Encode audio data to send to the server."""
    return base64.b64encode(data.tobytes()).decode("UTF-8")

class GeminiHandler(AsyncStreamHandler):
    """Handler for interacting with the Gemini API."""
    def __init__(
        self,
        api_key: str,
        system_prompt: str,
        voice_name: str,
        expected_layout: Literal["mono"] = "mono",
        output_sample_rate: int = 24000,
        output_frame_size: int = 480,
        input_sample_rate: int = 16000,
    ) -> None:
        super().__init__(expected_layout, output_sample_rate, output_frame_size, input_sample_rate=input_sample_rate)
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.voice_name = voice_name
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self.quit: asyncio.Event = asyncio.Event()

    def copy(self) -> "GeminiHandler":
        return GeminiHandler(
            api_key=self.api_key,
            system_prompt=self.system_prompt,
            voice_name=self.voice_name,
            expected_layout="mono",
            output_sample_rate=self.output_sample_rate,
            output_frame_size=self.output_frame_size,
        )

    async def start_up(self):
        client = genai.Client(
            api_key=self.api_key,
            http_options={"api_version": "v1alpha"},
        )
        config = LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=Content(
                parts=[Part(text=self.system_prompt)]
            ),
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(
                        voice_name=self.voice_name,
                    )
                )
            ),
        )
        async with client.aio.live.connect(
            model="gemini-2.0-flash-exp", config=config
        ) as session:
            async for audio in session.start_stream(
                stream=self.stream(), mime_type="audio/pcm"
            ):
                if audio.data:
                    array = np.frombuffer(audio.data, dtype=np.int16)
                    self.output_queue.put_nowait((self.output_sample_rate, array))

    async def stream(self) -> AsyncGenerator[bytes, None]:
        while not self.quit.is_set():
            try:
                audio = await asyncio.wait_for(self.input_queue.get(), 0.1)
                yield audio
            except (asyncio.TimeoutError, TimeoutError):
                continue

    async def receive(self, frame: tuple[int, np.ndarray]) -> None:
        _, array = frame
        array = array.squeeze()
        audio_message = encode_audio(array)
        self.input_queue.put_nowait(audio_message)

    async def emit(self) -> tuple[int, np.ndarray] | None:
        return await wait_for_item(self.output_queue)

    def shutdown(self) -> None:
        self.quit.set()

import io
from kokoro_onnx import Kokoro
import soundfile as sf
from typing import Any, Union
from fastapi import FastAPI, APIRouter
import yaml
from fastapi.responses import StreamingResponse
from uuid import uuid4
import os
import requests
from datetime import datetime
import re

from speech_tool.config import NodeConfig


class SpeechToolServer:

    def __init__(self, config: NodeConfig):
        self.config = config
        self.router = APIRouter()

        model_path = f"{config.model_name}"

        if not os.path.exists(config.model_name):
            download_url = f"{config.base_download_link}/{config.model_name}"
            file = requests.get(
                download_url,
                allow_redirects=True,
            )
            with open(config.model_name, "wb") as f:
                f.write(file.content)

        if not os.path.exists(config.voices_name):
            download_url = f"{config.base_download_link}/{config.voices_name}"
            file = requests.get(
                download_url,
                allow_redirects=True,
            )
            with open(config.voices_name, "wb") as f:
                f.write(file.content)

        self.model = Kokoro(
            model_path=model_path,
            voices_path=config.voices_name,
        )

        self.router.add_api_route(
            "/node/speech",
            self.generate_speech,
            methods=["GET"],
        )

        self.start_time = None

    def generate_speech(
        self,
        text: str,
        voice: str = None,
        speed: Union[float, int] = None,
        split_pattern: str = None,
    ):

        unique_id = str(uuid4())

        text = re.sub(" +", " ", text)

        if voice:
            self.config.pipeline.voice = voice
        if speed:
            self.config.pipeline.speed = speed
        if split_pattern:
            self.config.pipeline.split_pattern = split_pattern

        self.start_time = datetime.now()

        stream = self.model.create_stream(
            text,
            voice=self.config.pipeline.voice,
            speed=self.config.pipeline.speed,
            lang=self.config.pipeline.language_code,
        )

        return StreamingResponse(
            self.stream_file(stream),
            media_type="audio/wav",
        )

    async def stream_file(self, stream: Any):
        buffer = io.BytesIO()
        async for sample, sample_rate in stream:
            sf.write(
                buffer,
                sample,
                samplerate=sample_rate,
                format=self.config.response.format,
                # compression_level=self.config.response.compression_level,
            )
            buffer.seek(0)
            yield buffer.read()
            buffer.truncate(0)

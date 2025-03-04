# speech_tool
A text-to-speech server to convert text to speech using the [Kokoro-TTS](https://huggingface.co/spaces/hexgrad/Kokoro-TTS) models and FastAPI.

## Other Tool Packages
- [Thinking Tool](https://github.com/Ladvien/thinking_tool) - an Ollama based LLM server for distributed agentic operations.
- [Listening Tool](https://github.com/Ladvien/listening_tool)
<!-- start quick_start -->

## Quick Start
Run:
```sh
pip install speech_tool
```

Create a `config.yaml` file with the following content, see [Configuration](#configuration) for more details.

Create a `main.py` file with the following content:
```py
import os
import yaml
from fastapi import FastAPI
import uvicorn
from speech_tool import SpeechToolServer, NodeConfig

CONFIG_PATH = os.environ.get("NODE_CONFIG_PATH", "config.yaml")
config = NodeConfig(**yaml.safe_load(open(CONFIG_PATH, "r")))

app = FastAPI()

speech_tool = SpeechToolServer(config)
app.include_router(speech_tool.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

Create a client file `client.py` with the following content:
```py
import requests
import io
import sounddevice as sd
import soundfile as sf
from datetime import datetime

HOST = "http://0.0.0.0:8000" # <--- Change to your server IP
url = f"{HOST}/node/speech"

start = datetime.now()
response = requests.get(
    url,
    params={
        "text": """Anyway, it was the Saturday of the football game with Saxon Hall. 
                   The game with Saxon Hall was supposed to be a very big deal around Pencey. 
        """,
        "voice": "af_bella",
        "speed": 1.1,
        "split_pattern": r"\n+",
    },
    stream=True,
)


# Read the streamed response into memory
audio_buffer = io.BytesIO()
for chunk in response.iter_content(chunk_size=4096):
    if chunk:
        audio_buffer.write(chunk)

# Play the audio in real-time
audio_buffer.seek(0)  # Reset buffer for reading
data, samplerate = sf.read(audio_buffer)
sd.play(data, samplerate)
sd.wait()  # Wait for audio to finish playing

print(f"Time taken: {datetime.now() - start}")
```

Run:
```sh
python main.py &
```

And then run:
```sh
python client.py
```
<!-- end quick_start -->

<!-- start config -->

## Configuration
Create a `config.yaml` file with the following content:
```yaml
name: "speech_node"

# "kokoro-v1.0.fp16-gpu.onnx",
# "kokoro-v1.0.fp16.onnx",
# "kokoro-v1.0.int8.onnx",
# "kokoro-v1.0.onnx"
model_name: kokoro-v1.0.int8.onnx
voices_name: voices-v1.0.bin

response:
  # TODO: type: stream
  sample_rate: 24000
  format: wav
  compression_level: 0

pipeline:
  model:
  device: cpu # cpu or cuda
  use_transformer: true

  # Model configuration
  # 'a' = American English
  # 'b' = British English
  # 'e' = Spanish
  # 'f' = French
  # 'h' = Hindi
  # 'i' = Italian
  # 'p' = Portuguese
  # 'j' = Japanese
  # 'z' = Chinese
  language_code: en-us

  # Request defaults
  speed: 1.0 # Can be set during request
  voice: "af_heart" # Can be set during request
  split_pattern: "\n" # Can be set during request
```
<!-- end config -->
****

## Dependencies

### Linux


#### Ubuntu
```sh
sudo apt update
sudo apt install libglslang-dev
```

#### Manjaro
```sh
sudo pacman -S ffmpeg glslang

# Check for version mismatch
find /usr -name "libglslang-default-resource-limits.so*"
# If version mismatch
sudo ln -s /usr/lib/libglslang-default-resource-limits.so.15 /usr/lib/libglslang-default-resource-limits.so.14

# Check for version mismatch
find /usr -name "libSPIRV.so*"
# If version mismatch

sudo ldconfig
```

If NVIDIA is not working:
```sh
sudo modprobe -r nvidia_uvm
sudo modprobe nvidia_uvm
```

### MacOS
```
brew install ffmpeg
brew install glslang
```
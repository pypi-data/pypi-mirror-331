# YTeva

YTeva is a Python library that fetches and downloads audio files using Pyrogram.

## Installation

```bash
pip install yteva
```

## Usage

```python
from pyrogram import Client
from yteva import YTeva

app = Client("my_bot", api_id=123456, api_hash="your_api_hash", bot_token="your_bot_token")
yteva = YTeva(api_key="your_api_key", bot_app=app)

async def main():
    await app.start()
    result = await yteva.download_audio("your_video_id")
    print("Downloaded:", result)
    await app.stop()
```

## License

MIT License

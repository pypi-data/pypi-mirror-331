import aiohttp
import asyncio
from pyrogram import Client
import httpx

class YTeva:
    def __init__(self, api_key: str, bot_app, max_retries=30, retry_delay=3000):
        self.api_key = api_key
        self.bot_app = bot_app
        self.channel = "Data_eva"
        self.session = httpx.AsyncClient(timeout=400)
        self.max_retries = max_retries
        self.retry_delay = retry_delay


    async def fetch_audio_link(self, video_id: str):
      url = f"http://152.42.143.150:8000/yt-download?video_id={video_id}&media_type=audio&api_key={self.api_key}"
      async with httpx.AsyncClient(timeout=180) as client:
        response = await client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")             
            telegram_link = data.get("download_link")
            if telegram_link:
                return telegram_link  
            else:
                raise ValueError("error in download link")
    
      raise Exception(f"Failed to fetch audio link. Status: {response.status_code}, Response: {response.text}")
    
    async def fetch_video_link(self, video_id: str):
      url = f"http://152.42.143.150:8000/yt-download?video_id={video_id}&media_type=video&api_key={self.api_key}"
      async with httpx.AsyncClient(timeout=180) as client:
        response = await client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Response: {data}")
            
            telegram_link = data.get("download_link")
            if telegram_link:
                return telegram_link  
            else:
                raise ValueError("error in download link")
    
      raise Exception(f"Failed to fetch audio link. Status: {response.status_code}, Response: {response.text}")

    async def play_audio(self, video_id: str):
        telegram_link = await self.fetch_audio_link(video_id)
        message_id = int(telegram_link.split("/")[-1])
        msg = await self.bot_app.get_messages(self.channel, message_id)
        downloaded_file = await msg.download(file_name=f"downloads/{video_id}.m4a")
        return [downloaded_file, False]

    async def play_video(self, video_id: str):
        telegram_link = await self.fetch_video_link(video_id)
        message_id = int(telegram_link.split("/")[-1])
        msg = await self.bot_app.get_messages(self.channel, message_id)
        downloaded_file = await msg.download(file_name=f"downloads/{video_id}.mp4")
        return [downloaded_file, False]
    
    async def download_send_audio(self, video_id: str):
        telegram_link = await self.fetch_audio_link(video_id)
        return telegram_link
    
    async def download_send_video(self, video_id: str):
        telegram_link = await self.fetch_video_link(video_id)
        return telegram_link
        
    async def close(self):
        await self.session.close()

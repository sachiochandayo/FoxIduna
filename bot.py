import discord
import aiohttp
from aiohttp import web
import google.generativeai as genai
import asyncio
import os

# Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Geminiの初期化
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])


def split_text(text, chunk_size=1500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    input_text = message.content
    try:
        response = chat.send_message(input_text)
        chunks = split_text(response.text)
        for chunk in chunks:
            await message.channel.send(chunk)
    except Exception as e:
        await message.channel.send(f"Geminiとの通信に失敗しました: {type(e).__name__} - {e}")
        print(f"Gemini error: {e}")

# HTTPサーバーの設定（Cloud Run用）
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# 並行でBotとHTTPサーバーを動かす
async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()
    await client.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())

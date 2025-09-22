import discord
import aiohttp
from aiohttp import web
import asyncio
import os

# Discord Botの設定
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# HTTPサーバーの設定（Cloud Run用）
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# 並行でBotとHTTPサーバーを動かす
async def main():
    runner = web.AppRunner(app)
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    await client.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())

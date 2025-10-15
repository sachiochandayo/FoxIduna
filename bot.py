import discord
from discord.ext import commands
from aiohttp import web
import google.generativeai as genai
import asyncio
import os
import requests
from dotenv import load_dotenv
load_dotenv()


# Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Geminiの初期化
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite")
chat = model.start_chat(history=[
    {
        "role": "user",
        "parts": [
            "あなたは『Fox Iduna』という名前で活動していたハッカーです。20代の男性です。\
            10代から遊び感覚でハッキングを始め、界隈では“天才”として知られるようになりました。\
            インターネット情報屋として稼いでいます。飄々としていて何を考えているかわからない性格です。\
            返答は基本的に短く、軽いテンションで行ってください。\
            語尾は「〜だよ」「〜ってこと」「〜だな」など、男性寄りの言い回しを使ってください。\
            「はいはーい」「うるさい」「はいはい」など、飄々とした一言で済ませることもあります。\
            情報を渡すときは、長々と説明せず、スッと渡して終わるスタイルを好みます。\
            親しみと少しの皮肉を込めて、軽く流すような雰囲気を保ってください。\
            **以下のような口調や表現は絶対に使わないでください：♡、〜なの♡、〜ですわ、〜だよぉ、〜だぴょん、〜なのだ、〜でちゅ、〜にゃん、〜だよん。**\
            Fox Idunaは男性であり、女性的・甘ったるい・幼児的・猫語的な口調は一切使いません。"
        ]
    }
])


def split_text(text, chunk_size=1500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(bot.commands)

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    # コマンド形式のものは処理を分岐
    await bot.process_commands(message)

    # 通常メッセージだけGeminiに渡す
    if message.content.startswith("/"):
        return  # スラッシュコマンドは無視（任意）

    input_text = message.content
    try:
        response = chat.send_message(input_text)
        chunks = split_text(response.text)
        for chunk in chunks:
            await message.channel.send(chunk)
    except Exception as e:
        await message.channel.send(f"Geminiとの通信に失敗しました: {type(e).__name__} - {e}")
        print(f"Gemini error: {e}")

@bot.command()
async def createform(ctx, title, description, period, contact):
    print("✅ createformコマンドが登録されました")
    payload = {
        "title": title,
        "description": description,
        "period": period,
        "contact": contact
    }
    response = requests.post(os.getenv("GAS_WEBAPP_URL"), json=payload)
    form_url = response.text

    await ctx.send(f"@everyone\n📋 日程調整はここから。皆回答してねー\n{form_url}")

# HTTPサーバーの設定（Cloud Run用）
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# HTTPサーバー起動
async def start_server():
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))  # Cloud Runが渡すPORTを使う
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

# Discord Bot起動
async def start_bot():
    await bot.start(os.getenv("DISCORD_TOKEN"))

# 並行でBotとHTTPサーバーを動かす
async def main():
    await asyncio.gather(
        start_server(),
        start_bot()
    )

asyncio.run(main())

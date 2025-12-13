import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from collections import deque

load_dotenv(dotenv_path="/home/dsbot/config.env")

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ Нет DISCORD_TOKEN!")
    exit(1)

print("=" * 50)
print("🎵 SIMPLE DISCORD MUSIC BOT")
print("=" * 50)

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

# Простая очередь
queue = deque()
now_playing = None

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print('🎵 Готов играть музыку!')
    await bot.change_presence(activity=discord.Game(name="/хелп"))

@bot.command(name='играть', aliases=['play', 'p'])
async def play_cmd(ctx, url: str = None):
    """▶️ Играть музыку из ссылки"""
    
    if not ctx.author.voice:
        await ctx.send("❌ Сначала зайдите в голосовой канал!")
        return
    
    # Подключаемся к голосовому каналу
    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await voice_channel.connect()
    
    # Если есть URL - добавляем в очередь
    if url and (url.startswith('http://') or url.startswith('https://')):
        queue.append({
            'url': url,
            'title': f"Трек от {ctx.author.name}",
            'requester': ctx.author.name
        })
        
        await ctx.send(f"✅ Ссылка добавлена в очередь (#{len(queue)})")
    
    # Если ничего не играет - начинаем
    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        await play_next(ctx)

async def play_next(ctx):
    """Воспроизвести следующий трек"""
    global now_playing
    
    if not queue or not ctx.voice_client:
        now_playing = None
        return
    
    # Берем следующий трек
    track = queue.popleft()
    now_playing = track
    
    try:
        # ПРЯМОЕ ВОСПРОИЗВЕДЕНИЕ БЕЗ СКАЧИВАНИЯ!
        source = discord.FFmpegPCMAudio(track['url'])
        
        def after_playing(error):
            if error:
                print(f"Ошибка: {error}")
            # Следующий трек
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        
        ctx.voice_client.play(source, after=after_playing)
        
        await ctx.send(f"🎶 **Сейчас играет:** {track['title']}\n👤 {track['requester']}")
        
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {str(e)[:100]}")
        await play_next(ctx)

@bot.command(name='скинуть', aliases=['add'])
async def add_cmd(ctx, url: str):
    """➕ Добавить ссылку на музыку"""
    if not (url.startswith('http://') or url.startswith('https://')):
        await ctx.send("❌ Это не ссылка!")
        return
    
    queue.append({
        'url': url,
        'title': f"Трек от {ctx.author.name}",
        'requester': ctx.author.name
    })
    
    await ctx.send(f"✅ Добавлено в очередь (#{len(queue)})")

@bot.command(name='очередь', aliases=['q'])
async def queue_cmd(ctx):
    """📋 Показать очередь"""
    if not queue and not now_playing:
        await ctx.send("📭 Очередь пуста!")
        return
    
    embed = discord.Embed(title="📋 Очередь", color=discord.Color.blue())
    
    if now_playing:
        embed.add_field(
            name="🎶 Сейчас играет",
            value=f"{now_playing['title']}\n👤 {now_playing['requester']}",
            inline=False
        )
    
    if queue:
        text = ""
        for i, track in enumerate(list(queue)[:5], 1):
            text += f"{i}. {track['title'][:30]}\n"
        
        if len(queue) > 5:
            text += f"\n...и ещё {len(queue) - 5}"
        
        embed.add_field(name=f"В очереди ({len(queue)})", value=text, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='скип', aliases=['skip'])
async def skip_cmd(ctx):
    """⏭️ Пропустить"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Пропущено!")
    else:
        await ctx.send("❌ Нечего пропускать")

@bot.command(name='пауза', aliases=['pause'])
async def pause_cmd(ctx):
    """⏸️ Пауза"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Пауза")
    else:
        await ctx.send("❌ Нечего ставить на паузу")

@bot.command(name='продолжить', aliases=['resume'])
async def resume_cmd(ctx):
    """▶️ Продолжить"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Продолжаем")
    else:
        await ctx.send("❌ Не на паузе")

@bot.command(name='стоп', aliases=['stop'])
async def stop_cmd(ctx):
    """⏹️ Стоп"""
    global now_playing
    queue.clear()
    now_playing = None
    
    if ctx.voice_client:
        ctx.voice_client.stop()
    
    await ctx.send("⏹️ Остановлено")

@bot.command(name='зайти', aliases=['join'])
async def join_cmd(ctx):
    """🎧 Зайти"""
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ Подключился!")
    else:
        await ctx.send("❌ Ты не в голосовом канале!")

@bot.command(name='выйти', aliases=['leave'])
async def leave_cmd(ctx):
    """👋 Выйти"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Вышел")
    else:
        await ctx.send("❌ Я не в канале")
    
    for url in test_urls:
        queue.append({
            'url': url,
            'title': "Тестовая музыка",
            'requester': ctx.author.name
        })
    
    await ctx.send(f"✅ Добавлено {len(test_urls)} тестовых треков")
    
    if not ctx.voice_client and ctx.author.voice:
        await ctx.author.voice.channel.connect()
    
    if ctx.voice_client and not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command(name='хелп', aliases=['help'])
async def help_cmd(ctx):
    """📖 Помощь"""
    embed = discord.Embed(
        title="🎵 Discord Music Bot",
        description="Простой бот для музыки",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Основные команды",
        value="`/скинуть <ссылка>` - Добавить музыку\n"
              "`/играть` - Начать воспроизведение\n"
              "`/очередь` - Показать очередь\n"
              "`/пропустить` - Пропустить трек",
        inline=False
    )
    
    embed.add_field(
        name="Управление",
        value="`/пауза` - Пауза\n"
              "`/продолжить` - Продолжить\n"
              "`/стоп` - Остановить всё\n"
              "`/зайти` - Войти в канал\n"
              "`/выйти` - Выйти из канала",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Автоматическое добавление ссылок из сообщений
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Проверяем ссылки в сообщениях
    if 'http://' in message.content or 'https://' in message.content:
        words = message.content.split()
        for word in words:
            if word.startswith('http://') or word.startswith('https://'):
                # Проверяем что это похоже на аудио/видео ссылку
                if any(ext in word.lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', 'youtube', 'youtu.be']):
                    if message.author.voice and message.guild:
                        # Добавляем в очередь
                        queue.append({
                            'url': word,
                            'title': f"Ссылка от {message.author.name}",
                            'requester': message.author.name
                        })
                        
                        # Подключаемся если не подключены
                        if not message.guild.voice_client:
                            await message.author.voice.channel.connect()
                        
                        # Начинаем воспроизведение если ничего не играет
                        vc = message.guild.voice_client
                        if vc and not vc.is_playing() and not vc.is_paused():
                            await play_next(await bot.get_context(message))
                        
                        await message.channel.send(f"✅ Ссылка добавлена (#{len(queue)})", delete_after=5)
                        break
    
    await bot.process_commands(message)

if __name__ == "__main__":
    print("🚀 Запускаю простого Discord Music Bot...")
    print("🔗 Бот играет музыку по прямым ссылкам")
    bot.run(TOKEN)
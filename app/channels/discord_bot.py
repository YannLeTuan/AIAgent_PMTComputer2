import asyncio

import discord

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent
from app.core.config import settings
from app.core.logger import write_log

_AUTHOR_NAME = "PMT Computer Assistant"
_AUTHOR_ICON = "https://cdn-icons-png.flaticon.com/512/2920/2920244.png"
_COLOR_SUCCESS = 0x3498DB
_COLOR_ERROR = 0xE74C3C
_TRUNCATE_SUFFIX = "\n…*(phản hồi bị cắt ngắn)*"
_MAX_EMBED_LEN = 4000 - len(_TRUNCATE_SUFFIX)


def build_embed(answer: str, error: bool = False) -> discord.Embed:
    color = _COLOR_ERROR if error else _COLOR_SUCCESS

    if error:
        embed = discord.Embed(
            title="⚠️ Lỗi xử lý",
            description=answer,
            color=color,
        )
    else:
        description = answer
        if len(description) > _MAX_EMBED_LEN:
            description = description[:_MAX_EMBED_LEN] + _TRUNCATE_SUFFIX
        embed = discord.Embed(description=description, color=color)

    embed.set_author(name=_AUTHOR_NAME, icon_url=_AUTHOR_ICON)
    embed.set_footer(text="PMT Computer")
    return embed


def strip_mention(text: str, bot_id: int) -> str:
    return text.replace(f"<@{bot_id}>", "").replace(f"<@!{bot_id}>", "").strip()


def create_bot() -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Discord bot đang chạy: {client.user} (id={client.user.id})")

    @client.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = client.user in message.mentions

        if not is_dm and not is_mentioned:
            return

        user_text = strip_mention(message.content, client.user.id)

        # !reset command
        if user_text.lower() == "!reset":
            thread_id = str(message.author.id)
            session_store.clear_session(thread_id)
            confirm = discord.Embed(
                description="Đã xóa ngữ cảnh hội thoại của bạn.",
                color=_COLOR_SUCCESS,
            )
            confirm.set_author(name=_AUTHOR_NAME, icon_url=_AUTHOR_ICON)
            confirm.set_footer(text="PMT Computer")
            await message.channel.send(embed=confirm)
            return

        if not user_text:
            await message.channel.send(
                embed=build_embed("Bạn cần nhập câu hỏi sau khi mention tôi. Ví dụ: @Bot kiểm tra đơn ORD001")
            )
            return

        thread_id = str(message.author.id)
        history = session_store.get_history(thread_id)
        context_state = session_store.get_context(thread_id)

        try:
            async with message.channel.typing():
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        chat_with_agent,
                        user_text,
                        history,
                        context_state,
                        thread_id,
                    ),
                    timeout=60.0,
                )
            session_store.set_history(thread_id, result["history"])
            session_store.set_context(thread_id, result["context_state"])
            await message.channel.send(embed=build_embed(result["answer"]))

        except asyncio.TimeoutError:
            write_log("discord_timeout", {"thread_id": thread_id})
            await message.channel.send(
                embed=build_embed("Yêu cầu mất quá nhiều thời gian. Vui lòng thử lại.", error=True)
            )
        except Exception as e:
            write_log("discord_error", {"error": str(e), "thread_id": thread_id})
            await message.channel.send(
                embed=build_embed("Hệ thống đang gặp sự cố. Vui lòng thử lại sau.", error=True)
            )

    return client


def main():
    if not settings.DISCORD_BOT_TOKEN:
        raise ValueError("Chưa có DISCORD_BOT_TOKEN trong .env")
    bot = create_bot()
    bot.run(settings.DISCORD_BOT_TOKEN)

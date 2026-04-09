"""
Tests cho discord_bot.py — helpers build_embed và strip_mention.

build_embed(answer, error=False) → discord.Embed với đúng màu, author, description.
strip_mention(text, bot_id) → xóa <@bot_id> khỏi đầu chuỗi.
"""
import discord
import pytest


# ---------------------------------------------------------------------------
# build_embed — success case
# ---------------------------------------------------------------------------
def test_build_embed_success_color():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Đơn hàng ORD001 đang được xử lý.")
    assert embed.color.value == 0x3498DB


def test_build_embed_success_description():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Câu trả lời test")
    assert embed.description == "Câu trả lời test"


def test_build_embed_has_author():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Xin chào")
    assert embed.author.name == "PMT Computer Assistant"
    assert embed.author.icon_url is not None


def test_build_embed_has_footer():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Test")
    assert embed.footer.text == "PMT Computer"


# ---------------------------------------------------------------------------
# build_embed — error case
# ---------------------------------------------------------------------------
def test_build_embed_error_color():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Lỗi hệ thống", error=True)
    assert embed.color.value == 0xE74C3C


def test_build_embed_error_title():
    from app.channels.discord_bot import build_embed
    embed = build_embed("Lỗi hệ thống", error=True)
    assert "Lỗi" in embed.title or "⚠️" in embed.title


# ---------------------------------------------------------------------------
# build_embed — truncation
# ---------------------------------------------------------------------------
def test_build_embed_truncates_long_answer():
    from app.channels.discord_bot import build_embed
    long_text = "x" * 5000
    embed = build_embed(long_text)
    assert len(embed.description) <= 4000
    assert "cắt ngắn" in embed.description


# ---------------------------------------------------------------------------
# strip_mention
# ---------------------------------------------------------------------------
def test_strip_mention_removes_bot_mention():
    from app.channels.discord_bot import strip_mention
    result = strip_mention("<@123456789> Kiểm tra đơn hàng", bot_id=123456789)
    assert result == "Kiểm tra đơn hàng"


def test_strip_mention_handles_no_mention():
    from app.channels.discord_bot import strip_mention
    result = strip_mention("Kiểm tra đơn hàng", bot_id=123456789)
    assert result == "Kiểm tra đơn hàng"


def test_strip_mention_strips_whitespace():
    from app.channels.discord_bot import strip_mention
    result = strip_mention("  <@99>   câu hỏi   ", bot_id=99)
    assert result == "câu hỏi"

# Discord Channel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm Discord làm kênh thứ 4 — bot respond @mention + DM, typing indicator, Discord Embed, `!reset`, error handling.

**Architecture:** Thin adapter `app/channels/discord_bot.py` gọi `chat_with_agent()` qua `asyncio.to_thread` (giống pattern Telegram). Thread_id = `str(message.author.id)` để session per-user. Entry point tách riêng ở `run_discord.py`.

**Tech Stack:** `discord.py>=2.3`, `asyncio`, existing `app.agent.orchestrator.chat_with_agent`, `app.agent.memory.session_store`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `requirements.txt` | Modify | Thêm `discord.py>=2.3.0` |
| `app/core/config.py` | Modify | Thêm `DISCORD_BOT_TOKEN: str \| None = None` |
| `app/channels/discord_bot.py` | Create | Bot client, embed builder, message handler |
| `run_discord.py` | Create | Entry point — check token, start bot |
| `tests/test_discord_bot.py` | Create | Unit tests cho helper functions |

---

## Task 1: Thêm dependency và config

**Files:**
- Modify: `requirements.txt`
- Modify: `app/core/config.py`

- [ ] **Step 1: Thêm discord.py vào requirements.txt**

Mở `requirements.txt`, thêm dòng cuối:
```
discord.py>=2.3.0
```

- [ ] **Step 2: Cài đặt**

```bash
pip install discord.py>=2.3.0
```

Expected output: `Successfully installed discord.py-2.x.x`

- [ ] **Step 3: Thêm DISCORD_BOT_TOKEN vào config**

Mở `app/core/config.py`, thêm field sau `TELEGRAM_BOT_TOKEN`:

```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    VECTOR_INDEX_PATH: str = "./data/vector_index/faiss_index"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    TOP_K_RETRIEVAL: int = 4
    TELEGRAM_BOT_TOKEN: str | None = None
    DISCORD_BOT_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

- [ ] **Step 4: Verify config load**

```bash
python -c "from app.core.config import settings; print(settings.DISCORD_BOT_TOKEN)"
```

Expected: `None` (chưa set .env)

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app/core/config.py
git commit -m "feat: add discord.py dep and DISCORD_BOT_TOKEN config"
```

---

## Task 2: Viết failing tests cho helper functions

**Files:**
- Create: `tests/test_discord_bot.py`

> Các helper functions (`build_embed`, `strip_mention`) là pure/near-pure, test được mà không cần Discord connection.

- [ ] **Step 1: Tạo file test**

Tạo `tests/test_discord_bot.py`:

```python
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
```

- [ ] **Step 2: Run tests — xác nhận FAIL**

```bash
pytest tests/test_discord_bot.py -v
```

Expected: `ImportError: cannot import name 'build_embed' from 'app.channels.discord_bot'` (file chưa tồn tại)

- [ ] **Step 3: Commit tests trước khi implement**

```bash
git add tests/test_discord_bot.py
git commit -m "test: add failing tests for discord_bot helpers"
```

---

## Task 3: Implement `app/channels/discord_bot.py`

**Files:**
- Create: `app/channels/discord_bot.py`

- [ ] **Step 1: Tạo file với helpers và bot client**

Tạo `app/channels/discord_bot.py`:

```python
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
_MAX_EMBED_LEN = 3990


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
            description = description[:_MAX_EMBED_LEN] + "\n…*(phản hồi bị cắt ngắn)*"
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
                result = await asyncio.to_thread(
                    chat_with_agent,
                    user_text,
                    history,
                    context_state,
                    thread_id,
                )
            session_store.set_history(thread_id, result["history"])
            session_store.set_context(thread_id, result["context_state"])
            await message.channel.send(embed=build_embed(result["answer"]))

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
```

- [ ] **Step 2: Run tests — xác nhận PASS**

```bash
pytest tests/test_discord_bot.py -v
```

Expected output:
```
tests/test_discord_bot.py::test_build_embed_success_color PASSED
tests/test_discord_bot.py::test_build_embed_success_description PASSED
tests/test_discord_bot.py::test_build_embed_has_author PASSED
tests/test_discord_bot.py::test_build_embed_has_footer PASSED
tests/test_discord_bot.py::test_build_embed_error_color PASSED
tests/test_discord_bot.py::test_build_embed_error_title PASSED
tests/test_discord_bot.py::test_build_embed_truncates_long_answer PASSED
tests/test_discord_bot.py::test_strip_mention_removes_bot_mention PASSED
tests/test_discord_bot.py::test_strip_mention_handles_no_mention PASSED
tests/test_discord_bot.py::test_strip_mention_strips_whitespace PASSED
10 passed in 0.XXs
```

- [ ] **Step 3: Commit**

```bash
git add app/channels/discord_bot.py
git commit -m "feat: implement Discord bot channel"
```

---

## Task 4: Tạo entry point `run_discord.py`

**Files:**
- Create: `run_discord.py`

- [ ] **Step 1: Tạo entry point**

Tạo `run_discord.py` tại root:

```python
from app.channels.discord_bot import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify import**

```bash
python -c "from app.channels.discord_bot import main; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add run_discord.py
git commit -m "feat: add run_discord.py entry point"
```

---

## Task 5: Setup Discord Bot Token và smoke test

> Task này là hướng dẫn thủ công — không có code tự động.

- [ ] **Step 1: Tạo Discord Application và Bot**

1. Vào [https://discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. Tab **Bot** → **Reset Token** → copy token
3. Bật **Privileged Gateway Intents**: `MESSAGE CONTENT INTENT` ✅
4. Tab **OAuth2 → URL Generator** → chọn scope: `bot`, permissions: `Send Messages`, `Read Message History`
5. Copy invite URL → mở trong browser → thêm bot vào server test của bạn

- [ ] **Step 2: Thêm token vào .env**

Mở file `.env`, thêm:
```
DISCORD_BOT_TOKEN=your_token_here
```

- [ ] **Step 3: Chạy bot**

```bash
python run_discord.py
```

Expected output: `Discord bot đang chạy: TenBot#1234 (id=...)`

- [ ] **Step 4: Smoke test trong Discord**

Trong server Discord (channel bất kỳ):
1. `@Bot xin chào` → bot gửi embed xanh với lời chào
2. `@Bot kiểm tra đơn ORD001` → bot gọi tool, trả kết quả trong embed
3. `@Bot đơn đó bảo hành bao lâu?` → bot nhớ context từ câu trước (session continuity)
4. `@Bot !reset` → bot xác nhận đã xóa session
5. Nhắn DM trực tiếp cho bot → bot respond không cần mention
6. Tắt bot → restart → nhắn lại (session in-memory sẽ mất — đây là expected behavior)

- [ ] **Step 5: Final commit**

```bash
git add .env.example 2>/dev/null || true
git commit -m "feat: Discord channel complete — mention + DM + embed + typing"
git push origin main
```

---

## Self-Review

**Spec coverage check:**
- ✅ Section 2 (Trigger: @mention + DM) → Task 3 `on_message` guards
- ✅ Section 2 (Session per-user) → `thread_id = str(message.author.id)`
- ✅ Section 2 (!reset) → Task 3 `!reset` branch
- ✅ Section 4 (typing indicator) → `async with message.channel.typing():`
- ✅ Section 4 (asyncio.to_thread) → Task 3
- ✅ Section 5 (Embed format, set_author, color) → `build_embed()` + Task 2 tests
- ✅ Section 6 (Error handling, write_log, no crash) → try/except in Task 3
- ✅ Section 7 (Config) → Task 1
- ✅ Section 8 (discord.py dep) → Task 1
- ✅ Success criteria checklist → covered bởi Task 5 smoke test

**Placeholder scan:** Không có TBD, không có "implement later", tất cả steps có code cụ thể.

**Type consistency:**
- `build_embed(answer: str, error: bool = False) -> discord.Embed` — định nghĩa Task 3, dùng trong tests Task 2 ✅
- `strip_mention(text: str, bot_id: int) -> str` — định nghĩa Task 3, dùng trong tests Task 2 ✅
- `session_store.get_history / set_history / get_context / set_context / clear_session` — đã có sẵn trong `app/agent/memory.py` ✅
- `chat_with_agent(user_text, history, context_state, thread_id)` — signature khớp với orchestrator.py ✅

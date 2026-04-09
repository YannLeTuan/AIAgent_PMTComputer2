# Design Spec: Discord Channel

**Date:** 2026-04-09
**Status:** Approved
**Scope:** Thêm Discord làm kênh thứ 4 của hệ thống AI Agent đa kênh RAG

---

## 1. Context & Motivation

Project hiện có 3 kênh:
- `streamlit_app.py` — web demo UI
- `app/channels/telegram_bot.py` — Telegram bot
- `app/api/routes_chat.py` — REST API

Tất cả đều gọi `chat_with_agent()` và chia sẻ `session_store`. Thêm Discord là thêm 1 file adapter mỏng, không đụng đến core.

Discord phù hợp cho cửa hàng máy tính vì: cộng đồng tech dùng Discord phổ biến, dễ demo, không cần approval.

---

## 2. Interaction Model

- **Trigger:** `@Bot <câu hỏi>` trong server channel **hoặc** nhắn DM trực tiếp
- **Session scope:** per-user (`str(message.author.id)`) — cùng một user giữ ngữ cảnh xuyên suốt dù nhắn DM hay mention trong bất kỳ channel nào
- **Reset:** `!reset` command xóa session của user đó

---

## 3. Files thay đổi / tạo mới

| File | Thay đổi |
|------|----------|
| `app/channels/discord_bot.py` | Tạo mới — toàn bộ logic bot |
| `app/core/config.py` | Thêm `DISCORD_BOT_TOKEN: str \| None = None` |
| `run_discord.py` | Tạo mới — entry point (mirror `run_telegram.py` nếu có) |
| `requirements.txt` | Thêm `discord.py>=2.3` |

---

## 4. Architecture — `discord_bot.py`

```
on_message(message)
├── Guard: skip if author is bot
├── Guard: skip if not DM and not @mentioned
├── Strip @mention from message text
├── thread_id = str(message.author.id)
├── Load history + context from session_store
├── async with message.channel.typing():        ← typing indicator
│   └── asyncio.to_thread(chat_with_agent, ...)
├── session_store.set_history / set_context
└── await message.channel.send(embed=build_embed(answer))

on_message("!reset")
└── session_store.clear_session(thread_id)
    └── confirm embed
```

**Intents cần bật:**
- `discord.Intents.default()` + `intents.message_content = True`
- (Cần bật "Message Content Intent" trong Discord Developer Portal)

---

## 5. Discord Embed Format

Câu trả lời được wrap trong `discord.Embed` để đọc dễ hơn plain text:

```
┌─────────────────────────────────────────┐
│ 🖥️ PMT Computer Assistant  [avatar]     │  ← set_author (name + icon_url)
│                                          │
│  <nội dung trả lời>                      │  ← description (max 4000 chars)
│                                          │
│  PMT Computer · #channel-name           │  ← footer
└─────────────────────────────────────────┘
```

**`set_author` config:**
```python
embed.set_author(
    name="PMT Computer Assistant",
    icon_url="https://cdn-icons-png.flaticon.com/512/2920/2920244.png"  # computer icon
)
```

- `icon_url` dùng public CDN icon máy tính — không cần host ảnh riêng
- **Màu:** `0x3498db` (xanh dương) — success
- **Màu lỗi:** `0xe74c3c` (đỏ) — khi API/exception
- Nếu answer > 4000 ký tự: truncate tại 3990 và append `"\n…(phản hồi bị cắt ngắn)"`

---

## 6. Error Handling

```python
try:
    async with message.channel.typing():
        result = await asyncio.to_thread(chat_with_agent, ...)
except Exception as e:
    error_embed = discord.Embed(
        title="⚠️ Lỗi xử lý",
        description="Hệ thống đang gặp sự cố. Vui lòng thử lại sau.",
        color=0xe74c3c
    )
    await message.channel.send(embed=error_embed)
    # log error nhưng không re-raise để bot không crash
    write_log("discord_error", {"error": str(e), "thread_id": thread_id})
    return
```

---

## 7. Config

Thêm vào `app/core/config.py`:
```python
DISCORD_BOT_TOKEN: str | None = None
```

Thêm vào `.env`:
```
DISCORD_BOT_TOKEN=your_token_here
```

`run_discord.py` kiểm tra token trước khi chạy, raise `ValueError` nếu thiếu (mirror pattern của Telegram).

---

## 8. Dependencies

```
discord.py>=2.3.0
```

Thêm vào `requirements.txt`. Không conflict với các dependency hiện tại.

---

## 9. Non-goals

- Không thêm slash commands (tăng complexity, không cần thiết cho demo)
- Không per-guild isolation (thread_id per-user là đủ)
- Không rich components (buttons, select menus)
- Không deploy ke server — chạy local cho demo đồ án là đủ

---

## 10. Success Criteria

- [ ] Bot respond đúng với @mention trong server channel
- [ ] Bot respond đúng trong DM
- [ ] Typing indicator hiển thị trong suốt thời gian gọi Gemini (2-5s)
- [ ] Embed hiển thị đúng màu, title, footer
- [ ] Session continuity: user mention → DM → mention vẫn nhớ ngữ cảnh
- [ ] `!reset` xóa session thành công
- [ ] Lỗi API trả về error embed, bot không crash

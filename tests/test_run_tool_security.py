"""
Tests cho A-1: Whitelist tool + validate destructive args trong run_tool().

Hành vi kỳ vọng:
- Tool không nằm trong whitelist → trả dict failure, KHÔNG raise exception
- Destructive tool thiếu customer_email → trả dict failure, KHÔNG gọi DB
- Destructive tool có customer_email rỗng → trả dict failure
- Tool đọc (read-only) không cần customer_email → được phép gọi (mock DB)
"""
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# A-1-1: Tool ngoài whitelist bị chặn
# ---------------------------------------------------------------------------
def test_run_tool_rejects_unknown_tool_name():
    from app.agent.orchestrator import run_tool
    result = run_tool("drop_table", {})
    assert result["success"] is False
    assert "không được phép" in result["message"] or "không tồn tại" in result["message"]


# ---------------------------------------------------------------------------
# A-1-2: cancel_order thiếu customer_email → bị chặn tại orchestrator,
#         KHÔNG raise TypeError, KHÔNG chạm DB
# ---------------------------------------------------------------------------
def test_cancel_order_without_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_order", {"order_code": "ORD001", "reason": "test"})
    assert isinstance(result, dict), "run_tool phải trả dict, không raise exception"
    assert result["success"] is False
    assert "customer_email" in result["message"].lower()


# ---------------------------------------------------------------------------
# A-1-3: cancel_order có customer_email rỗng → bị chặn tại orchestrator
# ---------------------------------------------------------------------------
def test_cancel_order_with_empty_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_order", {
        "order_code": "ORD001",
        "reason": "test",
        "customer_email": "   "
    })
    assert isinstance(result, dict)
    assert result["success"] is False


# ---------------------------------------------------------------------------
# A-1-4: cancel_multiple_orders thiếu customer_email → bị chặn
# ---------------------------------------------------------------------------
def test_cancel_multiple_orders_without_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_multiple_orders", {
        "order_codes": ["ORD001", "ORD002"],
        "reason": "test"
    })
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "customer_email" in result["message"].lower()


# ---------------------------------------------------------------------------
# A-1-5: Tool đọc (search_product) KHÔNG bị chặn — vẫn gọi được (mock DB)
# ---------------------------------------------------------------------------
def test_read_only_tool_is_not_blocked():
    from app.agent.orchestrator import run_tool
    mock_return = {"success": True, "results": []}
    with patch("app.tools.product_tools.search_product", return_value=mock_return):
        result = run_tool("search_product", {"keyword": "CPU"})
    assert result["success"] is True


# ---------------------------------------------------------------------------
# A-1-6: cancel_order có customer_email hợp lệ → đi tới tool function (mock DB)
# ---------------------------------------------------------------------------
def test_cancel_order_with_valid_email_reaches_tool():
    from app.agent.orchestrator import run_tool
    mock_return = {"success": True, "message": "Đã hủy"}
    with patch("app.agent.orchestrator.cancel_order", return_value=mock_return):
        result = run_tool("cancel_order", {
            "order_code": "ORD001",
            "reason": "test",
            "customer_email": "user@example.com"
        })
    assert result["success"] is True

import pytest
from unittest.mock import patch


def test_run_tool_rejects_unknown_tool_name():
    from app.agent.orchestrator import run_tool
    result = run_tool("drop_table", {})
    assert result["success"] is False
    assert "không được phép" in result["message"] or "không tồn tại" in result["message"]


def test_cancel_order_without_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_order", {"order_code": "ORD001", "reason": "test"})
    assert isinstance(result, dict), "run_tool phải trả dict, không raise exception"
    assert result["success"] is False
    assert "customer_email" in result["message"].lower()


def test_cancel_order_with_empty_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_order", {
        "order_code": "ORD001",
        "reason": "test",
        "customer_email": "   "
    })
    assert isinstance(result, dict)
    assert result["success"] is False


def test_cancel_multiple_orders_without_customer_email_returns_failure():
    from app.agent.orchestrator import run_tool
    result = run_tool("cancel_multiple_orders", {
        "order_codes": ["ORD001", "ORD002"],
        "reason": "test"
    })
    assert isinstance(result, dict)
    assert result["success"] is False
    assert "customer_email" in result["message"].lower()


def test_read_only_tool_is_not_blocked():
    from app.agent.orchestrator import run_tool
    mock_return = {"success": True, "results": []}
    with patch("app.tools.product_tools.search_product", return_value=mock_return):
        result = run_tool("search_product", {"keyword": "CPU"})
    assert result["success"] is True


def test_cancel_order_with_valid_email_reaches_tool():
    from app.agent.tool_runner import run_tool
    mock_return = {"success": True, "message": "Đã hủy"}
    with patch("app.agent.tool_runner.cancel_order", return_value=mock_return):
        result = run_tool("cancel_order", {
            "order_code": "ORD001",
            "reason": "test",
            "customer_email": "user@example.com"
        })
    assert result["success"] is True

"""
Tests cho C-2: DEFAULT_CONTEXT phải có cùng keys ở memory.py và orchestrator.py.
Sau refactor, orchestrator.copy_context() phải dùng cùng định nghĩa với memory.
"""


def test_default_context_exported_from_memory():
    """memory.py phải export DEFAULT_CONTEXT (dict) làm source of truth."""
    from app.agent import memory
    assert hasattr(memory, "DEFAULT_CONTEXT"), (
        "memory.py thiếu DEFAULT_CONTEXT — phải định nghĩa tại đây"
    )
    ctx = memory.DEFAULT_CONTEXT
    assert isinstance(ctx, dict)
    required_keys = {
        "last_order_code", "last_product_name", "last_customer_email",
        "last_customer_name", "last_order_codes", "context_summary"
    }
    assert required_keys == set(ctx.keys()), (
        f"DEFAULT_CONTEXT thiếu keys: {required_keys - set(ctx.keys())}"
    )


def test_copy_context_uses_memory_default_context():
    """copy_context() phải trả về dict với đúng các keys từ DEFAULT_CONTEXT."""
    from app.agent.orchestrator import copy_context
    from app.agent.memory import DEFAULT_CONTEXT

    result = copy_context(None)
    assert set(result.keys()) == set(DEFAULT_CONTEXT.keys()), (
        "copy_context(None) trả về keys khác DEFAULT_CONTEXT — DRY violation"
    )


def test_copy_context_does_not_mutate_default_context():
    """copy_context() không được mutate DEFAULT_CONTEXT gốc."""
    from app.agent.orchestrator import copy_context
    from app.agent.memory import DEFAULT_CONTEXT

    original_keys = set(DEFAULT_CONTEXT.keys())
    ctx = copy_context(None)
    ctx["last_order_code"] = "ORD999"
    ctx["new_key"] = "should_not_leak"

    assert set(DEFAULT_CONTEXT.keys()) == original_keys
    assert "new_key" not in DEFAULT_CONTEXT

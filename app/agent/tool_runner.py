from google.genai import types

from app.tools.customer_tools import get_customer_orders
from app.tools.order_tools import check_order_status, cancel_order, cancel_multiple_orders
from app.tools.product_tools import search_product, list_products, get_product_details
from app.tools.pc_build_tools import build_pc_config, check_compatibility

tool_declarations = [
    types.FunctionDeclaration(
        name="check_order_status",
        description="kiểm tra trạng thái đơn hàng theo mã order_code",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_code": {"type": "string"}
            },
            "required": ["order_code"]
        }
    ),
    types.FunctionDeclaration(
        name="cancel_order",
        description="hủy đơn hàng theo mã order_code và lý do reason. Bắt buộc truyền customer_email để xác thực danh tính khách hàng trước khi hủy.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_code": {"type": "string"},
                "reason": {"type": "string"},
                "customer_email": {
                    "type": "string",
                    "description": "email của khách hàng để xác thực danh tính, phải khớp với email đăng ký đơn hàng"
                }
            },
            "required": ["order_code", "reason", "customer_email"]
        }
    ),
    types.FunctionDeclaration(
        name="search_product",
        description="tìm sản phẩm theo từ khóa, có thể tìm theo tên, loại, hãng hoặc sku",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string"}
            },
            "required": ["keyword"]
        }
    ),
    types.FunctionDeclaration(
        name="list_products",
        description="liệt kê danh sách sản phẩm theo nhóm category, hãng brand hoặc giá tối đa max_price",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "brand": {"type": "string"},
                "max_price": {"type": "number"},
                "limit": {"type": "integer"}
            }
        }
    ),
    types.FunctionDeclaration(
        name="cancel_multiple_orders",
        description="hủy nhiều đơn hàng cùng lúc theo danh sách order_codes và lý do reason. Bắt buộc truyền customer_email để xác thực danh tính.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_codes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "reason": {"type": "string"},
                "customer_email": {
                    "type": "string",
                    "description": "email của khách hàng để xác thực danh tính"
                }
            },
            "required": ["order_codes", "reason", "customer_email"]
        }
    ),
    types.FunctionDeclaration(
        name="get_customer_orders",
        description="lấy danh sách đơn hàng của khách hàng theo email",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_email": {"type": "string"}
            },
            "required": ["customer_email"]
        }
    ),
    types.FunctionDeclaration(
        name="get_product_details",
        description="xem thông số kỹ thuật chi tiết của một sản phẩm theo SKU hoặc tên. Dùng khi khách hỏi về specs, thông số, socket, DDR, TDP, tốc độ đọc ghi, v.v.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "sku_or_name": {
                    "type": "string",
                    "description": "SKU hoặc tên sản phẩm cần xem chi tiết"
                }
            },
            "required": ["sku_or_name"]
        }
    ),
    types.FunctionDeclaration(
        name="build_pc_config",
        description="tư vấn cấu hình PC theo ngân sách và mục đích sử dụng. Tự động chọn linh kiện tương thích từ kho hàng hiện có.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "budget": {
                    "type": "number",
                    "description": "ngân sách tổng (VND), tối thiểu 8.000.000"
                },
                "use_case": {
                    "type": "string",
                    "description": "mục đích sử dụng: gaming, office, streaming, graphics"
                },
                "brand_preference": {
                    "type": "string",
                    "description": "hãng ưu tiên cho CPU/VGA (nếu có), ví dụ: AMD, Intel, MSI, ASUS"
                }
            },
            "required": ["budget", "use_case"]
        }
    ),
    types.FunctionDeclaration(
        name="check_compatibility",
        description="kiểm tra tương thích phần cứng giữa các linh kiện. Truyền danh sách SKU hoặc tên sản phẩm.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "component_skus": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "danh sách SKU hoặc tên sản phẩm cần kiểm tra tương thích"
                }
            },
            "required": ["component_skus"]
        }
    ),
]

_DESTRUCTIVE_TOOLS = {"cancel_order", "cancel_multiple_orders"}


def run_tool(name: str, args: dict):
    dispatch = {
        "check_order_status": check_order_status,
        "cancel_order": cancel_order,
        "cancel_multiple_orders": cancel_multiple_orders,
        "search_product": search_product,
        "list_products": list_products,
        "get_customer_orders": get_customer_orders,
        "get_product_details": get_product_details,
        "build_pc_config": build_pc_config,
        "check_compatibility": check_compatibility,
    }
    fn = dispatch.get(name)
    if fn is None:
        return {"success": False, "message": f"công cụ {name} không được phép gọi"}
    if name in _DESTRUCTIVE_TOOLS and not args.get("customer_email", "").strip():
        return {"success": False, "message": "Thiếu customer_email để xác thực danh tính trước khi thực hiện thao tác này."}
    return fn(**args)

import logging
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from bson import ObjectId

from todo_mcp.database import db
from todo_mcp.models import TaskCreate, TaskModel, TaskStatus

from fastapi import FastAPI
from todo_mcp.api.health import router as health_router

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo FastAPI
app = FastAPI(title="Todo MCP Server Health Check")
app.include_router(health_router)

# Khởi tạo MCP Server
server = Server("todo-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Liệt kê các công cụ Todo hiện có"""
    return [
        types.Tool(
            name="add_task",
            description="Tạo một task mới trong danh sách Todo",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Tiêu đề của task"}
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="list_tasks",
            description="Lấy danh sách tất cả các task",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="mark_task_as_done",
            description="Đánh dấu một task là đã hoàn thành bằng ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID của task (ObjectId)"}
                },
                "required": ["task_id"],
            },
        ),
        types.Tool(
            name="delete_task",
            description="Xóa một task khỏi danh sách bằng ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "ID của task (ObjectId)"}
                },
                "required": ["task_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Xử lý gọi các công cụ"""
    if not arguments:
        arguments = {}

    try:
        collection = db.get_collection()

        if name == "add_task":
            title = arguments.get("title")
            if not title:
                raise ValueError("Thiếu tiêu đề task")
            
            task_data = TaskCreate(title=title)
            new_task = TaskModel(title=task_data.title)
            result = await collection.insert_one(new_task.model_dump(by_alias=True, exclude={"id"}))
            return [types.TextContent(type="text", text=f"Đã thêm task thành công. ID: {result.inserted_id}")]

        elif name == "list_tasks":
            tasks_cursor = collection.find()
            tasks = await tasks_cursor.to_list(length=100)
            
            if not tasks:
                return [types.TextContent(type="text", text="Danh sách task hiện đang trống.")]
            
            formatted_tasks = []
            for t in tasks:
                task = TaskModel(**t)
                status_icon = "✅" if task.status == TaskStatus.DONE else "⏳"
                formatted_tasks.append(f"- [{status_icon}] {task.title} (ID: {task.id})")
            
            return [types.TextContent(type="text", text="\n".join(formatted_tasks))]

        elif name == "mark_task_as_done":
            task_id = arguments.get("task_id")
            if not task_id:
                raise ValueError("Thiếu task_id")
            
            result = await collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": {"status": TaskStatus.DONE, "updated_at": TaskModel().updated_at}}
            )
            
            if result.modified_count > 0:
                return [types.TextContent(type="text", text=f"Đã đánh dấu task {task_id} là hoàn thành.")]
            return [types.TextContent(type="text", text=f"Không tìm thấy task với ID: {task_id}")]

        elif name == "delete_task":
            task_id = arguments.get("task_id")
            if not task_id:
                raise ValueError("Thiếu task_id")
            
            result = await collection.delete_one({"_id": ObjectId(task_id)})
            
            if result.deleted_count > 0:
                return [types.TextContent(type="text", text=f"Đã xóa task {task_id} thành công.")]
            return [types.TextContent(type="text", text=f"Không tìm thấy task với ID: {task_id}")]

        else:
            raise ValueError(f"Không tìm thấy công cụ: {name}")

    except Exception as e:
        logger.error(f"Lỗi khi thực hiện công cụ {name}: {e}")
        return [types.TextContent(type="text", text=f"Lỗi: {str(e)}")]

async def run_mcp():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="todo-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

async def main():
    # Đảm bảo database được kết nối
    await db.connect()
    
    # Chạy FastAPI song song với MCP
    import uvicorn
    from anyio import create_task_group

    async with create_task_group() as tg:
        # Chạy MCP Server
        tg.start_soon(run_mcp)
        
        # Chạy FastAPI HTTP Server (chỉ chạy nội bộ để health check)
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server_uvicorn = uvicorn.Server(config)
        tg.start_soon(server_uvicorn.serve)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

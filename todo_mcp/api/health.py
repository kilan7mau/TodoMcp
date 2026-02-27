from fastapi import APIRouter
from todo_mcp.database import db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Kiểm tra trạng thái server và kết nối MongoDB"""
    mongodb_status = "connected"
    try:
        # Thử gửi một lệnh ping tới MongoDB
        await db.client.admin.command('ping')
    except Exception:
        mongodb_status = "disconnected"

    return {
        "status": "healthy",
        "mongodb": mongodb_status
    }

@router.get("/")
async def root():
    return {"message": "Welcome to Todo MCP Server"}

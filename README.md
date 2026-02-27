# Todo MCP Server

Dự án này là một MCP (Model Context Protocol) Server chuyên nghiệp dùng để quản lý danh sách công việc (Todo) sử dụng Python, FastAPI và MongoDB Atlas.

## Tính năng
- **MCP Tools**: `add_task`, `list_tasks`, `mark_task_as_done`, `delete_task`.
- **FastAPI Health Check**: Endpoint `/health` kiểm tra trạng thái server và kết nối DB.
- **Asynchronous**: Sử dụng `motor` cho các thao tác MongoDB bất đồng bộ.
- **Pydantic**: Validate dữ liệu chặt chẽ với Pydantic v2.

## Cấu trúc thư mục
- `todo_mcp/mcp_server.py`: File chạy chính (MCP + FastAPI).
- `todo_mcp/database.py`: Quản lý kết nối MongoDB.
- `todo_mcp/models.py`: Định nghĩa schema cho dữ liệu.
- `todo_mcp/api/health.py`: Route cho Health Check.
- `.env`: Lưu trữ biến môi trường (Database URI).

## Hướng dẫn cài đặt

1. **Cấu hình biến môi trường**:
   Mở file `.env` và điền `MONGO_URI` với mật khẩu của bạn.

2. **Cài đặt thư viện**:
   Nếu lệnh `pip` không nhận diện được, hãy dùng lệnh sau:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Chạy Server**:
   Đảm bảo bạn đang đứng tại thư mục gốc của dự án (`TodoMcp`), sau đó chạy:
   ```bash
   python -m todo_mcp.mcp_server
   ```
   Server sẽ lắng nghe qua Stdio (cho MCP) và HTTP (port 8000 cho Health Check).

4. **Kiểm tra Health Check**:
   Mở trình duyệt truy cập: `http://localhost:8000/health`

## Hướng dẫn Kiểm thử

### 1. Kiểm tra Health Check
Đảm bảo bạn đã điền mật khẩu đúng trong `.env`, sau đó chạy server. Mở trình duyệt:
`http://localhost:8000/health`
- Nếu `mongodb: connected`: Chúc mừng, bạn đã kết nối thành công!
- Nếu `mongodb: disconnected`: Hãy kiểm tra lại IP Whitelist trên MongoDB Atlas và mật khẩu trong `.env`.

### 2. Kiểm thử Tools (Dùng MCP Inspector)
Đây là cách nhanh nhất để test mà không cần cài đặt vào App Chat.
Chạy lệnh sau tại thư mục gốc:
```bash
npx @modelcontextprotocol/inspector python -m todo_mcp.mcp_server
```
- Sau đó mở URL mà lệnh trên cung cấp (thường là `http://localhost:5173`).
- Bạn có thể chọn tool `add_task`, nhập title và nhấn "Run Tool" để xem kết quả.

> [!TIP]
> **Sửa lỗi "Python was not found":**
> Nếu bạn gặp lỗi này trên Windows, hãy thay lệnh `python` bằng đường dẫn tuyệt đối:
> ```bash
> npx @modelcontextprotocol/inspector C:/Users/kudod/miniconda3/envs/TodoMcp/python.exe -m todo_mcp.mcp_server
> ```

### 3. Tích hợp vào Claude Desktop
Để dùng trực tiếp trong Chat, bạn cần sửa file cấu hình của Claude Desktop:
- Đường dẫn (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Thêm vào mục `mcpServers`:
```json
{
  "mcpServers": {
    "todo-mcp": {
      "command": "python",
      "args": ["-m", "todo_mcp.mcp_server"],
      "cwd": "D:/jetbrain/project/TodoMcp",
      "env": {
        "PYTHONPATH": "D:/jetbrain/project/TodoMcp"
      }
    }
  }
}
```
*Lưu ý: Thay đổi đường dẫn `cwd` và `PYTHONPATH` đúng với thư mục máy bạn.*

## Quy ước Commit (Conventional Commits)
Khi bạn commit code, hãy sử dụng các loại:
- `feat`: Thêm tính năng mới.
- `fix`: Sửa lỗi.
- `chore`: Thay đổi quy trình build hoặc thư viện.

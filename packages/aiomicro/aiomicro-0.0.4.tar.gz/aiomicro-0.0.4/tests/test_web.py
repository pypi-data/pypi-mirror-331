import pytest
import asyncio
from mia.web.app import WebServer

@pytest.mark.asyncio
async def test_web_server():
    server = WebServer()
    await server.start()
    # 使用 HTTP 客户端发送请求并验证响应 
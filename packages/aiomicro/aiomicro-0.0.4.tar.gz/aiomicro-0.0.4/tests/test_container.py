import pytest
import asyncio
from mia.containers import ServiceContainer
from mia.scripts import Script
from mia.exceptions import ContainerBeingKilled


class TestScript(Script):
    setup_called = False
    start_called = False
    stop_called = False
    kill_called = False

    async def setup(self):
        self.setup_called = True

    async def start(self):
        self.start_called = True

    async def stop(self):
        self.stop_called = True

    async def kill(self):
        self.kill_called = True


class TestService:
    name = "test_service"
    test_script = TestScript()


@pytest.mark.asyncio
async def test_container_lifecycle():
    config = {"test": "config"}
    container = ServiceContainer(TestService, config)

    # 测试启动
    await container.start()
    assert container.scripts.all

    # 测试停止
    await container.stop()

    # 测试生命周期方法调用
    script = container.dependencies.pop()
    assert script.setup_called
    assert script.start_called
    assert script.stop_called


@pytest.mark.asyncio
async def test_container_kill():
    container = ServiceContainer(TestService, {})
    await container.start()
    await container.kill()

    script = container.dependencies.pop()
    assert script.kill_called


@pytest.mark.asyncio
async def test_container_worker_spawn():
    container = ServiceContainer(TestService, {})

    async def test_worker():
        return "result"

    worker_ctx = await container.spawn_worker(
        TestScript(), (), {},
        context_data={"test": "data"}
    )

    assert worker_ctx.service_name == "test_service"
    assert worker_ctx.data == {"test": "data"}

import pytest
import asyncio
from mia.timer import timer
from mia.testing.pytest import mock_container


class TestTimerService:
    name = "timer_service"
    call_count = 0

    @timer(interval=0.1, eager=True)
    async def test_timer(self):
        self.call_count += 1
        return self.call_count


@pytest.mark.asyncio
async def test_timer_execution(mock_container):
    service = TestTimerService()

    # 启动定时器
    await service.test_timer.start()

    # 等待几个周期
    await asyncio.sleep(0.3)

    # 停止定时器
    await service.test_timer.stop()

    # 验证调用次数
    assert service.call_count >= 2


@pytest.mark.asyncio
async def test_timer_eager_execution(mock_container):
    service = TestTimerService()
    service.call_count = 0

    timer_instance = service.test_timer
    await timer_instance.start()

    # 立即执行的定时器应该马上被调用
    assert service.call_count == 1

    await timer_instance.stop()

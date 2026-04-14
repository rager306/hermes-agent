"""Tests for asyncio.TaskGroup patterns (Python 3.13+)."""
import pytest
import asyncio


class TestTaskGroupMigration:
    def test_taskgroup_works_like_gather(self):
        """TaskGroup should collect results like gather."""
        async def task(i):
            return i * 2

        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(task(1))
            t2 = tg.create_task(task(2))

        results = [t1.result(), t2.result()]
        assert results == [2, 4]

    def test_taskgroup_handles_exception(self):
        """TaskGroup should raise ExceptionGroup on errors."""
        async def bad_task():
            raise ValueError("test")

        with pytest.raises(ExceptionGroup):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(bad_task())

    def test_gateway_platforms_base_uses_gather(self):
        """Verify gateway/platforms/base.py uses asyncio.gather for cancellation."""
        # This test documents that gateway/platforms/base.py:1878 uses
        # asyncio.gather for cancel_background_tasks - potential migration target
        import inspect
        from gateway.platforms.base import MessagingPlatform

        source = inspect.getsource(MessagingPlatform.cancel_background_tasks)
        assert "asyncio.gather" in source
        # Migration to TaskGroup is straightforward but requires care
        # because TaskGroup raises ExceptionGroup on any exception from tasks

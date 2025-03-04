# this_file: tests/test_async_utils.py

"""
Unit tests for the async_utils.py module.
Tests each async utility function thoroughly, covering edge cases and error conditions.
"""

import asyncio
from unittest import mock
import pytest

from twat_fs.upload_providers.async_utils import (
    run_async,
    to_sync,
    to_async,
    gather_with_concurrency,
    AsyncContextManager,
    with_async_timeout,
)


class TestRunAsync:
    """Tests for the run_async function."""

    def test_run_async_with_successful_coroutine(self):
        """Test that run_async correctly runs a successful coroutine."""

        async def test_coro():
            return "test_result"

        result = run_async(test_coro())

        assert result == "test_result"

    def test_run_async_with_exception(self):
        """Test that run_async correctly propagates exceptions."""

        async def test_coro():
            msg = "test_error"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="test_error"):
            run_async(test_coro())

    def test_run_async_with_existing_event_loop(self):
        """Test that run_async works with an existing event loop."""

        async def test_coro():
            return "test_result"

        # Simulate RuntimeError for existing event loop
        with mock.patch("asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError(
                "There is no current event loop in thread"
            )

            # Mock the new event loop
            mock_loop = mock.MagicMock()
            mock_loop.run_until_complete.return_value = "test_result"

            with mock.patch("asyncio.new_event_loop", return_value=mock_loop):
                with mock.patch("asyncio.set_event_loop"):
                    result = run_async(test_coro())

                    assert result == "test_result"
                    mock_loop.run_until_complete.assert_called_once()
                    mock_loop.close.assert_called_once()


class TestToSync:
    """Tests for the to_sync decorator."""

    def test_to_sync_with_direct_decoration(self):
        """Test that to_sync works with direct decoration."""

        @to_sync
        async def test_func():
            return "test_result"

        result = test_func()

        assert result == "test_result"
        assert not asyncio.iscoroutinefunction(test_func)

    def test_to_sync_with_arguments(self):
        """Test that to_sync works with arguments."""

        @to_sync(name="custom_name")
        async def test_func():
            return "test_result"

        result = test_func()

        assert result == "test_result"
        assert test_func.__name__ == "custom_name"

    def test_to_sync_preserves_docstring(self):
        """Test that to_sync preserves the function's docstring."""

        @to_sync
        async def test_func():
            """Test docstring."""
            return "test_result"

        assert test_func.__doc__ == "Test docstring."

    def test_to_sync_preserves_arguments(self):
        """Test that to_sync preserves the function's arguments."""

        @to_sync
        async def test_func(arg1, arg2=None):
            return f"{arg1}_{arg2}"

        result = test_func("test", arg2="value")

        assert result == "test_value"


class TestToAsync:
    """Tests for the to_async decorator."""

    def test_to_async_with_direct_decoration(self):
        """Test that to_async works with direct decoration."""

        @to_async
        def test_func():
            return "test_result"

        assert asyncio.iscoroutinefunction(test_func)

        result = run_async(test_func())

        assert result == "test_result"

    def test_to_async_with_arguments(self):
        """Test that to_async works with arguments."""

        @to_async(name="custom_name")
        def test_func():
            return "test_result"

        assert test_func.__name__ == "custom_name"

        result = run_async(test_func())

        assert result == "test_result"

    def test_to_async_preserves_docstring(self):
        """Test that to_async preserves the function's docstring."""

        @to_async
        def test_func():
            """Test docstring."""
            return "test_result"

        assert test_func.__doc__ == "Test docstring."

    def test_to_async_preserves_arguments(self):
        """Test that to_async preserves the function's arguments."""

        @to_async
        def test_func(arg1, arg2=None):
            return f"{arg1}_{arg2}"

        result = run_async(test_func("test", arg2="value"))

        assert result == "test_value"


class TestGatherWithConcurrency:
    """Tests for the gather_with_concurrency function."""

    async def test_gather_with_concurrency(self):
        """Test that gather_with_concurrency correctly limits concurrency."""
        # Create a list to track concurrent executions
        concurrent = 0
        max_concurrent = 0
        results = []

        async def test_task(i):
            nonlocal concurrent, max_concurrent
            concurrent += 1
            max_concurrent = max(max_concurrent, concurrent)
            await asyncio.sleep(0.1)  # Simulate work
            results.append(i)
            concurrent -= 1
            return i

        # Run 10 tasks with a concurrency limit of 3
        tasks = [test_task(i) for i in range(10)]
        result = await gather_with_concurrency(3, *tasks)

        # Check that the concurrency limit was respected
        assert max_concurrent <= 3

        # Check that all tasks completed
        assert len(result) == 10
        assert set(result) == set(range(10))

    async def test_gather_with_concurrency_with_exceptions(self):
        """Test that gather_with_concurrency handles exceptions correctly."""

        async def test_task(i):
            if i % 2 == 0:
                msg = f"Error in task {i}"
                raise ValueError(msg)
            return i

        # Run 10 tasks with exceptions
        # Without return_exceptions=True, the first exception should propagate
        with pytest.raises(ValueError):
            tasks = [test_task(i) for i in range(10)]
            await gather_with_concurrency(3, *tasks)

        # With return_exceptions=True, exceptions should be returned
        # Create fresh coroutines for the second call
        tasks = [test_task(i) for i in range(10)]
        result = await gather_with_concurrency(3, *tasks, return_exceptions=True)

        # Check that all tasks completed
        assert len(result) == 10

        # Check that exceptions were returned
        for i, r in enumerate(result):
            if i % 2 == 0:
                assert isinstance(r, ValueError)
            else:
                assert r == i


class TestAsyncContextManager:
    """Tests for the AsyncContextManager class."""

    async def test_async_context_manager(self):
        """Test that AsyncContextManager works as expected."""

        class TestManager(AsyncContextManager):
            def __init__(self):
                self.entered = False
                self.exited = False

            async def __aenter__(self):
                self.entered = True
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.exited = True

        manager = TestManager()

        async with manager as m:
            assert m is manager
            assert manager.entered
            assert not manager.exited

        assert manager.exited


class TestWithAsyncTimeout:
    """Tests for the with_async_timeout decorator."""

    async def test_with_async_timeout_success(self):
        """Test that with_async_timeout works for functions that complete in time."""

        @with_async_timeout(0.5)
        async def test_func():
            await asyncio.sleep(0.1)
            return "test_result"

        result = await test_func()

        assert result == "test_result"

    async def test_with_async_timeout_timeout(self):
        """Test that with_async_timeout raises TimeoutError for functions that take too long."""

        @with_async_timeout(0.1)
        async def test_func():
            await asyncio.sleep(0.5)
            return "test_result"

        with pytest.raises(TimeoutError):
            await test_func()

    async def test_with_async_timeout_preserves_metadata(self):
        """Test that with_async_timeout preserves function metadata."""

        @with_async_timeout(0.5)
        async def test_func(arg1, arg2=None):
            """Test docstring."""
            await asyncio.sleep(0.1)
            return f"{arg1}_{arg2}"

        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test docstring."

        result = await test_func("test", arg2="value")

        assert result == "test_value"

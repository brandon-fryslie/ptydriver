"""
Tests for PtyProcess.
"""

import pytest
from ptydriver import PtyProcess, ProcessPool, Keys


class TestPtyProcessBasics:
    """Basic tests for PtyProcess functionality."""

    def test_context_manager(self):
        """PtyProcess works as a context manager."""
        with PtyProcess(["bash", "--norc"]) as proc:
            assert proc.is_alive()
        # After exiting, process should be cleaned up
        assert not proc.is_alive()

    def test_send_and_get_content(self):
        """Can send commands and get output."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            proc.send("echo 'HELLO_TEST'")
            proc.wait_for("HELLO_TEST")
            assert proc.contains("HELLO_TEST")

    def test_send_raw(self):
        """Can send raw key sequences."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            # Type without pressing enter
            proc.send("echo 'partial'", press_enter=False)
            # Send Ctrl-C to cancel
            proc.send_raw(Keys.CTRL_C)
            # The echo command should be cancelled
            proc.send("echo 'after_cancel'")
            proc.wait_for("after_cancel")

    def test_get_screen(self):
        """get_screen returns list of lines."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            lines = proc.get_screen()
            assert isinstance(lines, list)
            assert len(lines) > 0

    def test_cursor_position(self):
        """Can get cursor position."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            x, y = proc.get_cursor_position()
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert x >= 0
            assert y >= 0

    def test_wait_for_timeout(self):
        """wait_for raises TimeoutError when text doesn't appear."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            with pytest.raises(TimeoutError):
                proc.wait_for("THIS_TEXT_WONT_APPEAR", timeout=0.5)

    def test_contains(self):
        """contains checks current screen content."""
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.wait_for("$", timeout=5)
            assert not proc.contains("UNIQUE_TEXT_123")
            proc.send("echo 'UNIQUE_TEXT_123'")
            proc.wait_for("UNIQUE_TEXT_123")
            assert proc.contains("UNIQUE_TEXT_123")


class TestPtyProcessWithEnv:
    """Test environment variable handling."""

    def test_custom_env(self):
        """Can pass custom environment variables."""
        import os
        env = os.environ.copy()
        env["MY_CUSTOM_VAR"] = "my_custom_value"

        with PtyProcess(["bash", "--norc"], env=env) as proc:
            proc.wait_for("$", timeout=5)
            proc.send("echo $MY_CUSTOM_VAR")
            proc.wait_for("my_custom_value")


class TestProcessPool:
    """Tests for ProcessPool."""

    def test_empty_pool(self):
        """Empty pool has no processes."""
        pool = ProcessPool()
        assert len(pool) == 0

    def test_add_process(self):
        """Can add processes to pool."""
        with ProcessPool() as pool:
            proc = pool.add(["bash", "--norc"], name="test")
            assert len(pool) == 1
            assert pool.get("test") is proc

    def test_auto_naming(self):
        """Processes get auto-generated names."""
        with ProcessPool() as pool:
            pool.add(["bash", "--norc"])
            pool.add(["bash", "--norc"])
            assert len(pool) == 2
            assert pool.get("proc-0") is not None
            assert pool.get("proc-1") is not None

    def test_broadcast(self):
        """broadcast sends to all processes."""
        with ProcessPool() as pool:
            pool.add(["bash", "--norc"], name="a")
            pool.add(["bash", "--norc"], name="b")

            # Wait for both to be ready
            for proc in pool:
                proc.wait_for("$", timeout=5)

            # Broadcast a command
            pool.broadcast("echo 'BROADCAST_TEST'")

            # Both should have the output
            for proc in pool:
                proc.wait_for("BROADCAST_TEST")

    def test_any_contains(self):
        """any_contains works correctly."""
        with ProcessPool() as pool:
            pool.add(["bash", "--norc"], name="a")
            pool.add(["bash", "--norc"], name="b")

            for proc in pool:
                proc.wait_for("$", timeout=5)

            assert not pool.any_contains("UNIQUE_A")

            pool.get("a").send("echo 'UNIQUE_A'")
            pool.get("a").wait_for("UNIQUE_A")

            assert pool.any_contains("UNIQUE_A")
            assert not pool.all_contain("UNIQUE_A")


class TestKeys:
    """Test key sequence generation."""

    def test_ctrl(self):
        """Keys.ctrl generates control characters."""
        assert Keys.ctrl('c') == '\x03'
        assert Keys.ctrl('a') == '\x01'
        assert Keys.ctrl('z') == '\x1a'

    def test_meta(self):
        """Keys.meta generates escape sequences."""
        assert Keys.meta('f') == '\x1bf'
        assert Keys.meta('b') == '\x1bb'

    def test_alt_is_meta(self):
        """Keys.alt is alias for meta."""
        assert Keys.alt('x') == Keys.meta('x')

    def test_repeat(self):
        """Keys.repeat repeats sequences."""
        assert Keys.repeat(Keys.DOWN, 3) == Keys.DOWN * 3

    def test_sequence(self):
        """Keys.sequence combines sequences."""
        assert Keys.sequence(Keys.ESC, ':wq', Keys.ENTER) == '\x1b:wq\r'

"""
PtyProcess - Core class for driving interactive terminal applications.

This module provides a simple, reliable way to control interactive CLI
applications (TUI apps, REPLs, shells, etc.) by spawning them in a PTY
and maintaining a virtual terminal screen.

Example:
    from ptydriver import PtyProcess, Keys

    # Drive any interactive CLI
    with PtyProcess(["python3"]) as proc:
        proc.send("print('hello')")
        proc.wait_for("hello")

    # Drive multiple instances
    procs = [PtyProcess(["claude"]) for _ in range(3)]
    for proc in procs:
        proc.send("What is 2+2?")
"""

import time
from threading import Lock, Thread
from typing import Dict, List, Optional, Callable

import pexpect
import pyte


class PtyProcess:
    """
    Drives an interactive terminal application via PTY.

    This class spawns CLI processes directly via pexpect and maintains a
    virtual terminal screen using pyte. Designed for programmatic control
    of interactive applications like shells, REPLs, TUI apps, and AI agents.

    Example:
        with PtyProcess(["bash", "--norc"]) as proc:
            proc.send("echo hello")
            proc.wait_for("hello")

        # Test fzf
        with PtyProcess(["fzf"]) as proc:
            proc.send_raw("test")
            proc.wait_for("test")

    Attributes:
        command: Command and arguments being executed
        width: Terminal width in characters
        height: Terminal height in characters
        timeout: Default timeout for operations
    """

    def __init__(
        self,
        command: List[str],
        width: int = 120,
        height: int = 40,
        timeout: int = 5,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
    ):
        """
        Create a PTY process for driving an interactive application.

        Args:
            command: Command and arguments to execute (e.g., ["bash", "--norc"])
            width: Terminal width in characters
            height: Terminal height in characters
            timeout: Default timeout for operations in seconds
            env: Environment variables (None = inherit from parent)
            cwd: Working directory (None = current directory)
        """
        self.command = command
        self.width = width
        self.height = height
        self.timeout = timeout
        self.env = env
        self.cwd = cwd

        # Track cleanup state
        self._is_cleaned_up = False

        # Initialize attributes that cleanup() depends on
        self.process: Optional[pexpect.spawn] = None
        self._stop_thread = False
        self._update_thread: Optional[Thread] = None

        # Virtual terminal screen (using pyte)
        self.screen = pyte.Screen(width, height)
        self.stream = pyte.Stream(self.screen)
        self.screen_lock = Lock()

        # Spawn process
        self.process = pexpect.spawn(
            command[0],
            command[1:] if len(command) > 1 else [],
            dimensions=(height, width),
            env=env,
            cwd=cwd,
            encoding='utf-8',
            timeout=timeout
        )

        # Start background thread to update screen
        self._update_thread = Thread(target=self._update_screen_loop, daemon=True)
        self._update_thread.start()

        # Give process time to start
        time.sleep(0.1)

    def _update_screen_loop(self):
        """
        Background thread to continuously feed process output to virtual screen.

        This keeps the pyte screen in sync with the actual process output.
        """
        while not self._stop_thread:
            try:
                # Read available output (non-blocking with timeout)
                if self.process and self.process.isalive():
                    # Read with very short timeout to avoid blocking
                    try:
                        data = self.process.read_nonblocking(size=4096, timeout=0.05)
                        if data:
                            # Feed to pyte screen (inside lock)
                            with self.screen_lock:
                                self.stream.feed(data)
                    except pexpect.TIMEOUT:
                        # No data available, continue loop
                        pass
                    except pexpect.EOF:
                        # Process ended
                        break
                else:
                    break
            except Exception:
                # Process might be dead
                break

            time.sleep(0.01)

    def send(self, text: str, delay: float = 0.15, press_enter: bool = True):
        """
        Send text to the process.

        Args:
            text: Text to send
            delay: Delay after sending (seconds)
            press_enter: If True (default), append Enter key after text.
                        If False, send text as-is.
        """
        if not self.process or not self.process.isalive():
            raise RuntimeError("Process not running")

        self.process.send(text)
        if press_enter:
            self.process.send('\r')
        time.sleep(delay)

    def send_raw(self, sequence: str, delay: float = 0.15):
        """
        Send raw byte sequences or escape codes to the process.

        Use this for special keys, control characters, and escape sequences.

        Args:
            sequence: Raw string to send (can include escape sequences)
            delay: Delay after sending for processing (seconds)
        """
        if not self.process or not self.process.isalive():
            raise RuntimeError("Process not running")

        self.process.send(sequence)
        time.sleep(delay)

    def get_content(self) -> str:
        """
        Get visible terminal content from virtual screen.

        Returns:
            Text content of the current screen as a single string
        """
        with self.screen_lock:
            lines = []
            for line in self.screen.display:
                lines.append(line)
            return '\n'.join(lines)

    def get_screen(self) -> List[str]:
        """
        Get the current screen as a list of lines.

        Returns:
            List of lines (strings) representing the screen
        """
        with self.screen_lock:
            return list(self.screen.display)

    def get_cursor_position(self) -> tuple[int, int]:
        """
        Get current cursor position.

        Returns:
            Tuple of (x, y) where x is column and y is row
        """
        with self.screen_lock:
            return (self.screen.cursor.x, self.screen.cursor.y)

    def wait_for(
        self,
        text: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Wait for text to appear in terminal content.

        Args:
            text: Text to wait for
            timeout: Max seconds to wait (None = use default)

        Returns:
            True if text appears within timeout

        Raises:
            TimeoutError: If text doesn't appear within timeout
        """
        timeout = timeout if timeout is not None else self.timeout
        start = time.time()

        while time.time() - start < timeout:
            content = self.get_content()
            if text in content:
                return True
            time.sleep(0.1)

        content = self.get_content()
        raise TimeoutError(
            f"Text '{text}' did not appear within {timeout}s.\n"
            f"Current content:\n{content}"
        )

    def contains(self, text: str) -> bool:
        """
        Check if text is currently visible on screen.

        Args:
            text: Text to search for

        Returns:
            True if text is on screen, False otherwise
        """
        content = self.get_content()
        return text in content

    def is_alive(self) -> bool:
        """
        Check if the process is still running.

        Returns:
            True if process is running, False otherwise
        """
        return self.process is not None and self.process.isalive()

    def terminate(self, force: bool = False):
        """
        Terminate the process.

        Args:
            force: If True, forcefully kill the process
        """
        if self.process and self.process.isalive():
            self.process.terminate(force=force)

    def cleanup(self):
        """
        Clean up the process and resources.

        MUST be called to prevent orphaned processes.
        Automatically called when using context manager.
        """
        if self._is_cleaned_up:
            return

        self._is_cleaned_up = True

        # Stop update thread
        self._stop_thread = True
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1.0)

        # Kill process
        if self.process:
            try:
                if self.process.isalive():
                    self.process.terminate(force=True)
                self.process.close()
            except (pexpect.ExceptionPexpect, OSError):
                pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        self.cleanup()
        return False

    def __del__(self):
        """Destructor - ensure cleanup on garbage collection."""
        self.cleanup()


class ProcessPool:
    """
    Manages multiple PtyProcess instances for parallel execution.

    Useful for driving multiple instances of interactive applications
    simultaneously, like running multiple AI agents in parallel.

    Example:
        pool = ProcessPool()

        # Add 3 Claude instances
        for i in range(3):
            pool.add(["claude"], name=f"claude-{i}")

        # Send to all
        pool.broadcast("What is 2+2?")

        # Wait for responses
        for name, proc in pool.processes.items():
            proc.wait_for("4")

        pool.cleanup()
    """

    def __init__(self):
        """Initialize an empty process pool."""
        self.processes: Dict[str, PtyProcess] = {}
        self._counter = 0

    def add(
        self,
        command: List[str],
        name: Optional[str] = None,
        **kwargs
    ) -> PtyProcess:
        """
        Add a new process to the pool.

        Args:
            command: Command to execute
            name: Optional name for the process (auto-generated if None)
            **kwargs: Additional arguments passed to PtyProcess

        Returns:
            The created PtyProcess instance
        """
        if name is None:
            name = f"proc-{self._counter}"
            self._counter += 1

        proc = PtyProcess(command, **kwargs)
        self.processes[name] = proc
        return proc

    def get(self, name: str) -> Optional[PtyProcess]:
        """
        Get a process by name.

        Args:
            name: Process name

        Returns:
            PtyProcess instance or None if not found
        """
        return self.processes.get(name)

    def broadcast(self, text: str, delay: float = 0.15, press_enter: bool = True):
        """
        Send text to all processes in the pool.

        Args:
            text: Text to send
            delay: Delay after sending
            press_enter: Whether to press Enter after text
        """
        for proc in self.processes.values():
            if proc.is_alive():
                proc.send(text, delay=delay, press_enter=press_enter)

    def broadcast_raw(self, sequence: str, delay: float = 0.15):
        """
        Send raw sequence to all processes in the pool.

        Args:
            sequence: Raw sequence to send
            delay: Delay after sending
        """
        for proc in self.processes.values():
            if proc.is_alive():
                proc.send_raw(sequence, delay=delay)

    def all_contain(self, text: str) -> bool:
        """
        Check if all processes contain the given text.

        Args:
            text: Text to search for

        Returns:
            True if all processes contain the text
        """
        return all(proc.contains(text) for proc in self.processes.values())

    def any_contains(self, text: str) -> bool:
        """
        Check if any process contains the given text.

        Args:
            text: Text to search for

        Returns:
            True if any process contains the text
        """
        return any(proc.contains(text) for proc in self.processes.values())

    def cleanup(self):
        """Clean up all processes in the pool."""
        for proc in self.processes.values():
            proc.cleanup()
        self.processes.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        self.cleanup()
        return False

    def __len__(self) -> int:
        """Return number of processes in pool."""
        return len(self.processes)

    def __iter__(self):
        """Iterate over processes."""
        return iter(self.processes.values())

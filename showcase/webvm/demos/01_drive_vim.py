#!/usr/bin/env python3
"""
Drive vim from Python.

Opens vim on a temp file, enters insert mode, types some text, leaves insert
mode, writes, quits, then prints the file's contents to prove vim actually
ran on the other side of the PTY.
"""
import os
import tempfile

from ptydriver import PtyProcess, Keys


def main():
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="ptydriver-demo-")
    os.close(fd)

    with PtyProcess(["vim", path]) as proc:
        # Wait until vim has drawn its first frame.
        proc.wait_for("[New File]", timeout=5)

        # Enter insert mode and type a line.
        proc.send_raw("i")
        proc.send_raw("ptydriver wrote this from Python.")
        proc.send_raw(Keys.ESCAPE)

        # Save and quit.
        proc.send_raw(":wq")
        proc.send_raw(Keys.ENTER)

    with open(path) as f:
        contents = f.read()

    print("vim is gone. The file ptydriver edited contains:")
    print("---")
    print(contents, end="")
    print("---")
    os.unlink(path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Drive a Python REPL from Python.

Spawns python3 as a child, sends statements line-by-line, waits for the
prompt to come back between statements, and prints the final screen state
so you can see exactly what the REPL displayed.
"""
import time

from ptydriver import PtyProcess


def main():
    with PtyProcess(["python3", "-q"]) as proc:
        # Initial prompt.
        proc.wait_for(">>>", timeout=5)

        proc.send("x = 21")
        proc.wait_for(">>>", timeout=5)

        proc.send("y = 2")
        proc.wait_for(">>>", timeout=5)

        proc.send("print(f'x * y = {x * y}')")
        proc.wait_for("x * y = 42", timeout=5)

        proc.send("exit()")
        deadline = time.time() + 5
        while proc.is_alive() and time.time() < deadline:
            time.sleep(0.05)

        print("\n--- final virtual screen ---")
        print(proc.get_content())
        print("--- ptydriver drove the REPL; the prints above are what it saw ---")


if __name__ == "__main__":
    main()

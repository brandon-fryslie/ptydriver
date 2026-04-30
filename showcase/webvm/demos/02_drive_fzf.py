#!/usr/bin/env python3
"""
Drive fzf from Python.

Pipes a list of fruits into fzf, types a filter to narrow the matches, then
hits Enter to select. Reads the chosen fruit out of the pipeline and prints it.
"""
import time

from ptydriver import PtyProcess, Keys


FRUITS = ["apple", "apricot", "banana", "blackberry", "cantaloupe", "cherry"]


def main():
    # Pipe the fruit list through `fzf` under bash so the shell handles the
    # echo/pipe construction. ptydriver gets the pty, bash gets the wiring.
    cmd = ["bash", "-c", f"echo -e '{chr(10).join(FRUITS)}' | fzf"]

    with PtyProcess(cmd) as proc:
        # Wait for fzf's prompt to appear.
        proc.wait_for(">", timeout=5)

        # Type a filter that narrows to two matches: 'an' → banana, cantaloupe.
        proc.send_raw("an")

        # Wait until fzf has redrawn with the filter applied.
        proc.wait_for("banana", timeout=5)

        # Pick the first match.
        proc.send_raw(Keys.ENTER)

        # Wait for fzf to exit. ptydriver doesn't expose wait_for_exit, so
        # we poll is_alive() — fzf is usually gone within ~100ms of Enter.
        deadline = time.time() + 5
        while proc.is_alive() and time.time() < deadline:
            time.sleep(0.05)

    print()
    print("fzf is gone. ptydriver drove the interactive picker; bash exited 0.")


if __name__ == "__main__":
    main()

# ptydriver WebVM image
#
# Built by ~/code/gh-pages-showcase/webvm/build-image.sh and uploaded to a
# GitHub Release on this repo by upload-image.sh. The result is fetched by
# CheerpX in the browser via HTTP range requests, so size matters: keep
# packages minimal.
#
# [LAW:one-source-of-truth] ptydriver itself comes from the published wheel
# on PyPI — same artifact users would `pip install` locally. Don't bake in
# a from-source copy; that would drift.

FROM showcase-kit-webvm-base:latest

USER root

# Tooling visitors will drive with ptydriver: vim (real one, not -tiny so
# :q works the way the demos expect), fzf, ncurses-term for the broader
# TERM database. Python + venv tools too.
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv \
      vim fzf \
      ncurses-base ncurses-term \
    && rm -rf /var/lib/apt/lists/*

USER user
WORKDIR /home/user

# Install ptydriver into an isolated venv so system Python stays clean and
# the visitor can `which python3` to see the venv shim.
#
# --ignore-requires-python: buster ships Python 3.7; ptydriver's metadata
# says >=3.8 but the actual code is pure-Python and runs on 3.7 cleanly.
# Using buster is forced by CheerpX's syscall surface (see Dockerfile.base).
RUN python3 -m venv /home/user/.venv && \
    /home/user/.venv/bin/pip install --no-cache-dir --upgrade 'pip<24' && \
    /home/user/.venv/bin/pip install --no-cache-dir --ignore-requires-python ptydriver
ENV PATH=/home/user/.venv/bin:$PATH
ENV VIRTUAL_ENV=/home/user/.venv

# Demo scripts — these are what the showcase's "suggested commands" sidebar
# launches. Keep them small, readable, and obviously real ptydriver code.
COPY --chown=user:user demos /home/user/demos

# Friendly login banner so the visitor's first impression isn't a bare prompt.
RUN printf '%s\n' \
    '' \
    '  ptydriver — drive interactive TUIs from Python.' \
    '' \
    '  Try a demo:   python3 demos/01_drive_vim.py' \
    '  See source:   cat demos/01_drive_vim.py' \
    '  REPL:         python3   (then `from ptydriver import PtyProcess`)' \
    '' \
  > /home/user/.welcome

RUN printf '%s\n' \
    'cat ~/.welcome' \
    'export PS1="\[\e[36m\]\u@webvm\[\e[0m\]:\[\e[33m\]\w\[\e[0m\]\$ "' \
    'alias ll="ls -lah"' \
  > /home/user/.bashrc

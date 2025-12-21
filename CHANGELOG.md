# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-20

### Added

- `PtyProcess` class for driving interactive terminal applications via PTY
- `ProcessPool` class for managing multiple processes in parallel
- `Keys`, `MacKeys`, `ReadlineKeys` classes with common key sequences
- `send()`, `send_raw()`, `send_bytes()` methods for sending input
- `wait_for()`, `contains()` methods for pattern matching (string and regex)
- `expect_any()` for waiting on multiple patterns
- `expect_sequence()` for waiting on ordered pattern sequences
- `get_content()`, `get_screen()`, `get_cursor_position()` for reading terminal state
- `set_size()` for terminal resizing
- Context manager support for automatic cleanup
- Full type annotations with strict mypy compliance
- Comprehensive test suite

### Fixed

- Removed broken `ProcessPool.expect_any()` and `ProcessPool.expect_sequence()` methods that referenced non-existent attributes

## [0.1.0] - 2024-12-20

### Added

- Initial release

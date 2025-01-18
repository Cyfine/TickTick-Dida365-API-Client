# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-18

### Fixed
- Fixed GitHub repository URL in package metadata

## [0.1.1] - 2025-01-18

### Added
- Detailed OAuth2 setup instructions in README.md:
  - Step-by-step guide for obtaining client credentials
  - Clear instructions for configuring OAuth redirect URL
  - Improved environment configuration examples

### Changed
- Enhanced Quick Start example in README.md with better authentication flow explanation
- Improved documentation clarity for first-time users

## [0.1.0] - 2025-01-18

### Added
- Initial release
- Full async support using `httpx`
- OAuth2 authentication with automatic token management
- Type-safe API with Pydantic v2 models
- Support for both Dida365 and TickTick APIs
- Comprehensive error handling
- Environment file integration
- State management for tasks and projects
- Request timeout configuration
- Logging configuration
- Project CRUD operations
- Task CRUD operations
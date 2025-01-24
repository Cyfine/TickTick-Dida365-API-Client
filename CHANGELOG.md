# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.8] - 2024-01-24

### Fixed
- Fixed a bug where service type from environment variables wasn't properly propagated to the API configuration, causing incorrect OAuth redirection

## [0.1.7] - 2025-01-24

### Fixed
- Fixed bug where service type was not being loaded correctly from environment variables

## [0.1.6] - 2025-01-22

### Changed
- Refactored task models to make fields optional in base model and required where needed
- Added better documentation and examples for task models

## [0.1.5] - 2025-01-19

### Changed
- Made `project` field optional in `ProjectData` model to handle API responses more flexibly
- Fixed linting issues in project models
- Allow extra environment variables in .env file to better support integration with other packages
- Updated settings to use Pydantic v2 model_config instead of Config class

## [0.1.4] - 2025-01-19

### Changed
- Made `project` field optional in `ProjectData` model to handle API responses more flexibly
- Fixed linting issues in project models
- Allow extra environment variables in .env file to better support integration with other packages

## [0.1.3] - 2025-01-19
- Fix bug that service type is not being saved. 

### Changed
- Fixed bug where the service type was not being saved correctly. Now, if the user has selected the TickTick/Dida365 service type, it will be updated accordingly in the environment variables.

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
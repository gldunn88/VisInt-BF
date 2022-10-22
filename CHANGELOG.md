# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2022-09-28
### Added
- Hardcoded rendering configuration
    - Screen scrolls fluidly to keep program counter in center
    - Each cell is represented by a red base with growing white tower
- Loading bf programs from CLI
- Loading bf memory environments from CLI
- Unit tests for BF Interpreting engine
- Screen elements to display current run configuration
- Controls to change the execution rate for powers of 2 in the range 2^0 -> 2^5
- Pause to temporarily halt execution
- Initial README file

## [0.0.2] - 2022-10-22
### Added
- Input prompt support for ',' command

### Changed

- Refactored rendering to classes outside of main. Now main is responsible for event handling and state controls only.

# Changelog for valarpy

Adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [2.2.0] - 2020-08-26

### Fixed:
- `submission_statuses` was incompatible with the actual database


## [2.1.0] - 2020-08-25

### Fixed:
- Incompatibility with real database
- Improved connection code
- Inflexible dependency version ranges
- Poor code separation: moved general code from `model.py` to `metamodel.py`

### Removed:
- `DagsToCreate` and `GeneticConstructs`, which were invalid

### Added:
- `new_model` and `opened` context managers
- Test that checks each model class
- Support for `.chemfish/connection.json`
- Better main method, useful for testing with the active db


## [2.0.0] - 2020-08-14

### Changed:
- Build infrastructure and code organization.

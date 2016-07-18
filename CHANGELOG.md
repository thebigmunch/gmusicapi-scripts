# Change Log

Notable changes for the [gmusicapi-scripts](https://github.com/thebigmunch/gmusicapi-scripts) project. This project uses [Semantic Versioning](http://semver.org/) principles.


## [0.5.0](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.5.0) (2016-07-18)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/0.4.0...0.5.0)

### Fixed

* Update template_to_base_path for gmusicapi-wrapper changes. Fixes issue with using incorrect tag field.


## [0.4.0](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.4.0) (2016-06-03)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/0.3.0...0.4.0)

### Changed

* Update dependency versions.
* Exit scripts on authentication failures.


## [0.3.0](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.3.0) (2016-02-29)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/0.2.1...0.3.0)

### Added

* Output songs to be filtered in dry-run.

### Changed

* Change --include-all to --all-includes to match parameter change in gmusicapi-wrapper.
* Change --exclude-all to --all-excludes to match parameter change in gmusicapi-wrapper.
* Change behavior of --max-depth=0; it now limits to the current directory level instead of being infinite recursion.


## [0.2.1](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.2.1) (2016-02-15)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/0.2.0...0.2.1)

### Fixed

* Use correct track number metadata key for sorting.
* Fix delete on success check.

### Changed

* Update supported gmusicapi-wrapper versions.


## [0.2.0](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.2.0) (2016-02-13)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/0.1.0...0.2.0)

### Added

* Python 3 support.

### Remove

* Python 2 support.

### Changed

* Port to Python 3. Python 2 is no longer supported.


## [0.1.0](https://github.com/thebigmunch/gmusicapi-scripts/releases/tag/0.1.0) (2015-12-02)

[Commits](https://github.com/thebigmunch/gmusicapi-scripts/compare/b66da631025f5074df0e290aa515b7f18d14fde8...0.1.0)

* First package release for PyPi.

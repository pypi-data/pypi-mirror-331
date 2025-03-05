# Changelog

## 0.1.1 - 2025-03-04

### Changed

* Updated the project structure to PyScaffold 4.6.
* Applied the [Black](https://github.com/psf/black) formatter.

### Added

* An empirical function to calculate the diffuse radiation fraction
  `radtrans.canopy_light.diffuse_radiation`.

## 0.1.0 - 2020-06-14

### Changed

* Renamed the project as ``ecoflux``.
* Restructured the project using [PyScaffold](https://pyscaffold.org).

## 0.0.2 - 2019-01-08

### Added

* `setup.py` and `Makefile` to automate the installation.
* `left` and `right` boundary options in `stats.timeseries.simple_gapfill`.

### Changed

* Shortened some constant names in `constants.py`.
* Reformatted `light_response.py`.
* Updated `.gitignore`.

### Fixed

* An error that occurs when importing `zscore` from `stats.summary`.

## 0.0.1 - 2017-11-11

### Added

* Ecophysiology: Light response functions for photosynthesis.
* Physical chemistry: Saturation water vapor pressure function.
* Radiative transfer
  + Solar angle function
  + Planck's law
  + Canopy light extinction
* Statistics
  + Histogram bin-size calculation
  + Some functions for summary statistics
  + Some time series functions

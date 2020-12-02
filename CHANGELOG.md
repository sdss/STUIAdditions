# Change Log

## [3.0.0] - 2020-07-09

### Changes

- Added changelog
- Added Scripts/dev/telControls.py, ran through linter, made some minor changes,
 added a version number
- Switched to BSD license to conform with SDSS standards
- Major README overhaul to match ObserverTools closely
- Added goto5MCP
- Removed some print statements from guideMonitor2

## [3.1.0] - 2020-11-30

### Changes

- Added all the scripts from STUI because STUI 1.7.11 will remove them.
- Removed APOGEE cals, we want to force observers to run them via SOP.
- Renamed all files to Title Format since they'll be seen by users
- Updates doApoggeeBossScience from nDither to nExposure
- Removed Run_Commands.py, Loop Commands.py, and Pointing Data.py
 as they will be maintained inside STUI

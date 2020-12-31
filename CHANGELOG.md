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

## [3.1.1] - 2020-12-04

### Changes

- Removed APOGEE folder, only one script was in it, Dither Clearing.py, which
 we will not use

- Removed engineering folder, only one script was in it, which we will not use

- Removed old folder. Now that they're in the git history, we can still access
 them if we need them, but they're no longer cluttering
 
- Reformatted some files

# [3.1.2] - 2020-12-08

### Changes

- Get Versions.py now shows the git version of STUIAdditions

- Timer.py works for MWM plates

- Many prints in Guide Monitor 2 and Timer were moved inside sr.debug if
 statements

# [3.1.3] - 2020-12-30

### Changes

- Timer.py has a fudge factor adjusted for the overhead on each cart

- Fixed a bug that prevented Fiducial Monitor from playing its sound

- Log Support callbacks are now APOGEE-read based and only write if one hasn't
 been written in 12 minutes (dt can be adjusted)
  
- Axis Error scripts were refactored for consistent naming

- Guide Monitor 2 wastes less space and has some fatty chunks of code removed

- Some old prints were commented or moved to sr.debug ifs

- FluxMonitorWindow was removed, the usefulness of a non-script STUI extension
 was completely lost to me.

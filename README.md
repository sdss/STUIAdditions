# STUIAdditions

This is a repository of STUI Scripts. As of STUI  1.7.12, this repository
 replaced APO-local as the main home for observer-maintained scripts. This
 repository is required for normal night operations.
 
## Authors

Dylan Gatlin, Elena Malanuchenko, Russel Owens, Dan Oravetz

## Accessing/Using
STUI checks a few locations for STUIAdditions directories. If this directory
 is there when STUI starts, then you will have access to the directory and
 any scripts found inside will be available in STUI. The recommended install
 procedure is as follows:
 
### Mac Installation
```bash
cd ~/Library/Application\ Support/
git clone https://github.com/sdss/STUIAdditions.git
```

### Linux Installation
```bash
mkdir -p ~/software/
cd ~/software/
git clone https://github.com/sdss/STUIAdditions.git
```

### Updating
If at any time changes are made, you can update your local version by running
 `git pull` from the top of the repository.

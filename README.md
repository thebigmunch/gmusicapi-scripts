gmusicapi-scripts
=================

A collection of scripts for [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API).

### gmdownload

[gmdownload.py](gmdownload.py) is a dumb download script. It will download all songs matching the filters.

### gmsync

[gmsync.py](gmsync.py) is a smart sync script. It can both upload and download songs. Songs from the source that exist on the destination will not be uploaded or downloaded.

### gmupload

[gmupload.py](gmupload.py) is a dumb upload script. It will make an upload request for all files matching the input.

## Requirements
* Python 2.7 (Probably 2.6, but untested.)
* [docopt](https://github.com/docopt/docopt)
* [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API)
* [mutagen](https://code.google.com/p/mutagen/) ([gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API) should install this for you)
* avconv (See [here](http://unofficial-google-music-api.readthedocs.org/en/latest/usage.html#usage))

## Installation

See the [INSTALL.md](INSTALL.md) file or the online [Wiki](https://github.com/thebigmunch/gmusicapi-scripts/wiki)

## Usage

See the [USAGE.md](USAGE.md) file or the online [Wiki](https://github.com/thebigmunch/gmusicapi-scripts/wiki)

## Contact

You can contact the author in ``#gmusicapi`` on ``irc.freenode.net`` or by [e-mail](mailto:mail@thebigmunch.me)

-----

Copyright (c) 2014 [thebigmunch](mailto:mail@thebigmunch.me). Licensed under the MIT License. See [LICENSE](LICENSE).

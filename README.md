gmusicapi-scripts
=================

A collection of scripts for [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API) using [gmusicapi-wrapper](https://github.com/thebigmunch/gmusicapi-wrapper).

## Scripts

### gmdelete

gmdelete is a script to delete songs from your Google Music library.

### gmdownload

gmdownload is a dumb download script. It will download all songs matching the filters.

### gmsearch

gmsearch is a script to search your Google Music library.

### gmsync

gmsync is a smart sync script. It can both upload and download songs. Songs from the source that exist on the destination will not be uploaded or downloaded.

### gmupload

gmupload is a dumb upload script. It will make an upload request for all files matching the input.

## Requirements

* Python 2.7
* [gmusicapi](https://github.com/simon-weber/Unofficial-Google-Music-API)
* [gmusicapi-wrapper](https://github.com/thebigmunch/gmusicapi-wrapper)
* [mutagen](https://bitbucket.org/lazka/mutagen)
* [docopt](https://github.com/docopt/docopt)
* ffmpeg or avconv for uploading non-mp3 files (See [here](http://unofficial-google-music-api.readthedocs.org/en/latest/usage.html#usage))

## Installation

* Stable release

		pip install gmusicapi-scripts
		pip install git+https://github.com/thebigmunch/gmusicapi-scripts

* Development release

		pip install git+https://github.com/thebigmunch/gmusicapi-scripts@devel

## Usage

See the [USAGE.md](https://github.com/thebigmunch/gmusicapi-scripts/blob/master/USAGE.md) file or the online [Wiki](https://github.com/thebigmunch/gmusicapi-scripts/wiki)

## Contributing

See the [CONTRIBUTING.md](https://github.com/thebigmunch/gmusicapi-scripts/blob/master/CONTRIBUTING.md) file

## Contact

You can contact the author in ``#gmusicapi`` on ``irc.freenode.net`` or by [e-mail](mailto:mail@thebigmunch.me)

## Donate

Donations, as any compliment, are appreciated but not expected.

[![Bitcoin](http://img.shields.io/badge/bitcoin-donate-green.svg?style=flat-square)](https://coinbase.com/thebigmunch) [![Flattr](http://img.shields.io/badge/flattr-donate-green.svg?style=flat-square)](https://flattr.com/thing/2419308) [![PayPal](http://img.shields.io/badge/paypal-donate-green.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=DHDVLSYW8V8N4&lc=US&item_name=thebigmunch&currency_code=USD)  
[![Coinbase](http://img.shields.io/badge/coinbase-referral-orange.svg?style=flat-square)](https://coinbase.com/?r=52502f01e0fdd4d3ef000253&utm_campaign=user-referral&src=referral-link) [![Digital Ocean](http://img.shields.io/badge/digital ocean-referral-orange.svg?style=flat-square)](https://www.digitalocean.com/?refcode=3823208a0597) [![Namecheap](http://img.shields.io/badge/namecheap-referral-orange.svg?style=flat-square)](http://www.namecheap.com/?aff=67208)

-----

Copyright (c) 2015 [thebigmunch](mailto:mail@thebigmunch.me). Licensed under the MIT License. See [LICENSE](LICENSE).

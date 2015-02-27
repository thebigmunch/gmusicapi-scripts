#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A download script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdownload.py (-h | --help)
  gmdownload.py [-f FILTER]... [options] [<output>]

Arguments:
  output                        Output file or directory name which can include a template pattern.
                                Defaults to name suggested by Google Music in your current directory.

Options:
  -h, --help                    Display help message.
  -c CRED, --cred CRED          Specify oauth credential file name to use/create. [Default: oauth]
  -U ID --uploader-id ID        A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').
                                This should only be provided when the default does not work.
  -l, --log                     Enable gmusicapi logging.
  -d, --dry-run                 Output list of songs that would be downloaded.
  -q, --quiet                   Don't output status messages.
                                With -l,--log will display gmusicapi warnings.
                                With -d,--dry-run will display song list.
  -f FILTER, --filter FILTER    Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                Songs can match any filter criteria.
                                This option can be set multiple times.
  -a, --all                     Songs must match all filter criteria.
"""

import sys

from gmusicapi_scripts.gmdownload import main

sys.exit(main())

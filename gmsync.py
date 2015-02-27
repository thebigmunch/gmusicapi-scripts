#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py up [-e PATTERN]... [-f FILTER]... [options] [<input>]...
  gmsync.py down [-f FILTER]... [options] [<output>]
  gmsync.py [-e PATTERN]... [-f FILTER]... [options] [<input>]...

Commands:
  up                             Sync local songs to Google Music. Default behavior.
  down                           Sync Google Music songs to local computer.

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.
  output                         Output file or directory name which can include a template pattern.
                                 Defaults to name suggested by Google Music in your current directory.

Options:
  -h, --help                     Display help message.
  -c CRED, --cred CRED           Specify oauth credential file name to use/create. [Default: oauth]
  -U ID --uploader-id ID         A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').
                                 This should only be provided when the default does not work.
  -l, --log                      Enable gmusicapi logging.
  -m, --match                    Enable scan and match.
  -d, --dry-run                  Output list of songs that would be uploaded.
  -q, --quiet                    Don't output status messages.
                                 With -l,--log will display gmusicapi warnings.
                                 With -d,--dry-run will display song list.
  -e PATTERN, --exclude PATTERN  Exclude file paths matching a Python regex pattern.
                                 This option can be set multiple times.
  -f FILTER, --filter FILTER     Filter Google songs (download) or local songs (upload) by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
"""

import sys

from gmusicapi_scripts.gmsync import main

sys.exit(main())

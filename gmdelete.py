#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to delete songs from your Google Music library using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdelete.py (-h | --help)
  gmdelete.py [options] [-f FILTER]...

Options:
  -h, --help                         Display help message.
  -u USERNAME, --user USERNAME       Your Google username or e-mail address.
  -p PASSWORD, --pass PASSWORD       Your Google or app-specific password.
  -l, --log                          Enable gmusicapi logging.
  -d, --dry-run                      Output list of songs that would be deleted.
  -q, --quiet                        Don't output status messages.
                                     With -l,--log will display gmusicapi warnings.
                                     With -d,--dry-run will display song list.
  -f FILTER, --filter FILTER         Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                     Songs can match any filter criteria.
                                     This option can be set multiple times.
  -a, --all                          Songs must match all filter criteria.
  -y, --yes                          Delete songs without asking for confirmation.
"""

import sys

from gmusicapi_scripts.gmdelete import main

sys.exit(main())

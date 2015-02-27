#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to search your Google Music library using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsearch.py (-h | --help)
  gmsearch.py [options] [-f FILTER]...

Options:
  -h, --help                         Display help message.
  -u USERNAME, --user USERNAME       Your Google username or e-mail address.
  -p PASSWORD, --pass PASSWORD       Your Google or app-specific password.
  -l, --log                          Enable gmusicapi logging.
  -q, --quiet                        Don't output status messages.
                                     With -l,--log will display gmusicapi warnings.
  -f FILTER, --filter FILTER         Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                     Songs can match any filter criteria.
                                     This option can be set multiple times.
  -a, --all                          Songs must match all filter criteria.
  -y, --yes                          Display results without asking for confirmation.
"""

import sys

from gmusicapi_scripts.gmsearch import main

sys.exit(main())

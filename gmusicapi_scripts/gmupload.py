#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmupload.py (-h | --help)
  gmupload.py [-e PATTERN]... [-f FILTER]... [options] [<input>]...

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.

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
  -f FILTER, --filter FILTER     Filter local songs by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
"""

from __future__ import unicode_literals

import logging
import os

from docopt import docopt

from gmusicapi_wrapper import MusicManagerWrapper

QUIET = 25
logging.addLevelName(25, "QUIET")

logger = logging.getLogger('gmusicapi_wrapper')
sh = logging.StreamHandler()
logger.addHandler(sh)


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	filters = [tuple(filt.split(':', 1)) for filt in cli['filter']]

	excludes = "|".join(pattern.decode('utf8') for pattern in cli['exclude']) if cli['exclude'] else None

	upload_songs, _, exclude_songs = mmw.get_local_songs(cli['input'], filters=filters, filter_all=cli['all'], exclude_patterns=excludes)

	upload_songs.sort()
	exclude_songs.sort()

	if cli['dry-run']:
		logger.info("Found {0} song(s) to upload".format(len(upload_songs)))

		if upload_songs:
			logger.info("\nSongs to upload:\n")

			for song in upload_songs:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to upload")

		if exclude_songs:
			logger.info("\nSongs to exclude:\n")

			for song in exclude_songs:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to exclude")
	else:
		if upload_songs:
			logger.info("Uploading {0} song(s) to Google Music\n".format(len(upload_songs)))

			mmw.upload(upload_songs, enable_matching=cli['match'])
		else:
			logger.info("\nNo songs to upload")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

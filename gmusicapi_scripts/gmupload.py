#!/usr/bin/env python3
# coding=utf-8

"""
An upload script for Google Music using https://github.com/simon-weber/gmusicapi.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmupload (-h | --help)
  gmupload [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...

Arguments:
  input                                 Files, directories, or glob patterns to upload.
                                        Defaults to current directory.

Options:
  -h, --help                            Display help message.
  -c CRED, --cred CRED                  Specify oauth credential file name to use/create. [Default: oauth]
  -U ID --uploader-id ID                A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').
                                        This should only be provided when the default does not work.
  -l, --log                             Enable gmusicapi logging.
  -m, --match                           Enable scan and match.
  -d, --dry-run                         Output list of songs that would be uploaded.
  -q, --quiet                           Don't output status messages.
                                        With -l,--log will display gmusicapi warnings.
                                        With -d,--dry-run will display song list.
  --delete-on-success                   Delete successfully uploaded local files.
  -R, --no-recursion                    Disable recursion when scanning for local files.
                                        This is equivalent to setting --max-depth to 0.
  --max-depth DEPTH                     Set maximum depth of recursion when scanning for local files.
                                        Default is infinite recursion.
                                        Has no effect when -R, --no-recursion set.
  -e PATTERN, --exclude PATTERN         Exclude file paths matching a Python regex pattern.
  -f FILTER, --include-filter FILTER    Include local songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -F FILTER, --exclude-filter FILTER    Exclude local songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -a, --all-includes                    Songs must match all include filter criteria to be included.
  -A, --all-excludes                    Songs must match all exclude filter criteria to be excluded.

Patterns can be any valid Python regex patterns.
"""

import logging
import os
import sys

from docopt import docopt

from gmusicapi_wrapper import MusicManagerWrapper

QUIET = 25
logging.addLevelName(25, "QUIET")

logger = logging.getLogger('gmusicapi_wrapper')
sh = logging.StreamHandler()
logger.addHandler(sh)


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	if cli['no-recursion']:
		cli['max-depth'] = 0
	else:
		cli['max-depth'] = int(cli['max-depth']) if cli['max-depth'] else float('inf')

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	mmw = MusicManagerWrapper(enable_logging=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	if not mmw.is_authenticated:
		sys.exit()

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	songs_to_upload, songs_to_filter, songs_to_exclude = mmw.get_local_songs(
		cli['input'], include_filters=include_filters, exclude_filters=exclude_filters,
		all_includes=cli['all-includes'], all_excludes=cli['all-excludes'],
		exclude_patterns=cli['exclude'], max_depth=cli['max-depth']
	)

	songs_to_upload.sort()
	songs_to_exclude.sort()

	if cli['dry-run']:
		logger.info("\nFound {0} song(s) to upload".format(len(songs_to_upload)))

		if songs_to_upload:
			logger.info("\nSongs to upload:\n")

			for song in songs_to_upload:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to upload")

		if songs_to_filter:
			logger.info("\nSongs to filter:\n")

			for song in songs_to_filter:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to filter")

		if songs_to_exclude:
			logger.info("\nSongs to exclude:\n")

			for song in songs_to_exclude:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to exclude")
	else:
		if songs_to_upload:
			logger.info("\nUploading {0} song(s) to Google Music\n".format(len(songs_to_upload)))

			mmw.upload(songs_to_upload, enable_matching=cli['match'], delete_on_success=cli['delete-on-success'])
		else:
			logger.info("\nNo songs to upload")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmupload.py (-h | --help)
  gmupload.py [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...

Arguments:
  input                          Files, directories, or glob patterns to upload.
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
                                        This is equivalent to setting --max-depth to 1.
  --max-depth DEPTH                     Set maximum depth of recursion when scanning for local files.
                                        Default is infinite recursion. [Default: 0]
  -e PATTERN, --exclude PATTERN         Exclude file paths matching a Python regex pattern.
  -f FILTER, --include-filter FILTER    Include local songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -F FILTER, --exclude-filter FILTER    Exclude local songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -a, --include-all                     Songs must match all include filter criteria to be included.
  -A, --exclude-all                     Songs must match all exclude filter criteria to be excluded.

Patterns can be any valid Python regex patterns.
"""

from __future__ import unicode_literals

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


# From https://code.activestate.com/recipes/572200/
def win32_unicode_argv():
	"""Uses shell32.GetCommandLineArgvW to get sys.argv as a list of Unicode strings."""

	from ctypes import POINTER, byref, cdll, c_int, windll
	from ctypes.wintypes import LPCWSTR, LPWSTR

	GetCommandLineW = cdll.kernel32.GetCommandLineW
	GetCommandLineW.argtypes = []
	GetCommandLineW.restype = LPCWSTR

	CommandLineToArgvW = windll.shell32.CommandLineToArgvW
	CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
	CommandLineToArgvW.restype = POINTER(LPWSTR)

	cmd = GetCommandLineW()
	argc = c_int(0)
	argv = CommandLineToArgvW(cmd, byref(argc))
	if argc.value > 0:
		# Remove Python executable and commands if present
		start = argc.value - len(sys.argv)
		return [argv[i] for i in xrange(start, argc.value)]


def main():
	if os.name == 'nt':
		sys.argv = win32_unicode_argv()
	else:
		sys.argv = [arg.decode(sys.stdin.encoding) for arg in sys.argv]

	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	filepath_exclude_patterns = "|".join(pattern for pattern in cli['exclude']) if cli['exclude'] else None

	songs_to_upload, _, songs_to_exclude = mmw.get_local_songs(
		cli['input'], include_filters, exclude_filters, cli['include-all'], cli['exclude-all'],
		filepath_exclude_patterns, not cli['no-recursion'], int(cli['max-depth'])
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

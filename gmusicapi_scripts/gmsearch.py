#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to search your Google Music library using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsearch.py (-h | --help)
  gmsearch.py [options] [-f FILTER]... [-F FILTER]...

Options:
  -h, --help                            Display help message.
  -u USERNAME, --user USERNAME          Your Google username or e-mail address.
  -p PASSWORD, --pass PASSWORD          Your Google or app-specific password.
  -I ID --android-id ID                 An Android device id.
  -l, --log                             Enable gmusicapi logging.
  -q, --quiet                           Don't output status messages.
                                        With -l,--log will display gmusicapi warnings.
  -f FILTER, --include-filter FILTER    Include Google songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -F FILTER, --exclude-filter FILTER    Exclude Google songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -a, --include-all                     Songs must match all include filter criteria to be included.
  -A, --exclude-all                     Songs must match all exclude filter criteria to be excluded.
  -y, --yes                             Display results without asking for confirmation.

Patterns can be any valid Python regex patterns.
"""

from __future__ import unicode_literals

import logging
import os
import sys

from docopt import docopt

from gmusicapi_wrapper import MobileClientWrapper

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

	mcw = MobileClientWrapper()
	mcw.login(cli['user'], cli['pass'], cli['android-id'])

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	logger.info("Scanning for songs...\n")
	search_results, _ = mcw.get_google_songs(include_filters, exclude_filters, cli['include-all'], cli['exclude-all'])
	search_results.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

	if search_results:
		confirm = cli['yes'] or cli['quiet']
		logger.info("")

		if confirm or raw_input("Display {} results? (y/n) ".format(len(search_results))) in ("y", "Y"):
			logger.log(QUIET, "")

			for song in search_results:
				title = song.get('title', "<empty>")
				artist = song.get('artist', "<empty>")
				album = song.get('album', "<empty>")
				song_id = song['id']

				logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
	else:
		logger.info("\nNo songs found matching query")

	mcw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A download script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdownload.py (-h | --help)
  gmdownload.py [-f FILTER]... [-F FILTER]... [options] [<output>]

Arguments:
  output                                Output file or directory name which can include a template pattern.
                                        Defaults to name suggested by Google Music in your current directory.

Options:
  -h, --help                            Display help message.
  -c CRED, --cred CRED                  Specify oauth credential file name to use/create. [Default: oauth]
  -U ID --uploader-id ID                A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').
                                        This should only be provided when the default does not work.
  -l, --log                             Enable gmusicapi logging.
  -d, --dry-run                         Output list of songs that would be downloaded.
  -q, --quiet                           Don't output status messages.
                                        With -l,--log will display gmusicapi warnings.
                                        With -d,--dry-run will display song list.
  -f FILTER, --include-filter FILTER    Include Google songs by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -F FILTER, --exclude-filter FILTER    Exclude Google songs by field:pattern filter (e.g. "artist:Muse").
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

	if not cli['output']:
		cli['output'] = os.getcwd()

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	songs_to_download, _ = mmw.get_google_songs(include_filters, exclude_filters, cli['include-all'], cli['exclude-all'])

	songs_to_download.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

	if cli['dry-run']:
		logger.info("\nFound {0} song(s) to download".format(len(songs_to_download)))

		if songs_to_download:
			logger.info("\nSongs to download:\n")

			for song in songs_to_download:
				title = song.get('title', "<empty>")
				artist = song.get('artist', "<empty>")
				album = song.get('album', "<empty>")
				song_id = song['id']

				logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
		else:
			logger.info("\nNo songs to download")
	else:
		if songs_to_download:
			logger.info("\nDownloading {0} song(s) from Google Music\n".format(len(songs_to_download)))
			mmw.download(songs_to_download, cli['output'])
		else:
			logger.info("\nNo songs to download")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

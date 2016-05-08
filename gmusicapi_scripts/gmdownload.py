#!/usr/bin/env python3
# coding=utf-8

"""
A download script for Google Music using https://github.com/simon-weber/gmusicapi.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdownload (-h | --help)
  gmdownload [-f FILTER]... [-F FILTER]... [options] [<output>]

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

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	if not cli['output']:
		cli['output'] = os.getcwd()

	mmw = MusicManagerWrapper(enable_logging=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	if not mmw.is_authenticated:
		sys.exit()

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	songs_to_download, songs_to_filter = mmw.get_google_songs(
		include_filters=include_filters, exclude_filters=exclude_filters,
		all_includes=cli['all-includes'], all_excludes=cli['all-excludes']
	)

	songs_to_download.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('track_number')))

	if cli['dry-run']:
		logger.info("\nFound {0} song(s) to download".format(len(songs_to_download)))

		if songs_to_download:
			logger.info("\nSongs to download:\n")

			for song in songs_to_download:
				title = song.get('title', "<title>")
				artist = song.get('artist', "<artist>")
				album = song.get('album', "<album>")
				song_id = song['id']

				logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
		else:
			logger.info("\nNo songs to download")

		if songs_to_filter:
			logger.info("\nSongs to filter:\n")

			for song in songs_to_filter:
				logger.log(QUIET, song)
		else:
			logger.info("\nNo songs to filter")
	else:
		if songs_to_download:
			logger.info("\nDownloading {0} song(s) from Google Music\n".format(len(songs_to_download)))
			mmw.download(songs_to_download, template=cli['output'])
		else:
			logger.info("\nNo songs to download")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

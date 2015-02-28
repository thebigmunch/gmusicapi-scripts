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

	if not cli['output']:
		cli['output'] = os.getcwd()

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	filters = [tuple(filt.split(':', 1)) for filt in cli['filter']]

	download_songs, _ = mmw.get_google_songs(filters=filters, filter_all=cli['all'])

	download_songs.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

	if cli['dry-run']:
		logger.info("Found {0} song(s) to download".format(len(download_songs)))

		if download_songs:
			logger.info("\nSongs to download:\n")

			for song in download_songs:
				title = song.get('title', "<empty>")
				artist = song.get('artist', "<empty>")
				album = song.get('album', "<empty>")
				song_id = song['id']

				logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
		else:
			logger.info("\nNo songs to download")
	else:
		if download_songs:
			logger.info("Downloading {0} song(s) from Google Music\n".format(len(download_songs)))
			mmw.download(download_songs, cli['output'])
		else:
			logger.info("\nNo songs to download")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

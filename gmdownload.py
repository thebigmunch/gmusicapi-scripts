#!/usr/bin/env python2

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

from __future__ import print_function, unicode_literals

import os
import sys

from docopt import docopt

from gmwrapper import MusicManagerWrapper
from utils import safe_print


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	print_ = safe_print if not cli['quiet'] else lambda *args, **kwargs: None

	if not cli['output']:
		cli['output'] = os.getcwd()

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_file=cli['cred'], uploader_id=cli['uploader-id'])

	download_songs = mmw.get_google_songs(filters=cli['filter'], filter_all=cli['all'])

	download_songs.sort(key=lambda song: (song['artist'], song['album'], song['track_number']))

	if cli['dry-run']:
		print_("Found {0} songs to download".format(len(download_songs)))

		if download_songs:
			safe_print("\nSongs to download:\n")
			for song in download_songs:
				safe_print("{0} by {1}".format(song['title'], song['artist']))
		else:
			safe_print("\nNo songs to download")
	else:
		if download_songs:
			print_("Downloading {0} songs from Google Music\n".format(len(download_songs)))
			mmw.download(download_songs, cli['output'])
		else:
			safe_print("\nNo songs to download")

	mmw.logout()
	print_("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit("\n\nExiting")

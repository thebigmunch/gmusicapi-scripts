#!/usr/bin/env python2

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
  -f FILTER, --filter FILTER     Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
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

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login()

	excludes = "|".join(pattern.decode('utf8') for pattern in cli['exclude']) if cli['exclude'] else None

	upload_songs, exclude_songs = mmw.get_local_songs(cli['input'], exclude_patterns=excludes, filters=cli['filter'], filter_all=cli['all'])

	upload_songs.sort()
	exclude_songs.sort()

	if cli['dry-run']:
		print_("Found {0} songs to upload".format(len(upload_songs)))

		if upload_songs:
			safe_print("\nSongs to upload:\n")

			for song in upload_songs:
				safe_print(song)
		else:
			safe_print("\nNo songs to upload")

		if exclude_songs:
			safe_print("\nSongs to exclude:\n")

			for song in exclude_songs:
				safe_print(song)
		else:
			safe_print("\nNo songs to exclude")
	else:
		if upload_songs:
			print_("Uploading {0} songs to Google Music\n".format(len(upload_songs)))

			mmw.upload(upload_songs, enable_matching=cli['match'])
		else:
			safe_print("\nNo songs to upload")

	mmw.logout()
	print("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\n\nExiting")
		sys.exit()

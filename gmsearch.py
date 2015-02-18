#!/usr/bin/env python2

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

from __future__ import print_function, unicode_literals

import sys

from docopt import docopt

from gmwrapper import MobileClientWrapper
from utils import safe_print


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	print_ = safe_print if not cli['quiet'] else lambda *args, **kwargs: None

	mcw = MobileClientWrapper()
	mcw.login(cli['user'], cli['pass'])

	print_("Scanning for songs...\n")
	search_songs = mcw.get_google_songs(filters=cli['filter'], filter_all=cli['all'])
	search_songs.sort(key=lambda song: (song['artist'], song['album'], song['trackNumber']))

	if search_songs:
		if cli['yes'] or raw_input("Display results? (y/n) ").lower() == "y":
			print_()

			for song in search_songs:
				title = song.get('title', "<empty>")
				artist = song.get('artist', "<empty>")
				album = song.get('album', "<empty>")

				print("{0} _by_ {1} _from_ {2} ({3})".format(title, artist, album, song['id']))

			print_()
	else:
		safe_print("\nNo songs found matching query")

	mcw.logout()
	print_("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit("\n\nExiting")

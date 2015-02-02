#!/usr/bin/env python2

"""
A script to delete songs from your Google Music library using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmdelete.py (-h | --help)
  gmdelete.py [options] [-f FILTER]...

Options:
  -h, --help                         Display help message.
  -u USERNAME, --user USERNAME       Your Google username or e-mail address.
  -p PASSWORD, --pass PASSWORD       Your Google or app-specific password.
  -l, --log                          Enable gmusicapi logging.
  -d, --dry-run                      Output list of songs that would be deleted.
  -q, --quiet                        Don't output status messages.
                                     With -l,--log will display gmusicapi warnings.
                                     With -d,--dry-run will display song list.
  -f FILTER, --filter FILTER         Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                     Songs can match any filter criteria.
                                     This option can be set multiple times.
  -a, --all                          Songs must match all filter criteria.
  -y, --yes                          Delete songs without asking for confirmation.
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

	delete_songs = mcw.get_google_songs(filters=cli['filter'], filter_all=cli['all'])

	if cli['dry-run']:
		print_("Found {0} songs to delete".format(len(delete_songs)))

		if delete_songs:
			safe_print("\nSongs to delete:\n")

			for song in delete_songs:
				safe_print("{0} by {1}".format(song['title'], song['artist']))
		else:
			safe_print("\nNo songs to delete")
	else:
		if delete_songs:
			if cli['yes'] or raw_input("Are you sure you want to delete {0} songs from Google Music? (y/n) ".format(len(delete_songs))).lower() == "y":
				print_("\nDeleting {0} songs from Google Music\n".format(len(delete_songs)))

				songnum = 0
				total = len(delete_songs)
				pad = len(str(total))

				for song in delete_songs:
					mcw.api.delete_songs(song['id'])
					songnum += 1

					print_("Deleted {num:>{pad}}/{total} songs from Google Music".format(num=songnum, pad=pad, total=total), end="\r")
					sys.stdout.flush()

				print_()
			else:
				print_("No songs deleted.")
		else:
			safe_print("\nNo songs to delete")

	mcw.logout()
	print_("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit("\n\nExiting")

#!/usr/bin/env python2

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py up [-e PATTERN]... [-f FILTER]... [options] [<input>]...
  gmsync.py down [-f FILTER]... [options] [<output>]
  gmsync.py [-e PATTERN]... [-f FILTER]... [options] [<input>]...

Commands:
  up                             Sync local songs to Google Music. Default behavior.
  down                           Sync Google Music songs to local computer.

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.
  output                         Output file or directory name which can include a template pattern.
                                 Defaults to name suggested by Google Music in your current directory.

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
                                 This option can be set multiple times.
  -f FILTER, --filter FILTER     Filter Google songs (download) or local songs (upload) by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
"""

from __future__ import print_function, unicode_literals

import os
import sys

from docopt import docopt

from gmwrapper import compare_song_collections, MusicManagerWrapper
from utils import safe_print

CHARACTER_REPLACEMENTS = {
	'\\': '-', '/': ',', ':': '-', '*': 'x', '<': '[',
	'>': ']', '|': '!', '?': '', '"': "''"
}

TEMPLATE_PATTERNS = {
	'%artist%': 'artist', '%title%': 'title', '%track%': 'tracknumber',
	'%track2%': 'tracknumber', '%album%': 'album', '%date%': 'date',
	'%genre%': 'genre', '%albumartist%': 'albumartist', '%disc%': 'discnumber'
}


def template_to_base_path(google_songs, template):
	"""Get common base output path for a set of songs."""

	song_paths = []

	for song in google_songs:
		drive, path = os.path.splitdrive(template)
		parts = []

		while True:
			newpath, tail = os.path.split(path)

			if newpath == path:
				break

			parts.append(tail)
			path = newpath

		parts.reverse()

		for i, part in enumerate(parts):
			if "%suggested%" in part:
				parts[i] = ''
				del parts[i+1:]
			for key in TEMPLATE_PATTERNS:
				if key in part and TEMPLATE_PATTERNS[key] in song:
					parts[i] = parts[i].replace(key, song[TEMPLATE_PATTERNS[key]])

			for char in CHARACTER_REPLACEMENTS:
				if char in parts[i]:
					parts[i] = parts[i].replace(char, CHARACTER_REPLACEMENTS[char])

		if drive:
			filename = os.path.join(drive, os.sep, *parts)
		else:
			filename = os.path.join(*parts)

		song_paths.append(filename)

	common_path = os.path.commonprefix(song_paths)

	local_path = [common_path] if common_path else [os.getcwd()]

	return local_path


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	print_ = safe_print if not cli['quiet'] else lambda *args, **kwargs: None

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	if not cli['output']:
		cli['output'] = os.getcwd()

	# Pre-compile regex for exclude option.
	excludes = "|".join(pattern.decode('utf8') for pattern in cli['exclude']) if cli['exclude'] else None

	mmw = MusicManagerWrapper(log=cli['log'], quiet=cli['quiet'])
	mmw.login(oauth_file=cli['cred'], uploader_id=cli['uploader-id'])

	if cli['down']:
		google_songs = mmw.get_google_songs(filters=cli['filter'], filter_all=cli['all'])
		local_songs, exclude_songs = mmw.get_local_songs(cli['input'], exclude_patterns=excludes)

		cli['input'] = template_to_base_path(google_songs, cli['output'])

		print_("Scanning for missing songs...")
		download_songs = compare_song_collections(google_songs, local_songs)

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
	else:
		google_songs = mmw.get_google_songs()
		local_songs, exclude_songs = mmw.get_local_songs(cli['input'], exclude_patterns=excludes, filters=cli['filter'], filter_all=cli['all'])

		print_("Scanning for missing songs...")

		upload_songs = compare_song_collections(local_songs, google_songs)

		# Sort lists for sensible output.
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
	print_("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit("\n\nExiting")

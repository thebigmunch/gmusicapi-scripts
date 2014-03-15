#!/usr/bin/env python

"""
A download script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net or by e-mail at mail@thebigmunch.me.
"""

from __future__ import print_function, unicode_literals
import argparse
import mutagen
import os
import re
import sys
import shutil
from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

INVALID_CHARS = {
	'\\': '-', '/': ',', ':': '-', '*': 'x', '<': '[',
	'>': ']', '|': '!', '?': '', '"': "''"
}

FILTER_FIELDS = [
	'artist', 'title', 'album', 'album_artist'
]

TEMPLATE_PATTERNS = {
	'%artist%': 'artist', '%title%': 'title', '%track%': 'tracknumber',
	'%track2%': 'tracknumber', '%album%': 'album', '%date%': 'date',
	'%genre%': 'genre', '%albumartist%': 'albumartist', '%disc%': 'discnumber'
}

# Parse command line for arguments.
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-c', '--cred', default='oauth', help='Specify oauth credential file name to use/create\n(Default: "oauth" -> ' + OAUTH_FILEPATH + ')')
parser.add_argument('-l', '--log', action='store_true', default=False, help='Enable gmusicapi logging')
parser.add_argument('-f', '--filter', action='append', help='Filter Google songs by field:pattern pair (e.g. "artist:Muse")\nThis option can be set multiple times')
parser.add_argument('-a', '--all', action='store_true', default=False, help='Songs must match all filter criteria\n(Default: Songs can match any filter criteria')
parser.add_argument('-d', '--dry-run', action='store_true', default=False, help='Output list of songs that would be uploaded')
parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Don\'t output status messages\n-l,--log will display gmusicapi warnings\n-d,--dry-run will display song list')
parser.add_argument('output', nargs='?', default=os.getcwd(), help='Output file or directory name which can include a template pattern\nDefaults to name suggested by Google Music in your current directory')
opts = parser.parse_args()

mm = Musicmanager(debug_logging=opts.log)

_print = print if not opts.quiet else lambda *a, **k: None


def do_auth():
	"""
	Authenticates the mm client.
	"""

	attempts = 0

	oauth_file = os.path.join(os.path.dirname(OAUTH_FILEPATH), opts.cred + '.cred')

	# Attempt to login. Perform oauth only when necessary.
	while attempts < 3:
		if mm.login(oauth_credentials=oauth_file):
			break
		mm.perform_oauth(storage_filepath=oauth_file)
		attempts += 1

	if not mm.is_authenticated():
		_print("Sorry, login failed.")
		return

	_print("Successfully logged in.\n")


def do_download(songs, total):
	"""
	Downloads the songs with a counter.
	"""

	songnum = 0
	errors = {}
	pad = len(str(total))

	for song in songs:
		songnum += 1

		try:
			_print("Downloading  {0} by {1}".format(song['title'], song['artist']), end="\r")
			sys.stdout.flush()
			filename, audio = mm.download_song(song['id'])
		except CallFailure as e:
			_print("({num:>{pad}}/{total}) Failed to download  {file} | {error}".format(num=songnum, total=total, file=filename, error=e, pad=pad).encode('utf8'))
			errors[filename] = e
		else:
			filename = make_file_name(filename, audio)
			shutil.move('temp.mp3', filename)
			_print("({num:>{pad}}/{total}) Successfully downloaded  {file}".format(num=songnum, total=total, file=filename, pad=pad).encode('utf8'))

	if errors:
		_print("\n\nThe following errors occurred:\n")
		for filename, e in errors.iteritems():
			_print("{file} | {error}".format(file=filename, error=e).encode('utf8'))
		_print("\nThese files may need to be synced again.\n")


def get_google_songs(filters=None, filter_all=False):
	"""
	Load song list from Google Music library.
	"""

	_print("Loading Google Music songs...")

	google_songs = []

	try:
		songs = mm.get_all_songs()
	except:
		songs = mm.get_uploaded_songs()

	if filters:
		if filter_all:
			for song in songs:
				if all(re.search(value, song[field], re.I) for field, value in filters):
					google_songs.append(song)
		else:
			for song in songs:
				if any(re.search(value, song[field], re.I) for field, value in filters):
					google_songs.append(song)
	else:
		google_songs += songs

	_print("Loaded {0} Google Music songs\n".format(len(google_songs)))

	return google_songs


def make_file_name(filename, audio):
	"""
	Creates directory structure and file name based on user input.
	"""

	with open('temp.mp3', 'wb') as temp:
		temp.write(audio)

	tag = mutagen.File(temp.name, easy=True)

	if opts.output != os.getcwd():
		drive, path = os.path.splitdrive(opts.output)
		parts = []

		while True:
			newpath, tail = os.path.split(path)

			if newpath == path:
				break

			parts.append(tail)
			path = newpath

		parts.reverse()

		for i, part in enumerate(parts):
			for key in TEMPLATE_PATTERNS:
				if key in part and TEMPLATE_PATTERNS[key] in tag:
					if key == '%tr2%':
						tag['tracknumber'] = tag['tracknumber'][0].zfill(2)
						tag.save()

					parts[i] = parts[i].replace(key, tag[TEMPLATE_PATTERNS[key]][0])

			for char in INVALID_CHARS:
				if char in parts[i]:
					parts[i] = parts[i].replace(char, INVALID_CHARS[char])

		filename = os.path.join(drive, *parts) + '.mp3'

		basename, __ = os.path.split(filename)

		if basename:
			try:
				os.makedirs(basename)
			except OSError:
				if not os.path.isdir(basename):
					raise

	return filename


def main():
	do_auth()

	if opts.filter:
		filters = [
			tuple(filter.split(':', 1)) for filter in opts.filter if filter.split(':', 1)[0] in FILTER_FIELDS
		]
	else:
		filters = None

	songs = get_google_songs(filters, opts.all)

	# Sort the list for sensible output.
	songs.sort(key=lambda song: (song['artist'], song['album'], song['track_number']))
	total = len(songs)

	if opts.dry_run:
		_print("Found {0} songs\n".format(total))

		if songs:
			_print("\nSongs to download:\n")
			for song in songs:
				print("{0} by {1}".format(song['title'], song['artist']).encode('utf8'))
		else:
			_print("No songs to download")
	else:
		if songs:
			_print("Downloading {0} songs from Google Music\n".format(total))
			do_download(songs, total)
		else:
			_print("No songs to download")

	# Log out mm session when finished.
	mm.logout()
	_print("\nAll done!")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		mm.logout()
		print("\n\nExiting")

#!/usr/bin/env python

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py up [-e PATTERN]... [options] [<input>...]
  gmsync.py down [-f FILTER]... [options] [<output>]
  gmsync.py [-e PATTERN]... [options] [<input>...]

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
  -l, --log                      Enable gmusicapi logging.
  -m, --match                    Enable scan and match.
  -d, --dry-run                  Output list of songs that would be uploaded.
  -q, --quiet                    Don't output status messages.
                                 With -l,--log will display gmusicapi warnings.
                                 With -d,--dry-run will display song list.
  -e PATTERN, --exclude PATTERN  Exclude file paths matching a Python regex pattern.
                                 This option can be set multiple times.
  -f FILTER, --filter FILTER     Filter Google songs by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
"""

from __future__ import print_function, unicode_literals
from docopt import docopt
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

FORMATS = ('.mp3', '.flac', '.ogg', '.m4a')

# Pre-compile regex for clean_tag function.
track_slash = re.compile('\/\s*\d+')
lead_zeros = re.compile('^0+([0-9]+)')
track_dots = re.compile('^\d+\.+')
non_word = re.compile('[^\w\s]')
spaces = re.compile('\s+')
lead_space = re.compile('^\s+')
trail_space = re.compile('\s+$')
the = re.compile('^the\s+', re.I)


def clean_tag(tag):
	"""
	Clean up metadata tags to improve matching accuracy.
	"""

	tag = unicode(tag)  # Convert tag to unicode.
	tag = tag.lower()  # Convert to lower case.

	tag = track_slash.sub('', tag)  # Remove "/<totaltracks>" from track number.
	tag = lead_zeros.sub(r'\1', tag)  # Remove leading zero(s) from track number.
	tag = track_dots.sub('', tag)  # Remove dots from track number.
	tag = non_word.sub('', tag)  # Remove any non-words.
	tag = spaces.sub(' ', tag)  # Reduce multiple spaces to a single space.
	tag = lead_space.sub('', tag)  # Remove leading space.
	tag = trail_space.sub('', tag)  # Remove trailing space.
	tag = the.sub('', tag)  # Remove leading "the".

	return tag


def compare_song_dicts(src_songs, dest_songs):
	"""
	Create a list of songs from the difference between source destination song dicts.
	"""

	transfer_songs = []

	for key, song in src_songs.iteritems():
		if key not in dest_songs:
			transfer_songs.append(song)

	return transfer_songs


def create_song_key(song):
	"""
	Create dict key for song based on metadata.
	"""

	tags = []

	for tag in filter_tags(song):
		if isinstance(tag, list):
			tag = tag[0]
		tags.append(clean_tag(tag))
		key = '|'.join(tags)

	return key


def do_auth():
	"""
	Authenticate the mm client.
	"""

	attempts = 0

	oauth_file = os.path.join(os.path.dirname(OAUTH_FILEPATH), cli['cred'] + '.cred')

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
	Download songs with a counter.
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


def do_upload(files, total):
	"""
	Upload the files and outputs the upload response with a counter.
	"""

	filenum = 0
	errors = {}
	pad = len(str(total))

	for file in files:
		filenum += 1

		try:
			_print("Uploading  {0}".format(file), end="\r")
			sys.stdout.flush()
			uploaded, matched, not_uploaded = mm.upload(file, transcode_quality="320k", enable_matching=cli['match'])
		except CallFailure as e:
			_print("({num:>{pad}}/{total}) Failed to upload  {file} | {error}".format(num=filenum, total=total, file=file, error=e, pad=pad).encode('utf8'))
			errors[file] = e
		else:
			if uploaded:
				_print("({num:>{pad}}/{total}) Successfully uploaded  {file}".format(num=filenum, total=total, file=file, pad=pad).encode('utf8'))
			elif matched:
				_print("({num:>{pad}}/{total}) Successfully scanned and matched  {file}".format(num=filenum, total=total, file=file, pad=pad).encode('utf8'))
			else:
				check_strings = ["ALREADY_EXISTS", "this song is already uploaded"]
				if any(check_string in not_uploaded[file] for check_string in check_strings):
					response = "ALREADY EXISTS"
				else:
					response = not_uploaded[file]
				_print("({num:>{pad}}/{total}) Failed to upload  {file} | {response}".format(num=filenum, total=total, file=file, response=response, pad=pad).encode('utf8'))

	if errors:
		_print("\n\nThe following errors occurred:\n")
		for file, e in errors.iteritems():
			_print("{file} | {error}".format(file=file, error=e).encode('utf8'))
		_print("\nThese files may need to be synced again.\n")


def exclude_path(path):
	"""
	Exclude file paths based on user input.
	"""

	if excludes and excludes.search(path):
		return True
	else:
		return False


def filter_tags(song):
	"""
	Filter out a missing artist, album, title, or track tag to improve matching accuracy.
	"""

	# Replace track numbers with 0 if no tag exists.
	if song.get('id'):
		if not song.get('track_number'):
			song['track_number'] = '0'
	else:
		if not song.get('tracknumber'):
			song['tracknumber'] = '0'

	# Need both tracknumber (mutagen) and track_number (Google Music) here.
	return [song[tag] for tag in ['artist', 'album', 'title', 'tracknumber', 'track_number'] if song.get(tag)]


def get_google_songs(filters=None, filter_all=False):
	"""
	Load song list from Google Music library.
	"""

	_print("Loading Google Music songs...")

	google_songs = {}

	try:
		songs = mm.get_all_songs()
	except:
		songs = mm.get_uploaded_songs()

	if filters:
		if filter_all:
			for song in songs:
				if all(re.search(value, song[field], re.I) for field, value in filters):
					key = create_song_key(song)

					google_songs[key] = song
		else:
			for song in songs:
				if any(re.search(value, song[field], re.I) for field, value in filters):
					key = create_song_key(song)

					google_songs[key] = song
	else:
		for song in songs:
			key = create_song_key(song)

			google_songs[key] = song

	_print("Loaded {0} Google Music songs\n".format(len(google_songs)))

	return google_songs


def get_local_songs():
	"""
	Load song list from local system.
	"""

	_print("Loading local songs...")

	files = []
	exclude_files = []

	for i in cli['input']:
		i = i.decode('utf8')

		if os.path.isfile(i) and i.lower().endswith(FORMATS):
			if not exclude_path(os.path.abspath(i)):
				files.append(i)
			else:
				exclude_files.append(i)

		if os.path.isdir(i):
			for dirpath, dirnames, filenames in os.walk(i):
				for filename in filenames:
					if filename.lower().endswith(FORMATS):
						file = os.path.join(dirpath, filename)

						if not exclude_path(os.path.abspath(file)):
							files.append(file)
						else:
							exclude_files.append(file)

	local_songs = {}

	for file in files:
		song = mutagen.File(file, easy=True)

		key = create_song_key(song)

		local_songs[key] = file

	_print("Excluded {0} local songs".format(len(exclude_files)))
	_print("Loaded {0} local songs".format(len(local_songs)))

	return local_songs, exclude_files


def make_file_name(filename, audio):
	"""
	Create directory structure and file name based on user input.
	"""

	with open('temp.mp3', 'wb') as temp:
		temp.write(audio)

	tag = mutagen.File(temp.name, easy=True)

	if cli['output'] != os.getcwd():
		drive, path = os.path.splitdrive(cli['output'])
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

		dirname, __ = os.path.split(filename)

		if dirname:
			try:
				os.makedirs(dirname)
			except OSError:
				if not os.path.isdir(dirname):
					raise

	return filename


def main():
	do_auth()

	if cli['filter']:
		filters = [
			tuple(filter.split(':', 1)) for filter in cli['filter'] if filter.split(':', 1)[0] in FILTER_FIELDS
		]
	else:
		filters = None

	google_songs = get_google_songs(filters, cli['all'])
	local_songs, exclude_songs = get_local_songs()

	if cli['down']:
		_print("\nScanning for missing songs...")
		download_songs = compare_song_dicts(google_songs, local_songs)

		# Sort the list for sensible output.
		download_songs.sort(key=lambda song: (song['artist'], song['album'], song['track_number']))
		total = len(download_songs)

		if cli['dry-run']:
			_print("Found {0} songs to download\n".format(total))

			if download_songs:
				_print("Songs to download:\n")
				for song in download_songs:
					print("{0} by {1}".format(song['title'], song['artist']).encode('utf8'))
			else:
				_print("No songs to download")
		else:
			if download_songs:
				_print("Downloading {0} songs from Google Music\n".format(total))
				do_download(download_songs, total)
			else:
				_print("No songs to download")
	else:
		_print("\nScanning for missing songs...")

		upload_files = compare_song_dicts(local_songs, google_songs)

		# Sort lists for sensible output.
		upload_files.sort()
		exclude_songs.sort()

		total = len(upload_files)

		if cli['dry-run']:
			_print("Found {0} songs to upload\n".format(total))

			if upload_files:
				_print("Songs to upload:\n")
				for file in upload_files:
					print(file.encode('utf8'))
			else:
				_print("No songs to upload")

			if exclude_songs:
				_print("\nSongs to exclude:\n")
				for file in exclude_songs:
					print(file.encode('utf8'))
		else:
			if upload_files:
				_print("Uploading {0} songs to Google Music\n".format(total))
				do_upload(upload_files, total)
			else:
				_print("No songs to upload")

	# Log out mm session when finished.
	mm.logout()
	_print("\nAll done!")


if __name__ == '__main__':
	cli = docopt(__doc__)
	cli = dict((key.lstrip("-<>").rstrip(">"), value) for key, value in cli.items())  # Remove superfluous characters from cli keys

	if not cli['input']:
		cli['input'] = ['.']

	if not cli['output']:
		cli['output'] = os.getcwd()

	# Pre-compile regex for exclude option.
	excludes = re.compile("|".join(pattern.decode('utf8') for pattern in cli['exclude'])) if cli['exclude'] else None

	mm = Musicmanager(debug_logging=cli['log'])

	_print = print if not cli['quiet'] else lambda *a, **k: None

	try:
		main()
	except KeyboardInterrupt:
		mm.logout()
		print("\n\nExiting")

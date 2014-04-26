#!/usr/bin/env python

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py [options] [<input>...]

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.

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
"""

from __future__ import print_function, unicode_literals
from docopt import docopt
import mutagen
import os
import re
import sys

from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

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


def get_file_list():
	"""
	Create a list of supported files from user input(s).
	"""

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

	return files, exclude_files


def get_google_songs():
	"""
	Load song list from Google Music library.
	"""

	google_songs = {}

	try:
		songs = mm.get_all_songs()
	except:
		songs = mm.get_uploaded_songs()

	for song in songs:
		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag))
			key = '|'.join(tags)

		google_songs[key] = song

	return google_songs


def get_local_songs(files):
	"""
	Load song list from local system.
	"""

	local_songs = {}

	for file in files:
		song = mutagen.File(file, easy=True)

		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag[0]))
			key = '|'.join(tags)

		local_songs[key] = file

	return local_songs


def main():
	do_auth()

	_print("Loading local songs...")
	files, exclude_files = get_file_list()
	_print("Excluded {0} local songs".format(len(exclude_files)))
	local_songs = get_local_songs(files)
	_print("Loaded {0} local songs\n".format(len(local_songs)))

	_print("Loading Google Music songs...")
	google_songs = get_google_songs()
	_print("Loaded {0} Google Music songs\n".format(len(google_songs)))

	_print("Scanning for missing songs...")

	upload_files = []

	# Compare local and Google Music library lists.
	for key, song in local_songs.iteritems():
		if key not in google_songs:
			upload_files.append(song)

	# Sort lists for sensible output.
	upload_files.sort()
	exclude_files.sort()

	total = len(upload_files)

	if cli['dry-run']:
		_print("Found {0} songs".format(total))

		if upload_files:
			_print("\nSongs to upload:\n")
			for file in upload_files:
				print(file.encode('utf8'))

		if exclude_files:
			_print("\nSongs to exclude:\n")
			for file in exclude_files:
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

	# Pre-compile regex for exclude option.
	excludes = re.compile("|".join(pattern.decode('utf8') for pattern in cli['exclude'])) if cli['exclude'] else None

	mm = Musicmanager(debug_logging=cli['log'])

	_print = print if not cli['quiet'] else lambda *a, **k: None

	try:
		main()
	except KeyboardInterrupt:
		mm.logout()
		print("\n\nExiting")

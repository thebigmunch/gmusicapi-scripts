#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmupload.py (-h | --help)
  gmupload.py [-e PATTERN]... [options] [<input>]...

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
"""

from __future__ import print_function, unicode_literals
from docopt import docopt
import os
import re
import sys

from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

FORMATS = ('.mp3', '.flac', '.ogg', '.m4a')


def do_auth():
	"""
	Authenticate the mm client.
	"""

	oauth_file = os.path.join(os.path.dirname(OAUTH_FILEPATH), cli['cred'] + '.cred')

	try:
		if not mm.login(oauth_credentials=oauth_file, uploader_id=cli['uploader-id']):
			try:
				mm.perform_oauth(storage_filepath=oauth_file)
			except:
				print("\nUnable to login with specified oauth code.")

			mm.login(oauth_credentials=oauth_file, uploader_id=cli['uploader-id'])
	except (OSError, ValueError) as e:
		print(e.args[0])
		return False

	if not mm.is_authenticated():
		return False

	_print("Successfully logged in.\n")

	return True


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


def main():
	if not do_auth():
		_print("\nSorry, login failed.")
		sys.exit(0)

	_print("Loading local songs...")
	files, exclude_files = get_file_list()
	_print("Excluded {0} local songs".format(len(exclude_files)))

	# Sort list for sensible output.
	files.sort()
	exclude_files.sort()

	total = len(files)

	if cli['dry-run']:
		_print("Found {0} songs".format(total))

		if files:
			_print("\nSongs to upload:\n")
			for file in files:
				print(file.encode('utf8'))

		if exclude_files:
			_print("\nSongs to exclude:\n")
			for file in exclude_files:
				print(file.encode('utf8'))
	else:
		if files:
			_print("Uploading {0} songs to Google Music\n".format(total))
			do_upload(files, total)
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

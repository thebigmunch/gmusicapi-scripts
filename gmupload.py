#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net or by e-mail at munchicus+gmusicapi@gmail.com.
"""

from  __future__ import print_function, unicode_literals
import argparse
import os
import sys
from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

formats = ('.mp3', '.flac', '.ogg', '.m4a')

# Parse command line for arguments.
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-c', '--cred', default='oauth', help='Specify oauth credential file name to use/create\n(Default: "oauth" -> ' + OAUTH_FILEPATH + ')')
parser.add_argument('-l', '--log', action='store_true', default=False, help='Enable gmusicapi logging')
parser.add_argument('-m', '--match', action='store_true', default=False, help='Enable scan and match')
parser.add_argument('-d', '--dry-run', action='store_true', default=False, help='Output list of songs that would be uploaded')
parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Don\'t output status messages\n-l,--log will display gmusicapi warnings\n-d,--dry-run will display song list')
parser.add_argument('input', nargs='*', default='.', help='Files, directories, or glob patterns to upload\nDefaults to current directory if none given')
opts = parser.parse_args()

MM = Musicmanager(debug_logging=opts.log)

_print = print if not opts.quiet else lambda *a, **k: None


def do_auth():
	"""
	Authenticates the MM client.
	"""

	attempts = 0

	oauth_file = os.path.join(os.path.dirname(OAUTH_FILEPATH), opts.cred + '.cred')

	# Attempt to login. Perform oauth only when necessary.
	while attempts < 3:
		if MM.login(oauth_credentials=oauth_file):
			break
		MM.perform_oauth(storage_filepath=oauth_file)
		attempts += 1

	if not MM.is_authenticated():
		_print("Sorry, login failed.")
		return

	_print("Successfully logged in.\n")


def do_upload(files, total):
	"""
	Uploads the files and outputs the upload response with a counter.
	"""

	filenum = 0
	errors = {}
	pad = len(str(total))

	for file in files:
		filenum += 1

		try:
			uploaded, matched, not_uploaded = MM.upload(file, transcode_quality="320k", enable_matching=opts.match)
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


def get_file_list():
	"""
	Creates a list of supported files from user input(s).
	"""

	files = []

	for i in opts.input:
		i = i.decode('utf8')

		if os.path.isfile(i) and i.lower().endswith(formats):
			files.append(i)

		if os.path.isdir(i):
			for dirpath, dirnames, filenames in os.walk(i):
				for filename in filenames:
					if filename.lower().endswith(formats):
						file = os.path.join(dirpath, filename)
						files.append(file)

	return files


def main():
	do_auth()

	files = get_file_list()

	# Upload songs to your Google Music library.
	if files:
		# Sort the list for sensible output.
		files.sort()
		total = len(files)

		if opts.dry_run:
			_print("Found {0} songs\n".format(total))
			for file in files:
				print(file)
		else:
			_print("Uploading {0} songs to Google Music\n".format(total))
			do_upload(files, total)
	else:
		_print("No songs to upload")

	# Log out MM session when finished.
	MM.logout()
	_print("\nAll done!")


if __name__ == '__main__':
	main()

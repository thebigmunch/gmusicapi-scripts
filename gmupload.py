#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net or by e-mail at munchicus+gmusicapi@gmail.com.
"""

import argparse
import os
import sys
from gmusicapi import Musicmanager, CallFailure

formats = ('.mp3', '.flac', '.ogg', '.m4a')

# Parse command line for arguments.
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-l', '--log', action='store_true', default=False, help='Enable gmusicapi logging')
parser.add_argument('-m', '--match', action='store_true', default=False, help='Enable scan and match')
parser.add_argument('-d', '--dry-run', action='store_true', default=False, help='Output list of songs that would be uploaded')
parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Don\'t output status messages\n-l,--log will display gmusicapi warnings\n-d,--dry-run will display song list')
parser.add_argument('input', nargs='*', default='.', help='Files, directories, or glob patterns to upload\nDefaults to current directory if none given')
opts = parser.parse_args()

MM = Musicmanager(debug_logging=opts.log)


def do_output(msg, *args):
	"""
	Utility function for option-based output.
	"""

	if opts.quiet:
		pass
	elif args:
		print msg % args
	else:
		print msg


def do_auth():
	"""
	Authenticates the MM client.
	"""

	attempts = 0

	# Attempt to login. Perform oauth only when necessary.
	while attempts < 3:
		if MM.login():
			break
		MM.perform_oauth()
		attempts += 1

	if not MM.is_authenticated():
		do_output("Sorry, login failed.")
		return

	do_output("Successfully logged in.\n")


def do_upload(files, total):
	"""
	Uploads the files and outputs the upload response with a counter.
	"""

	filenum = 0
	errors = {}

	for file in files:
		filenum += 1

		try:
			uploaded, matched, not_uploaded = MM.upload(file, transcode_quality="320k", enable_matching=opts.match)
		except CallFailure as e:
			do_output("(%s/%s) Failed to upload  %s | %s", filenum, total, file, e)
			errors[file] = e
		else:
			if uploaded:
				do_output("(%s/%s) Successfully uploaded  %s", filenum, total, file)
			elif matched:
				do_output("(%s/%s) Successfully scanned and matched  %s", filenum, total, file)
			else:
				if "ALREADY_EXISTS" or "this song is already uploaded" in not_uploaded[file]:
					response = "ALREADY EXISTS"
				else:
					response = not_uploaded[file]
				do_output("(%s/%s) Failed to upload  %s | %s", filenum, total, file, response)

	if errors:
		do_output("\n\nThe following errors occurred:\n")
		for k, v in errors.iteritems():
			do_output("%s | %s", k, v)
		do_output("\nThese files may need to be synced again.\n")


def get_file_list():
	"""
	Creates a list of supported files from user input(s).
	"""

	files = []

	for i in opts.input:
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
			do_output("Found %s songs\n", total)
			for f in files:
				print "%s" % f
		else:
			do_output("Uploading %s songs to Google Music\n", total)
			do_upload(files, total)
	else:
		do_output("No songs to upload")

	# Log out MM session when finished.
	MM.logout()
	do_output("\nAll done!")


if __name__ == '__main__':
	main()

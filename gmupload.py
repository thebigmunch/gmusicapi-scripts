#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net.
"""

import os
import sys
from gmusicapi import Musicmanager, CallFailure

input = sys.argv[1:] if len(sys.argv) > 1 else '.'
formats = ('.mp3', '.flac', '.ogg', '.m4a', '.m4b', '.wma')

MM = Musicmanager(debug_logging=False)


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
		print "Sorry, login failed."
		return

	print "Successfully logged in.\n"


def do_upload(files):
	"""
	Uploads the files and outputs the upload response with a counter.
	"""

	# Sort the list for sensible output before uploading.
	files.sort()

	filenum = 0
	total = len(files)
	errors = {}

	print "Uploading %s songs to Google Music\n" % total

	for file in files:
		filenum += 1

		try:
			uploaded, matched, not_uploaded = MM.upload(file, transcode_quality="320k", enable_matching=False)
		except CallFailure as e:
			print "(%s/%s) Failed to upload  %s | %s" % (filenum, total, file, e)
			errors[file] = e
		else:
			if uploaded:
				print "(%s/%s) Successfully uploaded  %s" % (filenum, total, file)
			elif matched:
				print "(%s/%s) Successfully scanned and matched  %s" % (filenum, total, file)
			else:
				if "ALREADY_EXISTS" or "this song is already uploaded" in not_uploaded[file]:
					response = "ALREADY EXISTS"
				else:
					response = not_uploaded[file]
				print "(%s/%s) Failed to upload  %s | %s" % (filenum, total, file, response)

	if errors:
		print "\n\nThe following errors occurred:\n"
		for k, v in errors.iteritems():
			print "%s | %s" % (k, v)
		print "\nThese files may need to be synced again.\n"


def get_file_list():
	"""
	Creates a list of supported files from user input(s).
	"""

	files = []

	for i in input:
		if os.path.isfile(i) and i.endswith(formats):
			files.append(i)

		if os.path.isdir(i):
			for dirpath, dirnames, filenames in os.walk(i):
				for filename in filenames:
					if filename.endswith(formats):
						file = os.path.join(dirpath, filename)
						files.append(file)

	return files


def main():
	do_auth()

	files = get_file_list()

	do_upload(files)

	# Log out MM session when finished.
	MM.logout()
	print "All done!"


if __name__ == '__main__':
	main()

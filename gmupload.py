#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net.
"""

import os
import sys
from gmusicapi import Musicmanager


input = sys.argv[1:] if len(sys.argv) > 1 else '.'
formats = ('.mp3', '.flac', '.ogg', '.m4a', '.m4b', '.wma')

def auth():
	"""
	Creates an instance of the Musicmanager client and attempts to authenticate it.
	Returns the authenticated client if successful
	"""

	MM = Musicmanager(debug_logging=False)

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

	return MM

def do_upload(files):
	"""
	Uploads all supported files from files list.
	Outputs the upload response with a counter.
	"""

	# Sort the list for sensible output before uploading.
	files.sort()

	filenum = 0
	total = len(files)

	print "Uploading %s songs to Google Music\n" % total

	for file in files:
		filenum += 1

		uploaded, matched, not_uploaded = MM.upload(file, transcode_quality="320k", enable_matching=False)

		if uploaded:
			print "(%s/%s) " % (filenum, total), "Successfully uploaded ", file
		elif matched:
			print "(%s/%s) " % (filenum, total), "Successfully scanned and matched ", file
		else:
			if "ALREADY_EXISTS" or "this song is already uploaded" in not_uploaded[file]:
				response = "ALREADY EXISTS"
			else:
				response = not_uploaded[file]
			print "(%s/%s) " % (filenum, total), "Failed to upload ", file, " | ", response

def get_file_list():
	"""
	Creates a list of supported files from user input(s).
	"""

	files = []

	for i in input:
		if os.path.isfile(i) and i.endswith(formats):
			files.append(i)

		if os.path.isdir(i):
			files = files + [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(i) for filename in filenames if filename.endswith(formats)]

	return files

def main():
	do_upload(get_file_list())

	MM.logout()
	print "All done!"

if __name__ == '__main__':
	MM = auth()
	main()

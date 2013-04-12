#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
"""

import os
import sys
from gmusicapi import Musicmanager


## Do not edit below this line unless you know what you are doing ##
input = sys.argv[1:] if len(sys.argv) > 1 else '.'
formats = ('.mp3', '.flac', '.ogg', '.m4a', 'm4b', '.wma')

def auth():
	"""
	Creates an instance of the Musicmanager client and attempts to authenticate it.
	Returns the authenticated client if successful
	"""

	mm = Musicmanager(debug_logging=False)

	attempts = 0

	# Attempt to login. Perform oauth only when necessary.
	while attempts < 3:
		if mm.login():
			break
		mm.perform_oauth()
		attempts += 1

	if not mm.is_authenticated():
		print "Sorry, login failed."
		return

	print "Successfully logged in.\n"

	return mm

def upload(mm, files):
	"""
	Uploads all supported files from files list.
	Outputs the upload response with a counter.
	"""

	filenum = 0
	total = len(files)
	for file in files:
		filenum += 1

		uploaded, matched, not_uploaded = mm.upload(file, transcode_quality="320k", enable_matching=False)

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

	return mm

def main():
	"""
	Creates a list of supported files to upload from user inputs.
	"""

	mm = auth()

	files = []
	for i in input:
		if os.path.isfile(i) and i.endswith(formats):
			files.append(i)

		if os.path.isdir(i):
			files = files + [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(i) for filename in filenames if filename.endswith(formats)]

	# Sort the list before sending to upload for sensible output.
	files.sort()
	upload(mm, files)

	mm.logout()
	print "All done!"

if __name__ == '__main__':
	main()

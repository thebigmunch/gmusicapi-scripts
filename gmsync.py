#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net.
"""

import mutagen
import os
import re
import sys
from gmusicapi import Musicmanager, CallFailure

input = sys.argv[1:] if len(sys.argv) > 1 else '.'
formats = ('.mp3', '.flac', '.ogg', '.m4a', '.m4b')

# Pre-compile regex for clean_tag function.
track_slash = re.compile('\/\s*\d+')
lead_zeros = re.compile('^0+([0-9]+)')
track_dots = re.compile('^\d+\.+')
non_word = re.compile('[^\w\s]')
spaces = re.compile('\s+')
lead_space = re.compile('^\s+')
trail_space = re.compile('\s+$')
the = re.compile('^the\s+', re.I)

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


def clean_tag(tag):
	"""
	Cleans up metadata tags to improve matching accuracy.
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


def filter_tags(song):
	"""
	Filters out a missing artist, album, title, or track tag to improve matching accuracy.
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


def get_google_songs():
	"""
	Load song list from Google Music library.
	"""

	print "Loading Google Music songs..."

	google_songs = {}

	for song in MM.get_all_songs():
		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag))
			key = '|'.join(tags)

		google_songs[key] = song

	print "Loaded %s Google Music songs\n" % len(google_songs)

	return google_songs


def get_local_songs():
	"""
	Load song list from local system.
	"""

	print "Loading local songs..."

	local_songs = {}

	for file in get_file_list():
		song = mutagen.File(file, easy=True)

		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag[0]))
			key = '|'.join(tags)

		local_songs[key] = file

	print "Loaded %s local songs\n" % len(local_songs)

	return local_songs


def main():
	do_auth()

	local_songs = get_local_songs()
	google_songs = get_google_songs()

	print "Scanning for missing songs to upload..."

	files = []

	# Compare local and Google Music library lists.
	for key, song in local_songs.iteritems():
		if key not in google_songs:
			files.append(song)

	# Upload any local songs not in your Google Music library.
	if files:
		do_upload(files)
	else:
		print "No songs to upload\n"

	# Log out MM session when finished.
	MM.logout()
	print "All done!"


if __name__ == '__main__':
	main()

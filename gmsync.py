#!/usr/bin/env python

"""
An upload script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
You may contact the author (thebigmunch) in #gmusicapi on irc.freenode.net or by e-mail at munchicus+gmusicapi@gmail.com.
"""

import argparse
import mutagen
import os
import re
import sys
from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

formats = ('.mp3', '.flac', '.ogg', '.m4a')

# Pre-compile regex for clean_tag function.
track_slash = re.compile('\/\s*\d+')
lead_zeros = re.compile('^0+([0-9]+)')
track_dots = re.compile('^\d+\.+')
non_word = re.compile('[^\w\s]')
spaces = re.compile('\s+')
lead_space = re.compile('^\s+')
trail_space = re.compile('\s+$')
the = re.compile('^the\s+', re.I)

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

	oauth_file = os.path.join(os.path.dirname(OAUTH_FILEPATH), opts.cred + '.cred')

	# Attempt to login. Perform oauth only when necessary.
	while attempts < 3:
		if MM.login(oauth_credentials=oauth_file):
			break
		MM.perform_oauth(storage_filepath=oauth_file)
		attempts += 1

	if not MM.is_authenticated():
		do_output("Sorry, login failed.")
		return

	do_output("Successfully logged in.\n")


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
				check_strings = ["ALREADY_EXISTS", "this song is already uploaded"]
				if any(cs in not_uploaded[file] for cs in check_strings):
					response = "ALREADY EXISTS"
				else:
					response = not_uploaded[file]
				do_output("(%s/%s) Failed to upload  %s | %s", filenum, total, file, response)

	if errors:
		do_output("\n\nThe following errors occurred:\n")
		for k, v in errors.iteritems():
			do_output("%s | %s", k, v)
		do_output("\nThese files may need to be synced again.\n")


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


def get_google_songs():
	"""
	Load song list from Google Music library.
	"""

	do_output("Loading Google Music songs...")

	google_songs = {}

	for song in MM.get_all_songs():
		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag))
			key = '|'.join(tags)

		google_songs[key] = song

	do_output("Loaded %s Google Music songs\n", len(google_songs))

	return google_songs


def get_local_songs():
	"""
	Load song list from local system.
	"""

	do_output("Loading local songs...")

	local_songs = {}

	for file in get_file_list():
		song = mutagen.File(file, easy=True)

		tags = []

		for tag in filter_tags(song):
			tags.append(clean_tag(tag[0]))
			key = '|'.join(tags)

		local_songs[key] = file

	do_output("Loaded %s local songs\n", len(local_songs))

	return local_songs


def main():
	do_auth()

	local_songs = get_local_songs()
	google_songs = get_google_songs()

	do_output("Scanning for missing songs...")

	files = []

	# Compare local and Google Music library lists.
	for key, song in local_songs.iteritems():
		if key not in google_songs:
			files.append(song)

	# Upload any local songs not in your Google Music library.
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

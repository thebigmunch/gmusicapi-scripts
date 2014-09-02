from __future__ import print_function, unicode_literals

import logging
import os
import re
import shutil
import sys
import tempfile

import mutagen
from gmusicapi import CallFailure
from gmusicapi.clients import Musicmanager, OAUTH_FILEPATH

from utils import safe_print

SUPPORTED_FORMATS = ('.mp3', '.flac', '.ogg', '.m4a')

CHARACTER_REPLACEMENTS = {
	'\\': '-', '/': ',', ':': '-', '*': 'x', '<': '[',
	'>': ']', '|': '!', '?': '', '"': "''"
}

TEMPLATE_PATTERNS = {
	'%artist%': 'artist', '%title%': 'title', '%track%': 'tracknumber',
	'%track2%': 'tracknumber', '%album%': 'album', '%date%': 'date',
	'%genre%': 'genre', '%albumartist%': 'albumartist', '%disc%': 'discnumber'
}


def _mutagen_fields_to_single_value(file):
	"""Replace field list values in mutagen tags with the first list value."""

	return {k: v[0] for k, v in mutagen.File(file, easy=True).iteritems()}


def compare_song_collections(src_songs, dest_songs):
	"""Compare two song collections.

	Returns a list of songs from source missing in destination.
	"""

	missing_songs = []
	src_songs_keyed = {}
	dest_songs_keyed = {}

	for src_song in src_songs:
		if isinstance(src_song, dict):
			src_key = create_song_key(src_song)
		else:
			src_key = create_song_key(_mutagen_fields_to_single_value(src_song))

		src_songs_keyed[src_key] = src_song

	for dest_song in dest_songs:
		if isinstance(dest_song, dict):
			dest_key = create_song_key(dest_song)
		else:
			dest_key = create_song_key(_mutagen_fields_to_single_value(dest_song))

		dest_songs_keyed[dest_key] = dest_song

	for src_key, src_song in src_songs_keyed.iteritems():
		if src_key not in dest_songs_keyed:
			missing_songs.append(src_song)

	return missing_songs


def create_song_key(song):
	"""Create dict key for song based on metadata."""

	metadata = []

	# Replace track numbers with 0 if no tag exists.
	if song.get('id'):
		if not song.get('track_number'):
			song['track_number'] = '0'
	else:
		if not song.get('tracknumber'):
			song['tracknumber'] = '0'

	for field in filter_fields(song):
		metadata.append(normalize_metadata(song[field]))

	key = '|'.join(metadata)

	return key


def exclude_path(path, exclude_patterns):
	"""Exclude file paths based on regex patterns."""

	if exclude_patterns and re.search(exclude_patterns, path):
		return True
	else:
		return False


def filter_fields(song):
	"""Filter missing artist, album, title, or track fields to improve match accuracy."""

	# Need both tracknumber (mutagen) and track_number (Google Music) here.
	return [field for field in ['artist', 'album', 'title', 'tracknumber', 'track_number'] if field in song and song[field]]


# Shamelessly taken from gmusicapi itself.
def _get_valid_filter_fields():
	shared_fields = ['artist', 'title', 'album']
	diff_fields = {'albumartist': 'album_artist'}

	return dict(dict((shared, shared) for shared in shared_fields).items() + diff_fields.items())


def _match_filters(song, filters, filter_all):
	"""Match a song metadata dict against a set of metadata filters."""

	if filter_all:
		if not all(field in song and re.search(value, song[field], re.I) for field, value in filters):
			return False
	else:
		if not any(field in song and re.search(value, song[field], re.I) for field, value in filters):
			return False

	return True


def match_filters_google(songs, filters, filter_all):
	"""Match a Google Music song against a set of metadata filters."""

	match_songs = []
	filter_songs = []

	if filters:
		split_filters = []

		for filter in filters:
			filter_field, filter_value = filter.split(':', 1)
			valid_fields = _get_valid_filter_fields().items()

			for mutagen_field, google_field in valid_fields:
				if filter_field == mutagen_field or filter_field == google_field:
					split_filters.append((google_field, filter_value))

		for song in songs:
			if _match_filters(song, split_filters, filter_all):
				match_songs.append(song)
			else:
				filter_songs.append(song)
	else:
		match_songs += songs

	return match_songs, filter_songs


def match_filters_local(files, filters, filter_all):
	"""Match a local file against a set of metadata filters."""

	match_songs = []
	filter_songs = []

	if filters:
		split_filters = []

		for filter in filters:
			filter_field, filter_value = filter.split(':', 1)
			valid_fields = _get_valid_filter_fields().items()

			for mutagen_field, google_field in valid_fields:
				if filter_field == mutagen_field or filter_field == google_field:
					split_filters.append((mutagen_field, filter_value))

		for file in files:
			song = _mutagen_fields_to_single_value(file)

			if _match_filters(song, split_filters, filter_all):
				match_songs.append(file)
			else:
				filter_songs.append(file)
	else:
		match_songs += files

	return match_songs, filter_songs


def normalize_metadata(metadata):
	"""Normalize metadata to improve match accuracy."""

	metadata = unicode(metadata)  # Convert metadata to unicode.
	metadata = metadata.lower()  # Convert to lower case.

	metadata = re.sub('\/\s*\d+', '', metadata)  # Remove "/<totaltracks>" from track number.
	metadata = re.sub('^0+([0-9]+)', r'\1', metadata)  # Remove leading zero(s) from track number.
	metadata = re.sub('^\d+\.+', '', metadata)  # Remove dots from track number.
	metadata = re.sub('[^\w\s]', '', metadata)  # Remove any non-words.
	metadata = re.sub('\s+', ' ', metadata)  # Reduce multiple spaces to a single space.
	metadata = re.sub('^\s+', '', metadata)  # Remove leading space.
	metadata = re.sub('\s+$', '', metadata)  # Remove trailing space.
	metadata = re.sub('^the\s+', '', metadata, re.I)  # Remove leading "the".

	return metadata


def template_to_file_name(template, suggested_filename, metadata):
	"""Create directory structure and file name based on metadata template."""

	drive, path = os.path.splitdrive(template)
	parts = []

	while True:
		newpath, tail = os.path.split(path)

		if newpath == path:
			break

		parts.append(tail)
		path = newpath

	parts.reverse()

	for i, part in enumerate(parts):
		if "%suggested%" in part:
			parts[i] = parts[i].replace("%suggested%", suggested_filename.replace('.mp3', ''))

		for key in TEMPLATE_PATTERNS:
			if key in part and TEMPLATE_PATTERNS[key] in metadata:
				if key == '%track2%':
					metadata['tracknumber'] = metadata['tracknumber'][0].zfill(2)
					try:
						metadata.save()
					except:
						pass

				parts[i] = parts[i].replace(key, metadata[TEMPLATE_PATTERNS[key]][0])

		for char in CHARACTER_REPLACEMENTS:
			if char in parts[i]:
				parts[i] = parts[i].replace(char, CHARACTER_REPLACEMENTS[char])

	if drive:
		filename = os.path.join(drive, os.sep, *parts) + '.mp3'
	else:
		filename = os.path.join(*parts) + '.mp3'

	dirname, __ = os.path.split(filename)

	if dirname:
		try:
			os.makedirs(dirname)
		except OSError:
			if not os.path.isdir(dirname):
				raise

	return filename


class _Base(object):
	def get_local_songs(self, paths, formats=SUPPORTED_FORMATS, exclude_patterns=None, filters=None, filter_all=False):
		"""Load songs from local file paths."""

		if isinstance(paths, basestring):
			paths = [paths]

		assert isinstance(paths, list)

		self.print_("Loading local songs...")

		include_songs = []
		exclude_songs = []

		for path in paths:
			if not isinstance(path, unicode):
				path = path.decode('utf8')

			if os.path.isdir(path):
				for dirpath, dirnames, filenames in os.walk(path):
					for filename in filenames:
						if filename.lower().endswith(formats):
							filepath = os.path.join(dirpath, filename)

							if exclude_path(filepath, exclude_patterns):
								exclude_songs.append(filepath)
							else:
								include_songs.append(filepath)

			elif os.path.isfile(path) and path.lower().endswith(formats):
				if exclude_path(path, exclude_patterns):
					exclude_songs.append(path)
				else:
					include_songs.append(path)

		local_songs, filter_songs = match_filters_local(include_songs, filters, filter_all)

		self.print_("Excluded {0} local songs.".format(len(exclude_songs)))
		self.print_("Filtered {0} local songs.".format(len(filter_songs)))
		self.print_("Loaded {0} local songs.\n".format(len(local_songs)))

		return local_songs, exclude_songs


class MusicManagerWrapper(_Base):
	def __init__(self, log=False, quiet=False):
		self.api = Musicmanager(debug_logging=log)
		self.api.logger.addHandler(logging.NullHandler())

		self.print_ = safe_print if not quiet else lambda *args, **kwargs: None

	def login(self, oauth_file="oauth", uploader_id=None):
		"""Authenticate the gmusicapi Musicmanager instance."""

		oauth_cred = os.path.join(os.path.dirname(OAUTH_FILEPATH), oauth_file + '.cred')

		try:
			if not self.api.login(oauth_credentials=oauth_cred, uploader_id=uploader_id):
				try:
					self.api.perform_oauth(storage_filepath=oauth_cred)
				except:
					self.print_("\nUnable to login with specified oauth code.")

				self.api.login(oauth_credentials=oauth_cred, uploader_id=uploader_id)
		except (OSError, ValueError) as e:
			self.print_(e.args[0])
			return False

		if not self.api.is_authenticated():
			self.print_("Sorry, login failed.")

			return False

		self.print_("Successfully logged in.\n")

		return True

	def logout(self, revoke_oauth=False):
		"""Log out the gmusicapi Musicmanager instance."""

		self.api.logout(revoke_oauth=revoke_oauth)

	def get_google_songs(self, filters=None, filter_all=False):
		"""Load song list from Google Music library."""

		self.print_("Loading Google Music songs...")

		google_songs = []
		filter_songs = []

		songs = self.api.get_uploaded_songs()

		google_songs, filter_songs = match_filters_google(songs, filters, filter_all)

		self.print_("Filtered {0} Google Music songs".format(len(filter_songs)))
		self.print_("Loaded {0} Google Music songs\n".format(len(google_songs)))

		return google_songs

	def download(self, songs, template):
		"""Download songs from Google Music."""

		if isinstance(songs, basestring):
			songs = [songs]

		assert isinstance(songs, list)

		songnum = 0
		total = len(songs)
		errors = {}
		pad = len(str(total))

		for song in songs:
			songnum += 1

			try:
				self.print_("Downloading  {0} by {1}".format(song['title'], song['artist']), end="\r")
				sys.stdout.flush()
				suggested_filename, audio = self.api.download_song(song['id'])
			except CallFailure as e:
				self.print_("({num:>{pad}}/{total}) Failed to download  {file} | {error}".format(num=songnum, total=total, file=suggested_filename, error=e, pad=pad))
				errors[suggested_filename] = e
			else:
				with tempfile.NamedTemporaryFile(delete=False) as temp:
					temp.write(audio)

				metadata = mutagen.File(temp.name, easy=True)

				if template != os.getcwd():
					filename = template_to_file_name(template, suggested_filename, metadata)
				else:
					filename = suggested_filename

				shutil.move(temp.name, filename)

				self.print_("({num:>{pad}}/{total}) Successfully downloaded  {file}".format(num=songnum, total=total, file=filename, pad=pad))

		if errors:
			self.print_("\n\nThe following errors occurred:\n")
			for filename, e in errors.iteritems():
				self.print_("{file} | {error}".format(file=filename, error=e))
			self.print_("\nThese files may need to be synced again.\n")

	def upload(self, files, enable_matching=False):
		"""Upload files to Google Music."""

		if isinstance(files, basestring):
			files = [files]

		assert isinstance(files, list)

		filenum = 0
		total = len(files)
		errors = {}
		pad = len(str(total))

		for file in files:
			filenum += 1

			try:
				self.print_("Uploading  {0}".format(file), end="\r")
				sys.stdout.flush()
				uploaded, matched, not_uploaded = self.api.upload(file, transcode_quality="320k", enable_matching=enable_matching)
			except CallFailure as e:
				self.print_("({num:>{pad}}/{total}) Failed to upload  {file} | {error}".format(num=filenum, total=total, file=file, error=e, pad=pad))
				errors[file] = e
			else:
				if uploaded:
					self.print_("({num:>{pad}}/{total}) Successfully uploaded  {file}".format(num=filenum, total=total, file=file, pad=pad))
				elif matched:
					self.print_("({num:>{pad}}/{total}) Successfully scanned and matched  {file}".format(num=filenum, total=total, file=file, pad=pad))
				else:
					check_strings = ["ALREADY_EXISTS", "this song is already uploaded"]
					if any(check_string in not_uploaded[file] for check_string in check_strings):
						response = "ALREADY EXISTS"
					else:
						response = not_uploaded[file]
					self.print_("({num:>{pad}}/{total}) Failed to upload  {file} | {response}".format(num=filenum, total=total, file=file, response=response, pad=pad))

		if errors:
			self.print_("\n\nThe following errors occurred:\n")
			for file, e in errors.iteritems():
				self.print_("{file} | {error}".format(file=file, error=e))
			self.print_("\nThese files may need to be synced again.\n")

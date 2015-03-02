#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py up [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...
  gmsync.py down [-f FILTER]... [-F FILTER]... [options] [<output>]
  gmsync.py [-e PATTERN]... [-f FILTER]... [-F FILTER]... [options] [<input>]...

Commands:
  up                             Sync local songs to Google Music. Default behavior.
  down                           Sync Google Music songs to local computer.

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.
  output                         Output file or directory name which can include a template pattern.
                                 Defaults to name suggested by Google Music in your current directory.

Options:
  -h, --help                            Display help message.
  -c CRED, --cred CRED                  Specify oauth credential file name to use/create. [Default: oauth]
  -U ID --uploader-id ID                A unique id given as a MAC address (e.g. '00:11:22:33:AA:BB').
                                        This should only be provided when the default does not work.
  -l, --log                             Enable gmusicapi logging.
  -m, --match                           Enable scan and match.
  -d, --dry-run                         Output list of songs that would be uploaded.
  -q, --quiet                           Don't output status messages.
                                        With -l,--log will display gmusicapi warnings.
                                        With -d,--dry-run will display song list.
  -e PATTERN, --exclude PATTERN         Exclude file paths matching pattern.
                                        This option can be set multiple times.
  -f FILTER, --include-filter FILTER    Include Google songs (download) or local songs (upload)
                                        by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -F FILTER, --exclude-filter FILTER    Exclude Google songs (download) or local songs (upload)
                                        by field:pattern filter (e.g. "artist:Muse").
                                        Songs can match any filter criteria.
                                        This option can be set multiple times.
  -a, --include-all                     Songs must match all include filter criteria to be included.
  -A, --exclude-all                     Songs must match all exclude filter criteria to be excluded.

Patterns can be any valid Python regex patterns.
"""

from __future__ import unicode_literals

import logging
import os

from docopt import docopt

from gmusicapi_wrapper import MusicManagerWrapper
from gmusicapi_wrapper.utils import compare_song_collections, template_to_file_name

QUIET = 25
logging.addLevelName(25, "QUIET")

logger = logging.getLogger('gmusicapi_wrapper')
sh = logging.StreamHandler()
logger.addHandler(sh)


def template_to_base_path(template, google_songs):
	"""Get base output path for a list of songs for download."""

	song_paths = []

	if template == os.getcwd():
		local_path = [template]
	else:
		for song in google_songs:
			song_paths.append(template_to_file_name(template, song))

		common_base_path = os.path.commonprefix(song_paths)
		local_path = [common_base_path]

	return local_path


def main():
	cli = dict((key.lstrip("-<").rstrip(">"), value) for key, value in docopt(__doc__).items())

	if cli['quiet']:
		logger.setLevel(QUIET)
	else:
		logger.setLevel(logging.INFO)

	if not cli['input']:
		cli['input'] = [os.getcwd()]

	if not cli['output']:
		cli['output'] = os.getcwd()

	include_filters = [tuple(filt.split(':', 1)) for filt in cli['include-filter']]
	exclude_filters = [tuple(filt.split(':', 1)) for filt in cli['exclude-filter']]

	filepath_exclude_patterns = "|".join(pattern.decode('utf8') for pattern in cli['exclude']) if cli['exclude'] else None

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	if cli['down']:
		matched_google_songs, _ = mmw.get_google_songs(include_filters, exclude_filters, cli['include-all'], cli['exclude-all'])

		logger.info("")

		cli['input'] = template_to_base_path(cli['output'], matched_google_songs)

		matched_local_songs, _, _ = mmw.get_local_songs(cli['input'], filepath_exclude_patterns=filepath_exclude_patterns)

		logger.info("\nScanning for missing songs...")
		songs_to_download = compare_song_collections(matched_google_songs, matched_local_songs)

		songs_to_download.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

		if cli['dry-run']:
			logger.info("\nFound {0} song(s) to download".format(len(songs_to_download)))

			if songs_to_download:
				logger.info("\nSongs to download:\n")

				for song in songs_to_download:
					title = song.get('title', "<empty>")
					artist = song.get('artist', "<empty>")
					album = song.get('album', "<empty>")
					song_id = song['id']

					logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
			else:
				logger.info("\nNo songs to download")
		else:
			if songs_to_download:
				logger.info("\nDownloading {0} song(s) from Google Music\n".format(len(songs_to_download)))
				mmw.download(songs_to_download, cli['output'])
			else:
				logger.info("\nNo songs to download")
	else:
		matched_google_songs, _ = mmw.get_google_songs()

		logger.info("")

		matched_local_songs, _, songs_to_exclude = mmw.get_local_songs(
			cli['input'], include_filters, exclude_filters, cli['include-all'], cli['exclude-all'], filepath_exclude_patterns
		)

		logger.info("\nScanning for missing songs...")

		songs_to_upload = compare_song_collections(matched_local_songs, matched_google_songs)

		# Sort lists for sensible output.
		songs_to_upload.sort()
		songs_to_exclude.sort()

		if cli['dry-run']:
			logger.info("\nFound {0} song(s) to upload".format(len(songs_to_upload)))

			if songs_to_upload:
				logger.info("\nSongs to upload:\n")

				for song in songs_to_upload:
					logger.log(QUIET, song)
			else:
				logger.info("\nNo songs to upload")

			if songs_to_exclude:
				logger.info("\nSongs to exclude:\n")

				for song in songs_to_exclude:
					logger.log(QUIET, song)
			else:
				logger.info("\nNo songs to exclude")
		else:
			if songs_to_upload:
				logger.info("\nUploading {0} song(s) to Google Music\n".format(len(songs_to_upload)))

				mmw.upload(songs_to_upload, enable_matching=cli['match'])
			else:
				logger.info("\nNo songs to upload")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

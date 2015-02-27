#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A sync script for Google Music using https://github.com/simon-weber/Unofficial-Google-Music-API.
More information at https://github.com/thebigmunch/gmusicapi-scripts.

Usage:
  gmsync.py (-h | --help)
  gmsync.py up [-e PATTERN]... [-f FILTER]... [options] [<input>]...
  gmsync.py down [-f FILTER]... [options] [<output>]
  gmsync.py [-e PATTERN]... [-f FILTER]... [options] [<input>]...

Commands:
  up                             Sync local songs to Google Music. Default behavior.
  down                           Sync Google Music songs to local computer.

Arguments:
  input                          Files, directories, or glob patterns to upload.
                                 Defaults to current directory.
  output                         Output file or directory name which can include a template pattern.
                                 Defaults to name suggested by Google Music in your current directory.

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
                                 This option can be set multiple times.
  -f FILTER, --filter FILTER     Filter Google songs (download) or local songs (upload) by field:pattern pair (e.g. "artist:Muse").
                                 Songs can match any filter criteria.
                                 This option can be set multiple times.
  -a, --all                      Songs must match all filter criteria.
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

	for song in google_songs:
		song_paths.append(template_to_file_name(template, song))

	common_path = os.path.commonprefix(song_paths)
	local_path = [common_path] if common_path else [os.getcwd()]

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

	filters = [tuple(filt.split(':', 1)) for filt in cli['filter']]

	# Pre-compile regex for exclude option.
	excludes = "|".join(pattern.decode('utf8') for pattern in cli['exclude']) if cli['exclude'] else None

	mmw = MusicManagerWrapper(log=cli['log'])
	mmw.login(oauth_filename=cli['cred'], uploader_id=cli['uploader-id'])

	if cli['down']:
		google_songs, _ = mmw.get_google_songs(filters=filters, filter_all=cli['all'])

		cli['input'] = template_to_base_path(cli['output'], google_songs)

		local_songs, _, _ = mmw.get_local_songs(cli['input'], exclude_patterns=excludes)
		print(cli['input'])

		logger.info("Scanning for missing songs...")
		download_songs = compare_song_collections(google_songs, local_songs)

		download_songs.sort(key=lambda song: (song.get('artist'), song.get('album'), song.get('trackNumber')))

		if cli['dry-run']:
			logger.info("Found {0} song(s) to download".format(len(download_songs)))

			if download_songs:
				logger.info("\nSongs to download:\n")

				for song in download_songs:
					title = song.get('title', "<empty>")
					artist = song.get('artist', "<empty>")
					album = song.get('album', "<empty>")
					song_id = song['id']

					logger.log(QUIET, "{0} -- {1} -- {2} ({3})".format(title, artist, album, song_id))
			else:
				logger.info("\nNo songs to download")
		else:
			if download_songs:
				logger.info("Downloading {0} song(s) from Google Music\n".format(len(download_songs)))
				mmw.download(download_songs, cli['output'])
			else:
				logger.info("\nNo songs to download")
	else:
		google_songs, _ = mmw.get_google_songs()
		local_songs, _, exclude_songs = mmw.get_local_songs(cli['input'], filters=filters, filter_all=cli['all'], exclude_patterns=excludes)

		logger.info("Scanning for missing songs...")

		upload_songs = compare_song_collections(local_songs, google_songs)

		# Sort lists for sensible output.
		upload_songs.sort()
		exclude_songs.sort()

		if cli['dry-run']:
			logger.info("Found {0} song(s) to upload".format(len(upload_songs)))

			if upload_songs:
				logger.info("\nSongs to upload:\n")

				for song in upload_songs:
					logger.log(QUIET, song)
			else:
				logger.info("\nNo songs to upload")

			if exclude_songs:
				logger.info("\nSongs to exclude:\n")

				for song in exclude_songs:
					logger.log(QUIET, song)
			else:
				logger.info("\nNo songs to exclude")
		else:
			if upload_songs:
				logger.info("Uploading {0} song(s) to Google Music\n".format(len(upload_songs)))

				mmw.upload(upload_songs, enable_matching=cli['match'])
			else:
				logger.info("No songs to upload")

	mmw.logout()
	logger.info("\nAll done!")


if __name__ == '__main__':
	main()

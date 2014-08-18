#!/usr/bin/env

from __future__ import print_function, unicode_literals

import sys


def safe_print(msg, *args, **kwargs):
	"""Safely print strings containing unicode characters."""

	try:
		print(msg, *args, **kwargs)
	except:
		print(msg.encode(sys.stdout.encoding or 'utf8', errors='replace'), *args, **kwargs)

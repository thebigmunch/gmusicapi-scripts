#!/usr/bin/env

from __future__ import print_function, unicode_literals


def safe_print(msg, *args, **kwargs):
	"""Safely print strings containing unicode characters."""

	try:
		print(msg, *args, **kwargs)
	except UnicodeEncodeError:
		print(msg.encode('utf8'), *args, **kwargs)

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""gmdownload script wrapper for backward compatibility with old installations."""

import sys

from gmusicapi_scripts.gmdownload import main

sys.exit(main())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""gmupload script wrapper for backward compatibility with old installations."""

import sys

from gmusicapi_scripts.gmupload import main

sys.exit(main())

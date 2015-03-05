#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""gmdelete script wrapper for backward compatibility with old installations."""

import sys

from gmusicapi_scripts.gmdelete import main

sys.exit(main())

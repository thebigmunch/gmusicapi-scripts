#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""gmsearch script wrapper for backward compatibility with old installations."""

import sys

from gmusicapi_scripts.gmsearch import main

sys.exit(main())

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""gmsync script wrapper for backward compatibility with old installations."""

import sys

from gmusicapi_scripts.gmsync import main

sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

# __all__ = [
#     "io",
#     "compute",
#     "window",
# ]

import os


# use github release tag as the version number
try:
    __version__ = os.environ["GITHUB_REF_NAME"]
except:
    __version__ = "0.1.2"
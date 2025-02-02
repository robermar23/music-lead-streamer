# Copyright (c) 2024 JP Hutchins
# SPDX-License-Identifier: Apache-2.0

"""Support for `python -m jpsapp`."""

import sys
from music_led_streamer.main import app, config

#print (str(len(sys.argv)))

if len(sys.argv) == 1 or len(sys.argv) == 3:
    config()
else:
    app()
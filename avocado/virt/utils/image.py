# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright (C) 2008-2014 Red Hat Inc

"""
Utility functions for image files.
"""
import os


def is_ppm(filename):
    """
    Verify whether filename is a PPM file.

    :param filename: Path of the file being verified.
    :return: True if filename is a valid PPM image file. This function
             reads only the first few bytes of the file so it should be rather
             fast.
    """
    try:
        size = os.path.getsize(filename)
        with open(filename, "rb") as fin:
            assert fin.readline().strip() == "P6"
            width, height = map(int, fin.readline().split())
            assert width > 0 and height > 0
            assert fin.readline().strip() == "255"
            size_read = fin.tell()
            assert size - size_read == width * height * 3
        return True
    except AssertionError:
        return False

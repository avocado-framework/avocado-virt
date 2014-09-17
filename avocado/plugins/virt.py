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
# Copyright: Red Hat Inc. 2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

"""
Virtualization testing plugin.
"""

from avocado.plugins import plugin
from avocado.virt import defaults


class VirtOptions(plugin.Plugin):

    """
    Add virtualization testing related options.
    """

    name = 'virt'
    enabled = True

    def configure(self, parser):
        self.parser = parser
        self.parser.runner.add_argument(
            '--qemu-bin', type=str,
            dest='qemu_bin',
            help=('Path to a custom qemu binary to be tested. Default path: %s'
                  % defaults.qemu_bin))
        self.parser.runner.add_argument(
            '--qemu-dst-bin', type=str,
            dest='qemu_dst_bin',
            help=('Path to a destination qemu binary to be tested. Used as '
                  'incoming qemu in migration tests. Default path: %s'
                  % defaults.qemu_dst))
        self.parser.runner.add_argument(
            '--guest-image-path', type=str,
            dest='guest_image_path',
            help=('Path to a guest image to be used in tests. Default path: %s'
                  % defaults.guest_image_path))

        self.configured = True

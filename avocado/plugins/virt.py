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

import os
import logging

from avocado.core import output
from avocado.utils import process
from avocado.plugins import plugin
from avocado.virt import defaults


class VirtOptions(plugin.Plugin):

    """
    Add virtualization testing related options.
    """

    name = 'virt'
    enabled = True
    app_logger = logging.getLogger('avocado.app')

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
        self.parser.runner.add_argument(
            '--disable-restore-image-test', action='store_true',
            default=defaults.disable_restore_image_test,
            dest='disable_restore_image_test',
            help=('Do not restore the guest image before individual tests '
                  'start. Default: %s' % defaults.disable_restore_image_test))
        self.parser.runner.add_argument(
            '--disable-restore-image-job', action='store_true',
            default=defaults.disable_restore_image_job,
            dest='disable_restore_image_job',
            help=('Do not restore the guest image before a test job '
                  'start. Default: %s' % defaults.disable_restore_image_job))

        self.configured = True

    def activate(self, app_args):
        if app_args.disable_restore_image_test:
            if not app_args.disable_restore_image_job:
                if app_args.guest_image_path:
                    drive_file = app_args.guest_image_path
                else:
                    drive_file = defaults.guest_image_path
                compressed_drive_file = drive_file + '.7z'
                if os.path.isfile(compressed_drive_file):
                    # Hack until we work out a better way to signal an output
                    # Plugin wants the stdout exclusively.
                    if not (app_args.xunit_output == '-' or
                            app_args.json_output == '-'):
                        msg = ("Plugin setup (Restoring guest image backup). "
                               "Please wait...")
                        self.app_logger.info(msg)
                    cwd = os.getcwd()
                    os.chdir(os.path.dirname(compressed_drive_file))
                    process.run('7za -y e %s' %
                                os.path.basename(compressed_drive_file))
                    os.chdir(cwd)

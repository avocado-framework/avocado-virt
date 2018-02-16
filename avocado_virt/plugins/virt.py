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

import logging
import os
from argparse import FileType

from avocado.utils import process

# Avocado's plugin interface module has changed location. Let's keep
# compatibility with old for at, least, a new LTS release
try:
    from avocado.core.plugin_interfaces import CLI
except ImportError:
    from avocado.plugins.base import CLI

from .. import defaults

try:
    from ..utils import video
    # We are not going to need this module for now
    del video
    VIDEO_ENCODING_SUPPORT = True
except ImportError:
    VIDEO_ENCODING_SUPPORT = False


LOG = logging.getLogger("avocado.app")


class VirtRun(CLI):

    """
    Add virtualization testing related options.
    """

    name = 'virt'
    description = "Virtualization testing options to 'run' subcommand"

    def configure(self, parser):
        run_subcommand_parser = parser.subcommands.choices.get('run', None)
        if run_subcommand_parser is None:
            return

        virt_parser = run_subcommand_parser.add_argument_group('virtualization '
                                                               'testing arguments')
        virt_parser.add_argument(
            '--qemu-bin', type=str, default=defaults.QEMU_BIN,
            help=('Path to a custom qemu binary to be tested. Current: '
                  '%(default)s'))
        virt_parser.add_argument(
            '--qemu-dst-bin', type=str, default=defaults.QEMU_DST_BIN,
            help=('Path to a destination qemu binary to be tested. Used as '
                  'incoming QEMU in migration tests. Current: %(default)s'))
        virt_parser.add_argument(
            '--qemu-img-bin', type=str, default=defaults.QEMU_IMG_BIN,
            help=('Path to a custom qemu-img binary to be tested. '
                  'Current %(default)s'))
        virt_parser.add_argument(
            '--qemu-io-bin', type=str, default=defaults.QEMU_IO_BIN,
            help=('Path to a custom qemu-io binary to be tested. '
                  'Current: %(default)s'))
        virt_parser.add_argument(
            '--guest-image-path', type=str, default=defaults.GUEST_IMAGE_PATH,
            help=('Path to a guest image to be used in tests. Current: '
                  '%(default)s'))
        virt_parser.add_argument(
            '--guest-user', type=str, default=defaults.GUEST_USER,
            help=('User that avocado should use for remote logins. Current: '
                  '%(default)s'))
        virt_parser.add_argument(
            '--guest-password', type=str, default=defaults.GUEST_PASSWORD,
            help=('Password for the user avocado should use for remote logins. '
                  'You may omit this if SSH keys are setup in the guest. '
                  'Current: %(default)s'))
        virt_parser.add_argument(
            '--take-screendumps', action='store_true',
            default=defaults.SCREENDUMP_THREAD_ENABLE,
            help=('Take regular QEMU screendumps (PPMs) from VMs under test. '
                  'Current: %(default)s'))
        if VIDEO_ENCODING_SUPPORT:
            virt_parser.add_argument(
                '--record-videos', action='store_true',
                default=defaults.VIDEO_ENCODING_ENABLE,
                help=('Encode videos from VMs under test. '
                      'Implies --take-screendumps. Current: %(default)s'))
        virt_parser.add_argument(
            '--qemu-template', nargs='?', type=FileType('r'),
            help='Create qemu command line from a template')

    def __add_default_values(self, app_args):
        def set_value(path, key, arg=None, value=None):
            if arg:
                value = getattr(app_args, arg, value)
            app_args.avocado_variants.add_default_param("avocado-virt",
                                                        key, value, path)

        set_value('/plugins/virt/qemu/paths', 'qemu_bin', arg='qemu_bin')
        set_value('/plugins/virt/qemu/paths', 'qemu_dst_bin', arg='qemu_dst_bin')
        set_value('/plugins/virt/qemu/paths', 'qemu_img_bin', arg='qemu_img_bin')
        set_value('/plugins/virt/paths', 'qemu_io_bin', arg='qemu_io_bin')
        set_value('/plugins/virt/guest', 'image_path', arg='guest_image_path')
        set_value('/plugins/virt/guest', 'user', arg='guest_user')
        set_value('/plugins/virt/guest', 'password', arg='guest_password')
        set_value('/plugins/virt/screendumps', 'enable', arg='take_screendumps')
        set_value('/plugins/virt/screendumps', 'interval',
                  'screendump_thread_interval',
                  value=defaults.SCREENDUMP_THREAD_INTERVAL)
        set_value('/plugins/virt/qemu/migrate', 'timeout', 'migrate_timeout',
                  value=defaults.MIGRATE_TIMEOUT)
        if getattr(app_args, 'qemu_template', False):
            set_value('/plugins/virt/qemu/template', 'contents',
                      value=app_args.qemu_template.read())
        set_value('/plugins/virt/videos', 'enable', arg='record_videos')
        set_value('/plugins/virt/videos', 'jpeg_quality',
                  value=defaults.VIDEO_ENCODING_JPEG_QUALITY)
        set_value('/plugins/virt/guest', 'disable_restore_image_test',
                  value=defaults.DISABLE_RESTORE_IMAGE_TEST)

    def run(self, args):
        def app_using_human_output(args):
            for key in args.__dict__:
                if key.endswith('output'):
                    if args.__dict__[key] == '-':
                        return False
            return True
        self.__add_default_values(args)

        if (not defaults.DISABLE_RESTORE_IMAGE_JOB and
                defaults.DISABLE_RESTORE_IMAGE_TEST):
            # Don't restore the image when also restoring image per-test
            drive_file = getattr(args, 'guest_image_path', None)
            compressed_drive_file = drive_file + '.xz'
            if os.path.isfile(compressed_drive_file):
                if app_using_human_output(args):
                    LOG.debug("Plugin setup (Restoring guest image backup). "
                              "Please wait...")
                cwd = os.getcwd()
                os.chdir(os.path.dirname(compressed_drive_file))
                process.run('xz -d %s' %
                            os.path.basename(compressed_drive_file))
                os.chdir(cwd)

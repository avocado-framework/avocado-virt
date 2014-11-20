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

from avocado.core import output
from avocado.utils import process
from avocado.plugins import plugin
from avocado.virt import defaults

try:
    from avocado.virt.utils import video
    VIDEO_ENCODING_SUPPORT = True
except:
    VIDEO_ENCODING_SUPPORT = False


class VirtOptions(plugin.Plugin):

    """
    Add virtualization testing related options.
    """

    name = 'virt'
    enabled = True

    def configure(self, parser):
        virt_parser = parser.runner.add_argument_group('virtualization testing arguments')
        virt_parser.add_argument(
            '--qemu-bin', type=str,
            help=('Path to a custom qemu binary to be tested. Default path: %s'
                  % defaults.qemu_bin))
        virt_parser.add_argument(
            '--qemu-dst-bin', type=str,
            help=('Path to a destination qemu binary to be tested. Used as '
                  'incoming qemu in migration tests. Default path: %s'
                  % defaults.qemu_dst))
        virt_parser.add_argument(
            '--qemu-img-bin', type=str,
            help=('Path to a custom qemu-img binary to be tested. Default path: %s'
                  % defaults.qemu_img_bin))
        virt_parser.add_argument(
            '--qemu-io-bin', type=str,
            help=('Path to a custom qemu-io binary to be tested. Default path: %s'
                  % defaults.qemu_io_bin))
        virt_parser.add_argument(
            '--guest-image-path', type=str,
            help=('Path to a guest image to be used in tests. Default path: %s'
                  % defaults.guest_image_path))
        virt_parser.add_argument(
            '--guest-user', type=str,
            default=defaults.guest_user,
            help=('User that avocado should use for remote logins. Default: %s'
                  % defaults.guest_user))
        virt_parser.add_argument(
            '--guest-password', type=str,
            default=defaults.guest_password,
            help=('Password for the user avocado should use for remote logins. '
                  'You may omit this if SSH keys are setup in the guest. '
                  'Default: %s' % defaults.guest_password))
        virt_parser.add_argument(
            '--disable-restore-image-test', action='store_true',
            default=defaults.disable_restore_image_test,
            help=('Do not restore the guest image before individual tests '
                  'start. Default: %s' % defaults.disable_restore_image_test))
        virt_parser.add_argument(
            '--disable-restore-image-job', action='store_true',
            default=defaults.disable_restore_image_job,
            help=('Do not restore the guest image before a test job '
                  'starts. Default: %s' % defaults.disable_restore_image_job))
        virt_parser.add_argument(
            '--take-screendumps', action='store_true',
            default=defaults.screendump_thread_enable,
            help=('Take regular QEMU screendumps (PPMs) from VMs under test. '
                  'Default: %s' % defaults.screendump_thread_enable))
        virt_parser.add_argument(
            '--screendump-interval', type=float,
            default=defaults.screendump_thread_interval,
            help=('Interval (s) used to produce the screendumps. '
                  'Default: %s' % defaults.screendump_thread_interval))
        virt_parser.add_argument(
            '--migrate-timeout', type=float,
            default=defaults.migrate_timeout,
            help=('Time (s) to wait until a QEMU migration is finished. '
                  'Default: %s' % defaults.migrate_timeout))
        if VIDEO_ENCODING_SUPPORT:
            virt_parser.add_argument(
                '--record-videos', action='store_true',
                default=defaults.video_encoding_enable,
                help=('Encode videos from VMs under test. '
                      'Implies --take-screendumps. Default: %s' %
                      defaults.video_encoding_enable))
            virt_parser.add_argument(
                '--jpeg-conversion-quality', type=int,
                default=defaults.video_encoding_jpeg_quality,
                help=('Quality used to convert PPMs to JPGs. The larger this '
                      'setting, the larger the result video will be '
                      '(maximum 100). Default: %s' %
                      defaults.video_encoding_jpeg_quality))

        self.configured = True

    def activate(self, app_args):
        def app_using_human_output(app_args):
            for key in app_args.__dict__:
                if key.endswith('output'):
                    if app_args.__dict__[key] == '-':
                        return False
            return True

        view = output.View(app_args=app_args)
        if (hasattr(app_args, 'disable_restore_image_test') and
                getattr(app_args, 'disable_restore_image_test')):
            if (hasattr(app_args, 'disable_restore_image_job') and not
                    getattr(app_args, 'disable_restore_image_job')):
                if app_args.guest_image_path:
                    drive_file = app_args.guest_image_path
                else:
                    drive_file = defaults.guest_image_path
                compressed_drive_file = drive_file + '.7z'
                if os.path.isfile(compressed_drive_file):
                    if app_using_human_output(app_args):
                        msg = ("Plugin setup (Restoring guest image backup). "
                               "Please wait...")
                        view.notify(event='minor', msg=msg)
                    cwd = os.getcwd()
                    os.chdir(os.path.dirname(compressed_drive_file))
                    process.run('7za -y e %s' %
                                os.path.basename(compressed_drive_file))
                    os.chdir(cwd)

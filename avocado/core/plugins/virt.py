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

from argparse import FileType

from avocado.core import output
from avocado.core.plugins import plugin
from avocado.utils import process
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
        virt_parser = parser.runner.add_argument_group('virtualization '
                                                       'testing arguments')
        virt_parser.add_argument(
            '--qemu-bin', type=str, default=defaults.qemu_bin,
            help=('Path to a custom qemu binary to be tested. Current path: %s'
                  % defaults.qemu_bin))
        virt_parser.add_argument(
            '--qemu-dst-bin', type=str, default=defaults.qemu_dst,
            help=('Path to a destination qemu binary to be tested. Used as '
                  'incoming qemu in migration tests. Current path: %s'
                  % defaults.qemu_dst))
        virt_parser.add_argument(
            '--qemu-img-bin', type=str, default=defaults.qemu_img_bin,
            help=('Path to a custom qemu-img binary to be tested. '
                  'Current path: %s' % defaults.qemu_img_bin))
        virt_parser.add_argument(
            '--qemu-io-bin', type=str, default=defaults.qemu_io_bin,
            help=('Path to a custom qemu-io binary to be tested. '
                  'Current path: %s' % defaults.qemu_io_bin))
        virt_parser.add_argument(
            '--guest-image-path', type=str, default=defaults.guest_image_path,
            help=('Path to a guest image to be used in tests. '
                  'Current path: %s' % defaults.guest_image_path))
        virt_parser.add_argument(
            '--guest-user', type=str,
            default=defaults.guest_user,
            help=('User that avocado should use for remote logins. Current: %s'
                  % defaults.guest_user))
        virt_parser.add_argument(
            '--guest-password', type=str,
            default=defaults.guest_password,
            help=('Password for the user avocado should use for remote logins. '
                  'You may omit this if SSH keys are setup in the guest. '
                  'Current: %s' % defaults.guest_password))
        virt_parser.add_argument(
            '--take-screendumps', action='store_true',
            default=defaults.screendump_thread_enable,
            help=('Take regular QEMU screendumps (PPMs) from VMs under test. '
                  'Current: %s' % defaults.screendump_thread_enable))
        if VIDEO_ENCODING_SUPPORT:
            virt_parser.add_argument(
                '--record-videos', action='store_true',
                default=defaults.video_encoding_enable,
                help=('Encode videos from VMs under test. '
                      'Implies --take-screendumps. Current: %s' %
                      defaults.video_encoding_enable))
        virt_parser.add_argument(
            '--qemu-template', nargs='?', type=FileType('r'),
            help='Create qemu command line from a template')

        self.configured = True

    def activate(self, app_args):
        def app_using_human_output(app_args):
            for key in app_args.__dict__:
                if key.endswith('output'):
                    if app_args.__dict__[key] == '-':
                        return False
            return True

        def set_value(path, key, value):
            root.get_node(path, True).value[key] = value
        root = app_args.default_multiplex_tree
        set_value('/plugins/virt/qemu/paths', 'qemu_bin', app_args.qemu_bin)
        set_value('/plugins/virt/qemu/paths', 'qemu_dst_bin',
                  app_args.qemu_dst_bin)
        set_value('/plugins/virt/qemu/paths', 'qemu_img_bin',
                  app_args.qemu_img_bin)
        set_value('/plugins/virt/paths', 'qemu_io_bin', app_args.qemu_io_bin)
        set_value('/plugins/virt/guest', 'image_path', app_args.guest_image_path)
        set_value('/plugins/virt/guest', 'user', app_args.guest_user)
        set_value('/plugins/virt/guest', 'password', app_args.guest_password)
        set_value('/plugins/virt/screendumps', 'enable',
                  app_args.take_screendumps)
        set_value('/plugins/virt/screendumps', 'interval',
                  defaults.screendump_thread_interval)
        set_value('/plugins/virt/qemu/migrate', 'timeout',
                  defaults.migrate_timeout)
        if app_args.qemu_template:
            set_value('/plugins/virt/qemu/template', 'contents',
                      app_args.qemu_template.read())
        set_value('/plugins/virt/videos', 'enable',
                  getattr(app_args, "record_videos", False))
        set_value('/plugins/virt/videos', 'jpeg_quality',
                  defaults.video_encoding_jpeg_quality)

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

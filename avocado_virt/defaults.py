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
Default values used in tests and plugin code.
"""

from avocado.core import data_dir
from avocado.core.settings import settings
from avocado.core.settings import SettingsError
from .qemu import path

try:
    qemu_bin = settings.get_value('virt.qemu.paths', 'qemu_bin')
except SettingsError:
    try:
        qemu_bin = path.get_qemu_binary()
    except path.QEMUCmdNotFoundError:
        qemu_bin = 'qemu'

try:
    qemu_dst = settings.get_value('virt.qemu.paths', 'qemu_dst_bin')
except SettingsError:
    try:
        qemu_dst = path.get_qemu_dst_binary()
    except path.QEMUCmdNotFoundError:
        qemu_dst = 'qemu'

try:
    qemu_img_bin = settings.get_value('virt.qemu.paths', 'qemu_img_bin')
except SettingsError:
    try:
        qemu_img_bin = path.get_qemu_img_binary()
    except path.QEMUCmdNotFoundError:
        qemu_img_bin = 'qemu-img'

try:
    qemu_img_bin = settings.get_value('virt.qemu.paths', 'qemu_io_bin')
except SettingsError:
    try:
        qemu_io_bin = path.get_qemu_io_binary()
    except path.QEMUCmdNotFoundError:
        qemu_io_bin = 'qemu-io'

# The defaults are related to the default image used (JeOS)
try:
    guest_image_path = settings.get_value('virt.guest', 'image_path')
except SettingsError:
    guest_image_path = data_dir.get_datafile_path('images',
                                                  'jeos-23-64.qcow2')

guest_user = settings.get_value('virt.guest', 'user', default='root')
guest_password = settings.get_value('virt.guest', 'password', default='123456')

disable_restore_image_test = settings.get_value('virt.restore', 'disable_for_test', default=False, key_type=bool)
disable_restore_image_job = settings.get_value('virt.restore', 'disable_for_job', default=False, key_type=bool)

screendump_thread_enable = settings.get_value('virt.screendumps', 'enable', default=False, key_type=bool)
screendump_thread_interval = settings.get_value('virt.screendumps', 'interval', default=0.5, key_type=float)

video_encoding_enable = settings.get_value('virt.videos', 'enable', default=False, key_type=bool)
video_encoding_jpeg_quality = settings.get_value('virt.videos', 'jpeg_conversion_quality', default=95, key_type=int)

migrate_timeout = settings.get_value('virt.qemu.migrate', 'timeout', default=60.0, key_type=float)

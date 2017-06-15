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


#: The name or path of the QEMU binary.  Hardcoded default is 'qemu',
#: but will be overwritten by configuration value ("qemu_bin" under
#: section [virt.qemu.paths]) or by a dynamic (run time) search for a
#: suitable binary
QEMU_BIN = 'qemu'
try:
    QEMU_BIN = settings.get_value('virt.qemu.paths', 'qemu_bin')
except SettingsError:
    try:
        QEMU_BIN = path.get_qemu_binary()
    except path.QEMUCmdNotFoundError:
        pass

#: The name or path of the QEMU binary used for the destination
#: instance when doing migration.  Hardcoded default is 'qemu', but
#: will be overwritten by configuration value ("qemu_bin" under section
#: [virt.qemu.paths]) or by a dynamic (run time) search for a suitable
#: binary
QEMU_DST_BIN = 'qemu'
try:
    QEMU_DST_BIN = settings.get_value('virt.qemu.paths', 'qemu_dst_bin')
except SettingsError:
    try:
        QEMU_DST_BIN = path.get_qemu_dst_binary()
    except path.QEMUCmdNotFoundError:
        pass

#: The name or path of the qemu-img binary
QEMU_IMG_BIN = 'qemu-img'
try:
    QEMU_IMG_BIN = settings.get_value('virt.qemu.paths', 'qemu_img_bin')
except SettingsError:
    try:
        QEMU_IMG_BIN = path.get_qemu_img_binary()
    except path.QEMUCmdNotFoundError:
        pass

#: The name or path of the qemu-io binary
QEMU_IO_BIN = 'qemu-io'
try:
    QEMU_IMG_BIN = settings.get_value('virt.qemu.paths', 'qemu_io_bin')
except SettingsError:
    try:
        qemu_io_bin = path.get_qemu_io_binary()
    except path.QEMUCmdNotFoundError:
        pass

#: The path to the guest image to be used
GUEST_IMAGE_PATH = ''
try:
    GUEST_IMAGE_PATH = settings.get_value('virt.guest', 'image_path')
except SettingsError:
    GUEST_IMAGE_PATH = data_dir.get_datafile_path('images',
                                                  'jeos-25-64.qcow2')

#: The username that will be used when trying to log on to guest VMs
GUEST_USER = settings.get_value('virt.guest', 'user', default='root')

#: The password that will be used when trying to log on to guests VMs
GUEST_PASSWORD = settings.get_value('virt.guest', 'password', default='123456')

#: If the restoration of the guest image should be disabled between tests
DISABLE_RESTORE_IMAGE_TEST = settings.get_value('virt.restore', 'disable_for_test',
                                                default=False, key_type=bool)

#: If the restoration of the guest image should be disabled between jobs
DISABLE_RESTORE_IMAGE_JOB = settings.get_value('virt.restore', 'disable_for_job',
                                               default=False, key_type=bool)

#: If the screendump thread should be enabled
SCREENDUMP_THREAD_ENABLE = settings.get_value('virt.screendumps', 'enable',
                                              default=False, key_type=bool)

#: The interval between screedumps (in seconds)
SCREENDUMP_THREAD_INTERVAL = settings.get_value('virt.screendumps', 'interval',
                                                default=0.5, key_type=float)

#: If the video encoding should be enabled
VIDEO_ENCODING_ENABLE = settings.get_value('virt.videos', 'enable',
                                           default=False, key_type=bool)

#: The quality of the video encoding
VIDEO_ENCODING_JPEG_QUALITY = settings.get_value('virt.videos',
                                                 'jpeg_conversion_quality',
                                                 default=95, key_type=int)

#: The timeout for migrations
MIGRATE_TIMEOUT = settings.get_value('virt.qemu.migrate', 'timeout',
                                     default=60.0, key_type=float)

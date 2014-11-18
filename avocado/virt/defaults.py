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
from avocado.virt.qemu import path

try:
    qemu_bin = path.get_qemu_binary()
except:
    qemu_bin = 'qemu'

try:
    qemu_dst = path.get_qemu_dst_binary()
except:
    qemu_dst = 'qemu'

try:
    qemu_img_bin = path.get_qemu_img_binary()
except:
    qemu_img_bin = 'qemu-img'

try:
    qemu_io_bin = path.get_qemu_io_binary()
except:
    qemu_io_bin = 'qemu-io'

# The defaults are related to the default image used (JeOS)
guest_image_path = data_dir.get_datafile_path('images',
                                              'jeos-20-64.qcow2')
guest_user = 'root'
guest_password = '123456'

disable_restore_image_test = False
disable_restore_image_job = False

screendump_thread_enable = False
screendump_thread_interval = 0.5

video_encoding_enable = False
video_encoding_jpeg_quality = 95

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
# Copyright: Red Hat Inc. 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

# pylint: disable=E0611
from distutils.core import setup

VERSION = '0.1.0'

setup(name='avocado-virt',
      version=VERSION,
      description='Avocado Virtualization Testing Plugin',
      author='Lucas Meneghel Rodrigues',
      author_email='lmr@redhat.com',
      url='http://github.com/avocado-framework/avocado-virt',
      packages=['avocado',
                'avocado.virt',
                'avocado.virt.qemu',
                'avocado.plugins'],
      )

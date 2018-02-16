.. _get-started:

===============
Getting Started
===============

The first step towards using Avocado-Virt is, quite obviously, installing it.

Installing Avocado
==================

Start by following the instructions on `this link <http://avocado-framework.readthedocs.io/en/latest/GetStartedGuide.html#installing-avocado>`__.

Installing Avocado-Virt
=======================

The official source for avocado-virt is the GIT repository host at `GitHub <https://gitub.com/avocado-framework/avocado-virt`_.  You can clone it by running::

  $ git clone https://github.com/avocado-framework/avocado-virt

Then install ``avocado-virt`` itself with::

  $ cd avocado-virt
  $ python setup.py install

You may want to use ``python setup.py install --user`` to install
locally or even ``python setup.py develop --user`` to run from the
source tree.

Bootstrapping Avocado-Virt
--------------------------

After the package, a bootstrap process must be run wit the `vt-bootstrap`
command. Example::

    $ avocado virt-bootstrap

The output should be similar to::

    Probing your system for test requirements
    xz present
    Verifying expected SHA1 sum from https://avocado-project.org/data/assets/jeos/25/SHA1SUM_JEOS25
    Expected SHA1 sum: 7f5a440f6eb83577d42f9f68987534b1076967d8
    Compressed JeOS image found in /home/<user>/avocado/data/images/jeos-25-64.qcow2.xz, with proper SHA1
    Uncompressing the JeOS image to restore pristine state. Please wait...
    Successfully uncompressed the image
    Your system appears to be all set to execute tests

Another addition you'll notice is that the avocado subcommand ``run`` now has
extra parameters that you can pass::

    $ avocado run -h
    ...
    virtualization testing arguments:
      --qemu-bin QEMU_BIN   Path to a custom qemu binary to be tested. Current
                            path: /bin/qemu-kvm
      --qemu-dst-bin QEMU_DST_BIN
                            Path to a destination qemu binary to be tested. Used
                            as incoming qemu in migration tests. Current path:
                            /bin/qemu-kvm
      --qemu-img-bin QEMU_IMG_BIN
                            Path to a custom qemu-img binary to be tested. Current
                            path: /bin/qemu-img
      --qemu-io-bin QEMU_IO_BIN
                            Path to a custom qemu-io binary to be tested. Current
                            path: /bin/qemu-io
      --guest-image-path GUEST_IMAGE_PATH
                            Path to a guest image to be used in tests. Current
                            path: /home/<user>/avocado/data/images/jeos-25-64.qcow2
      --guest-user GUEST_USER
                            User that avocado should use for remote logins.
                            Current: root
      --guest-password GUEST_PASSWORD
                            Password for the user avocado should use for remote
                            logins. You may omit this if SSH keys are setup in the
                            guest. Current: 123456
      --take-screendumps    Take regular QEMU screendumps (PPMs) from VMs under
                            test. Current: False
      --record-videos       Encode videos from VMs under test. Implies --take-
                            screendumps. Current: False
      --qemu-template [QEMU_TEMPLATE]
                            Create qemu command line from a template


That's right, the virt plugin gives you new options on the runner specific to
the QEMU related tests. For example, you can provide ``--qemu-bin`` to tell your
tests that you want a specific QEMU binary instead of whatever the runner could
find looking in the system PATH or environment variables.

Now, after you bootstrapped your tests, you may want to look for some examples on
how to build your tests. We have a repo with example virtualization tests
in ``https://github.com/avocado-framework/avocado-virt-tests.git``. Cloning this
repo will allow you to run the example tests and study them::

    $ git clone https://github.com/avocado-framework/avocado-virt-tests.git
    Cloning into 'avocado-virt-tests'...
    remote: Counting objects: 15, done.
    remote: Total 15 (delta 0), reused 0 (delta 0)
    Unpacking objects: 100% (15/15), done.
    Checking connectivity... done.
    $ cd avocado-virt-tests/
    $ avocado run qemu/boot.py
    JOB ID     : <id>
    JOB LOG    : /home/<user>/avocado/job-results/job-<timestamp-shortid>/job.log
    TESTS      : 1
    (1/1) qemu/boot.py:BootTest.test_boot: PASS (23.13 s)
    RESULTS    : PASS 1 | ERROR 0 | FAIL 0 | SKIP 0 | WARN 0 | INTERRUPT 0
    JOB HTML   : /home/<user>/avocado/job-results/job-<timestamp-shortid>/html/results.html
    TIME       : 23.13 s

With this info, we are covering the basics. We'll cover setup details and the
available test API in later sessions.

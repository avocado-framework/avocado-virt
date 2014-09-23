.. _get-started:

=============================
Getting started guide - users
=============================

If you want to simply use avocado as a test runner/test API, you can install a
distro package. For Fedora, you can look at `lmr's autotest COPR`_. Work is
underway for Ubuntu/Mint packages.

.. _lmr's autotest COPR: http://copr.fedoraproject.org/coprs/lmr/Autotest

Installing avocado-virt - Fedora
--------------------------------

You can install the rpm package by performing the following commands::

    sudo curl http://copr.fedoraproject.org/coprs/lmr/Autotest/repo/fedora-20/lmr-Autotest-fedora-20.repo -o /etc/yum.repos.d/autotest.repo
    sudo yum update
    sudo yum install avocado avocado-virt

New options available in the test runner
----------------------------------------

After installing avocado-virt, if you had used avocado without the virt plugin
before, you'll notice a new subcommand, ``virt-bootstrap``::

    $ avocado
    usage: avocado [-h] [-v] [-V] [--logdir LOGDIR] [--loglevel LOG_LEVEL]
                   [--plugins PLUGINS_DIR]
                   {run,virt-bootstrap,plugins,list,sysinfo,datadir,multiplex} ...

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -V, --verbose         print extra debug messages
      --logdir LOGDIR       Alternate logs directory
      --loglevel LOG_LEVEL  Debug Level
      --plugins PLUGINS_DIR
                            Load extra plugins from directory

    subcommands:
      valid subcommands

      {run,virt-bootstrap,plugins,list,sysinfo,datadir,multiplex}
                            subcommand help
        run                 Run one or more tests (test module in .py, test alias
                            or dropin)
        virt-bootstrap      Download image files important to avocado virt tests
        plugins             List all plugins loaded
        list                List available test modules
        sysinfo             Collect system information
        datadir             List all relevant directories used by avocado
        multiplex           Generate a list of dictionaries with params from a
                            multiplex file

This command is used to download the latest JeOS image, necessary to run
QEMU related tests. The JeOS image is a qcow2 minimal image based on Fedora
(latest stable version available at a given time). It's also going to uncompress
it to ensure the image is pristine. Running the command, you'll see::

    $ avocado virt-bootstrap
    Verifying if you have '7za' installed
    Checking if JeOS is in the right location and matching SHA1
    Verifying expected SHA1 sum from https://lmr.fedorapeople.org/jeos/SHA1SUM_JEOS20
    Expected SHA1 sum: d6ee27df6fd855065adb9a42448ca0a43768b910
    Image found, with proper SHA1
    Uncompressing the image...

Another addition you'll notice is that the avocado subcommand ``run`` now has
extra parameters that you can pass::

    $ avocado run -h
    ...
    virtualization testing arguments:
      --qemu-bin QEMU_BIN   Path to a custom qemu binary to be tested. Default
                            path: /bin/qemu-kvm
      --qemu-dst-bin QEMU_DST_BIN
                            Path to a destination qemu binary to be tested. Used
                            as incoming qemu in migration tests. Default path:
                            /bin/qemu-kvm
      --guest-image-path GUEST_IMAGE_PATH
                            Path to a guest image to be used in tests. Default
                            path: /home/lmr/avocado/data/images/jeos-20-64.qcow2
      --guest-user GUEST_USER
                            User that avocado should use for remote logins.
                            Default: root
      --guest-password GUEST_PASSWORD
                            Password for the user avocado should use for remote
                            logins. Default: 123456
      --disable-restore-image-test
                            Do not restore the guest image before individual tests
                            start. Default: False
      --disable-restore-image-job
                            Do not restore the guest image before a test job
                            starts. Default: False


That's right, the virt plugin gives you new options on the runner specific to
the qemu related tests. For example, you can provide ``--qemu-bin`` to tell your
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
    JOB ID    : 8c06fcbefb6bdb9a177d47606d3a3e3b785c372a
    JOB LOG   : /home/lmr/avocado/job-results/job-2014-09-12T16.21-8c06fcb/job.log
    TESTS     : 1
    (1/1) qemu/boot.py: PASS (13.59 s)
    PASS      : 1
    ERROR     : 0
    FAIL      : 0
    SKIP      : 0
    WARN      : 0
    NOT FOUND : 0
    TIME      : 13.59 s

With this info, we are covering the basics. We'll cover setup details and the
available test API in later sessions.

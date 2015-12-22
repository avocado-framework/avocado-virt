PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/avocado-virt
PROJECT=avocado
VERSION="0.26.0"
AVOCADO_DIRNAME?=avocado
DIRNAME=$(shell echo $${PWD\#\#*/})

all:
	@echo
	@echo "Development related targets:"
	@echo "check:  Runs tree static check, unittests and functional tests"
	@echo "clean:  Get rid of scratch and byte files"
	@echo
	@echo "Platform independent distribution/installtion related targets:"
	@echo "source:   Create source package"
	@echo "install:  Install on local system"
	@echo
	@echo "RPM related targets:"
	@echo "rpm:   Generate binary RPMs"
	@echo
	@echo "Debian related targets:"
	@echo "deb:      Generate both source and binary debian packages"
	@echo "deb-src:  Generate a source debian package"
	@echo "deb-bin:  Generate a binary debian package"
	@echo

source:
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=SOURCES --prune

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

prepare-source:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	dch -D "trusty" -M -v "$(VERSION)" "Automated (make builddeb) build."
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*

deb-src: prepare-source
	# build the source package
	dpkg-buildpackage -S -elookkas@gmail.com -rfakeroot

deb-bin: prepare-source
	# build binary package
	dpkg-buildpackage -b -rfakeroot

deb: prepare-source
	# build both source and binary packages
	dpkg-buildpackage -i -I -rfakeroot

rpm: source
	rpmbuild --define '_topdir %{getenv:PWD}' \
		 -ba avocado-virt.spec
check:
	selftests/checkall
clean:
	$(PYTHON) setup.py clean
	$(MAKE) -f $(CURDIR)/debian/rules clean || true
	rm -rf build/ MANIFEST BUILD BUILDROOT SPECS RPMS SRPMS SOURCES
	find . -name '*.pyc' -delete

link:
	ln -sf ../../$(DIRNAME)/avocado/virt ../$(AVOCADO_DIRNAME)/avocado
	ln -sf ../../../../$(DIRNAME)/etc/avocado/conf.d/virt.conf ../$(AVOCADO_DIRNAME)/etc/avocado/conf.d/
	ln -sf ../../../../$(DIRNAME)/avocado/core/plugins/virt.py ../$(AVOCADO_DIRNAME)/avocado/core/plugins/
	ln -sf ../../../../$(DIRNAME)/avocado/core/plugins/virt_bootstrap.py ../$(AVOCADO_DIRNAME)/avocado/core/plugins/

unlink:
	test -L ../$(AVOCADO_DIRNAME)/avocado/virt && rm -f ../$(AVOCADO_DIRNAME)/avocado/virt || true
	test -L ../$(AVOCADO_DIRNAME)/etc/avocado/conf.d/virt.conf && rm -f ../$(AVOCADO_DIRNAME)/etc/avocado/conf.d/virt.conf || true
	test -L ../$(AVOCADO_DIRNAME)/avocado/core/plugins/virt.py && rm -f ../$(AVOCADO_DIRNAME)/avocado/core/plugins/virt.py || true
	test -L ../$(AVOCADO_DIRNAME)/avocado/core/plugins/virt_bootstrap.py && rm -f ../$(AVOCADO_DIRNAME)/avocado/core/plugins/virt_bootstrap.py || true


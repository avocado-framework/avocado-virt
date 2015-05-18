Summary: Avocado Virt Plugin
Name: avocado-virt
Version: 0.24.0
Release: 1%{?dist}
License: GPLv2
Group: Development/Tools
URL: http://avocado-framework.readthedocs.org/
Source: avocado-virt-%{version}.tar.gz
BuildRequires: python2-devel
BuildArch: noarch
Requires: python, avocado

%description
Avocado Virt is a plugin that allows users to run virtualization related
tests in avocado. Up to this point, QEMU/KVM is the only backend supported.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root %{buildroot} --skip-build

%files
%defattr(-,root,root,-)
%doc README.rst LICENSE
%exclude %{python_sitelib}/avocado/virt/utils/video.py*
%{python_sitelib}/avocado*

%package video
Summary: Avocado Virt VM Video Support
Requires: avocado-virt, python-pillow, gstreamer1-plugins-good, gobject-introspection

%description video
This Avocado Virt Plugin subpackage allows you to encode videos from vms
during avocado virt tests.

%files video
%{python_sitelib}/avocado/virt/utils/video.py*

%changelog
* Mon May 18 2015 Ruda Moura <rmoura@redhat.com> - 0.24.0-1
- New upstream release

* Mon Apr 21 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.23.0-1
- New upstream release

* Mon Oct 13 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.14.0-1
- New upstream release (sync releases with avocado releases)

* Mon Sep 22 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.3-1
- New upstream release

* Wed Sep  3 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.2-1
- New upstream release

* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.1-1
- New upstream release

* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.0-1
- First RPM

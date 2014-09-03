Summary: Avocado Virt Plugin
Name: avocado-virt
Version: 0.1.1
Release: 1%{?dist}
License: GPLv2
Group: Development/Tools
URL: http://avocado-framework.readthedocs.org/
Source: avocado-virt-%{version}.tar.gz
BuildRequires: python2-devel
BuildArch: noarch
Requires: python, avocado

%description
Avocado is a set of tools and libraries (what people call
these days a framework) to perform automated testing.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root %{buildroot} --skip-build

%files
%defattr(-,root,root,-)
%doc README.rst LICENSE
%{python_sitelib}/avocado*

%changelog
* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.1-1
- New upstream release
* Tue Sep  2 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.0-1
- First RPM

%define debug_package %{nil}
%define _enable_debug_packages %{nil}

# Defining the package namespace
# NOTE: pkg variable is a hack to fix invalid macro inside of macros.php
%global ns_name ea
%global ns_dir /opt/cpanel
%global pkg php84

# Force Software Collections on
%global _scl_prefix %{ns_dir}
%global scl %{ns_name}-%{pkg}
# HACK: OBS Doesn't support macros in BuildRequires statements, so we have
#       to hard-code it here.
# https://en.opensuse.org/openSUSE:Specfile_guidelines#BuildRequires
%global scl_prefix %{scl}-
%scl_package php

# API/ABI check
%global apiver      20240924
%global zendver     20240924
%global pdover      20240423

# Adds -z now to the linker flags
%global _hardened_build 1

# version used for php embedded library soname
%global embed_version 8.4

# Ugly hack. Harcoded values to avoid relocation.
%global _httpd_confdir     %{_root_sysconfdir}/apache2/conf.d
%global _httpd_moddir      %{_libdir}/apache2/modules
%global _root_httpd_moddir %{_root_libdir}/apache2/modules

# httpd 2.4 values
%global _httpd_apxs        %{_root_bindir}/apxs
%global _httpd_modconfdir  %{_root_sysconfdir}/apache2/conf.modules.d
%global _httpd_contentdir  /usr/share/apache2

# disabling DSO, for details on why see https://github.com/CpanelInc/ea-php81/blob/master/DESIGN.dso.md
%global with_httpd           0

%global mysql_sock %(mysql_config --socket  2>/dev/null || echo /var/lib/mysql/mysql.sock)

# Regression tests take a long time, you can skip 'em with this
%{!?runselftest: %{expand: %%global runselftest 0}}

%if 0%{?rhel} >= 8
%else
Requires: ea-libcurl
%global libcurl_prefix /opt/cpanel/libcurl
%endif

# Use the arch-specific mysql_config binary to avoid mismatch with the
# arch detection heuristic used by bindir/mysql_config.
%global mysql_config %{_root_libdir}/mysql/mysql_config

%global with_tidy 1
%global libtidy_prefix /opt/cpanel/libtidy

%global with_sqlite3   1

%if 0%{?rhel} >= 8
%global with_pcre 1
%else
%global with_pcre 0
%endif

%global isasuffix -%{__isa_bits}

%global with_systemd 1

%global with_zip     1

Requires: ea-libzip
BuildRequires: ea-libzip
BuildRequires: ea-libzip-devel
%if 0%{?rhel} == 8
BuildRequires: ea-re2c
%else
BuildRequires: re2c
%endif

%global db_devel  libdb-devel

%define ea_openssl_ver 1.1.1d-1

%if 0%{?rhel} >= 8
%define libcurl_ver 7.61.0
%else
%define ea_libcurl_ver 7.68.0-2
%endif

%if 0%{rhel} > 7
%global with_avif 1
%else
%global with_avif 0
%endif

Summary:  PHP scripting language for creating dynamic web sites
Vendor:   cPanel, Inc.
Name:     %{?scl_prefix}php
Version:  8.4.10
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4588 for more details
%define release_prefix 1
Release:  %{release_prefix}%{?dist}.cpanel
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM is licensed under BSD
License:  PHP and Zend and BSD
Group:    Development/Languages
URL:      http://www.php.net/

%global litespeed_version 8.1

Source0: php-%{version}.tar.bz2
Source1: https://www.litespeedtech.com/packages/lsapi/php-litespeed-%{litespeed_version}.tgz
Source2: php.ini
Source3: macros.php
Source4: php-fpm.conf
Source5: php-fpm-www.conf
Source6: php-fpm.service
Source7: php-fpm.logrotate
Source8: php-fpm.sysconfig
Source11: php-fpm.init
# Configuration files for some extensions
Source50: 10-opcache.ini
Source51: opcache-default.blacklist

Patch42: 0001-EA4-OBS-ready.patch

# Prevent pear package from dragging in devel, which drags in a lot of
# stuff for a production machine: https://bugzilla.redhat.com/show_bug.cgi?id=657812
Patch43: 0002-Prevent-PEAR-package-from-bringing-in-devel.patch

# cPanel patches
Patch100: 0003-Modify-standard-mail-extenstion-to-add-X-PHP-Script.patch
Patch102: 0005-Ensure-that-php.d-is-not-scanned-when-PHPRC-is-set.patch
Patch104: 0006-FPM-Ensure-docroot-is-in-the-user-s-homedir.patch
Patch105: 0007-Chroot-FPM-users-with-noshell-and-jailshell.patch
Patch106: 0008-Patch-epoll.c-per-bug-report-in-upstream.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch107: 0009-Add-support-for-use-of-the-system-timezone-database.patch

Patch402: 0010-0022-PLESK-missed-kill.patch
Patch403: 0011-Revert-new-.user.ini-search-behavior.patch
Patch404: 0012-Prevent-kill_all_lockers-from-crashing-PHP.patch

%if 0%{?rhel} == 7
BuildRequires: devtoolset-8 devtoolset-8-gcc devtoolset-8-gcc-c++ kernel-devel
%endif

%if 0%{rhel} >= 10
BuildRequires: langpacks-fonts-en
%endif

BuildRequires: ea-libxml2-devel
BuildRequires: bzip2-devel, %{db_devel}

%if 0%{?rhel} >= 8
BuildRequires: libcurl >= %{libcurl_ver}, libcurl-devel >= %{libcurl_ver}
BuildRequires: brotli brotli-devel
%else
BuildRequires: %{ns_name}-libcurl >= %{ea_libcurl_ver}, %{ns_name}-libcurl-devel >= %{ea_libcurl_ver}
%endif

BuildRequires: pam-devel
BuildRequires: scl-utils-build
BuildRequires: libstdc++-devel

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

# For Argon2 support
BuildRequires: ea-libargon2-devel
Requires: ea-libargon2
BuildRequires: sqlite-devel >= 3.7.5
BuildRequires: zlib-devel, smtpdaemon
BuildRequires: libedit-devel
%if %{with_pcre}
BuildRequires: pcre2-devel >= 10.30
%else
Provides:      Provides: bundled(pcre2) = 10.32
%endif
BuildRequires: bzip2, perl, libtool >= 1.4.3, gcc-c++
BuildRequires: libtool-ltdl-devel
BuildRequires: bison

BuildRequires: autoconf

# For backwards-compatibility, require php-cli for the time being:
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

# Don't provides extensions, which are not shared library, as .so
%{?filter_provides_in: %filter_provides_in %{_libdir}/php/modules/.*\.so$}
%{?filter_setup}

%description
This version of PHP does not include Apache's mod_php DSO module.

PHP dropped the major version from its '.so' and symbols. Because
 this change is not backwards compatible, cPanel & WHM dropped
 support for DSO in PHP 8.4.

%package sodium
Summary:        Cryptographic Extension Based on Libsodium
Group:          Development/Libraries/PHP
Requires:       %{?scl_prefix}php-common = %{version}
Provides:       %{?scl_prefix}php-sodium = %{version}
Obsoletes:      %{?scl_prefix}php-sodium < %{version}

BuildRequires:  pkgconfig(libsodium) >= 1.0.18
Requires:       libsodium >= 1.0.18

%description sodium
PHP binding to libsodium software library for encryption, decryption,
signatures, password hashing and more.

%package cli
Group: Development/Languages
Summary: Command-line interface for PHP
Requires: %{?scl_prefix}php-common = %{version}-%{release}
Provides: %{?scl_prefix}php-cgi = %{version}-%{release}, %{?scl_prefix}php-cgi%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pcntl = %{version}-%{release} , %{?scl_prefix}php-pcntl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-readline = %{version}-%{release}, %{?scl_prefix}php-readline%{?_isa} = %{version}-%{release}

# For the ea-php-cli wrapper rpm
Requires: ea-php-cli
Requires: ea-php-cli-lsphp

Requires: %{?scl_prefix}php-litespeed = %{version}-%{release}

%description cli
The php-cli package contains the command-line interface
executing PHP scripts, /usr/bin/php, and the CGI interface.

%package dbg
Group: Development/Languages
Summary: The interactive PHP debugger
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description dbg
The %{?scl_prefix}php-dbg package contains the interactive PHP debugger.

%package fpm
Group: Development/Languages
Summary: PHP FastCGI Process Manager
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM and fpm are licensed under BSD
License: PHP and Zend and BSD
Requires: ea-apache24-mod_proxy_fcgi
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: systemd-libs
BuildRequires: systemd-devel
BuildRequires: systemd-units
Requires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
# This is actually needed for the %%triggerun script but Requires(triggerun)
# is not valid.  We can use %%post because this particular %%triggerun script
# should fire just after this package is installed.
Requires(post): systemd-sysv

%description fpm
PHP-FPM (FastCGI Process Manager) is an alternative PHP FastCGI
implementation with some additional features useful for sites of
any size, especially busier sites.

%package litespeed
Summary: LiteSpeed Web Server PHP support
Group: Development/Languages
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description litespeed
The %{?scl_prefix}php-litespeed package provides the %{_bindir}/lsphp command
used by the LiteSpeed Web Server (LSAPI enabled PHP).

%package common
Group: Development/Languages
Summary: Common files for PHP
# All files licensed under PHP version 3.01, except
# fileinfo is licensed under PHP version 3.0
# regex, libmagic are licensed under BSD
# main/snprintf.c, main/spprintf.c and main/rfc1867.c are ASL 1.0
License: PHP and BSD and ASL 1.0
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php(api) = %{apiver}%{isasuffix}
Provides: %{?scl_prefix}php(zend-abi) = %{zendver}%{isasuffix}
Provides: %{?scl_prefix}php(language) = %{version}
Provides: %{?scl_prefix}php(language)%{?_isa} = %{version}
# Provides for all builtin/shared modules:
Provides: %{?scl_prefix}php-core = %{version}, %{?scl_prefix}php-core%{?_isa} = %{version}
Provides: %{?scl_prefix}php-ctype = %{version}-%{release}, %{?scl_prefix}php-ctype%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-date = %{version}-%{release}, %{?scl_prefix}php-date%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-filter = %{version}-%{release}, %{?scl_prefix}php-filter%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-hash = %{version}-%{release}, %{?scl_prefix}php-hash%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-mhash = %{version}-%{release}, %{?scl_prefix}php-mhash%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-json = %{version}-%{release}, %{?scl_prefix}php-json%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pecl-json = %{version}-%{release}, %{?scl_prefix}php-pecl-json%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pecl(json) = %{version}-%{release}, %{?scl_prefix}php-pecl(json)%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-libxml = %{version}-%{release}, %{?scl_prefix}php-libxml%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-openssl = %{version}-%{release}, %{?scl_prefix}php-openssl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-phar = %{version}-%{release}, %{?scl_prefix}php-phar%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pcre = %{version}-%{release}, %{?scl_prefix}php-pcre%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-reflection = %{version}-%{release}, %{?scl_prefix}php-reflection%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-session = %{version}-%{release}, %{?scl_prefix}php-session%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-spl = %{version}-%{release}, %{?scl_prefix}php-spl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-standard = %{version}, %{?scl_prefix}php-standard%{?_isa} = %{version}
Provides: %{?scl_prefix}php-tokenizer = %{version}-%{release}, %{?scl_prefix}php-tokenizer%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-zlib = %{version}-%{release}, %{?scl_prefix}php-zlib%{?_isa} = %{version}-%{release}
%{!?scl:Obsoletes: php-openssl, php-pecl-json, php-json, php-pecl-phar, php-pecl-Fileinfo}
%{?scl:Requires: %{scl}-runtime}

%description common
Requires: %{?scl_prefix}php-common = %{version}
the %{?scl_prefix}php package and the php-cli package.

%package devel
Group: Development/Libraries
Summary: Files needed for building PHP extensions
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}, autoconf, automake
%if %{with_pcre}
Requires: pcre2-devel%{?_isa} >= 10.30
%endif

%description devel
The %{?scl_prefix}php-devel package contains the files needed for building PHP
extensions. If you need to compile your own PHP extensions, you will
need to install this package.

%package opcache
Summary:   The Zend OPcache
Group:     Development/Languages
License:   PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl-zendopcache = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl-zendopcache%{?_isa} = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl(opcache) = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl(opcache)%{?_isa} = %{version}-%{release}

%description opcache
The Zend OPcache provides faster PHP execution through opcode caching and
optimization. It improves PHP performance by storing precompiled script
bytecode in the shared memory. This eliminates the stages of reading code from
the disk and compiling it on future access. In addition, it applies a few
bytecode optimization patterns that make code execution faster.

%package bz2
Summary: A module for PHP applications that interface with .bz2 files
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-bz2 = %{version}-%{release}, %{?scl_prefix}php-bz2%{?_isa} = %{version}-%{release}

%description bz2
The php-bz2 package delivers a module which will allow PHP scripts to
interface with .bz2 files.

%package calendar
Summary: A module for PHP applications that need date/time calculations
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-calendar = %{version}-%{release}, %{?scl_prefix}php-calendar%{?_isa} = %{version}-%{release}

%description calendar
The php-calendar package delivers a module which will allow PHP scripts to
do date and time conversions and calculations.

%package curl
Summary: A module for PHP applications that need to interface with curl
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
%if 0%{rhel} < 8
Requires: %{ns_name}-libcurl >= %{ea_libcurl_ver}
%else
Requires: libcurl
%endif
BuildRequires: libssh2 libssh2-devel libidn libidn-devel ea-libnghttp2-devel
Provides: %{?scl_prefix}php-curl = %{version}-%{release}, %{?scl_prefix}php-curl%{?_isa} = %{version}-%{release}

%description curl
The php-curl package delivers a module which will allow PHP
scripts to connect and communicate to many different types of servers
with many different types of protocols. libcurl currently supports the
http, https, ftp, gopher, telnet, dict, file, and ldap
protocols. libcurl also supports HTTPS certificates, HTTP POST, HTTP
PUT, FTP uploading, HTTP form based upload, proxies, cookies, and
user+password authentication.

%package exif
Summary: A module for PHP applications that need to work with image metadata
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-exif = %{version}-%{release}, %{?scl_prefix}php-exif%{?_isa} = %{version}-%{release}

%description exif
The php-exif package delivers a module which will allow PHP scripts to
work with image meta data. For example, you may use exif functions to
read meta data of pictures taken from digital cameras by working with
information stored in the headers of the JPEG and TIFF images.

%package fileinfo
Summary: A module for PHP applications that need to detect file types
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-fileinfo = %{version}-%{release}, %{?scl_prefix}php-fileinfo%{?_isa} = %{version}-%{release}

%description fileinfo
The php-fileinfo package delivers a module which will allow PHP
scripts to try to guess the content type and encoding of a file by
looking for certain magic byte sequences at specific positions within
the file. While this is not a bullet proof approach the heuristics
used do a very good job.

%package ftp
Summary: A module for PHP applications that need full FTP protocol support
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-ftp = %{version}-%{release}, %{?scl_prefix}php-ftp%{?_isa} = %{version}-%{release}

%description ftp
The php-ftp package delivers a module which will allow PHP scripts
client access to files servers speaking the File Transfer Protocol
(FTP) as defined in http://www.faqs.org/rfcs/rfc959. This extension is
meant for detailed access to an FTP server providing a wide range of
control to the executing script. If you only wish to read from or
write to a file on an FTP server, consider using the ftp:// wrapper
with the %{?scl_prefix}php-filesystem package which provides a simpler
and more intuitive interface.

%package gettext
Summary: A module for PHP applications that need native language support
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-gettext = %{version}-%{release}, %{?scl_prefix}php-gettext%{?_isa} = %{version}-%{release}

%description gettext
The php-gettext package delivers a module which will allow PHP scripts
to access an NLS (Native Language Support) API which can be used to
internationalize your PHP applications. Please see the gettext
documentation for your system for a thorough explanation of these
functions or view the docs at
http://www.gnu.org/software/gettext/manual/gettext.html.

%package iconv
Summary: A module for PHP applications that need to convert character sets
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-iconv = %{version}-%{release}, %{?scl_prefix}php-iconv%{?_isa} = %{version}-%{release}

%description iconv
The php-iconv package delivers a module which will allow PHP scripts
to access the iconv character set conversion facility. With this
module, you can turn a string represented by a local character set
into the one represented by another character set, which may be the
Unicode character set. Supported character sets depend on the iconv
implementation of your system. Note that the iconv function on some
systems may not work as you expect. In such case, it would be a good
idea to install the GNU libiconv library. It will most likely end up
with more consistent results.

%package ldap
Summary: A module for PHP applications that use LDAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

BuildRequires: cyrus-sasl-devel, openldap-devel

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

%description ldap
The %{?scl_prefix}php-ldap package adds Lightweight Directory Access Protocol (LDAP)
support to PHP. LDAP is a set of protocols for accessing directory
services over the Internet. PHP is an HTML-embedded scripting
language.

%package pdo
Summary: A database access abstraction module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}-%{release}
Requires: %{?scl_prefix}php-cli = %{version}-%{release}
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php-pdo-abi = %{pdover}%{isasuffix}
Provides: %{?scl_prefix}php(pdo-abi) = %{pdover}%{isasuffix}
Provides: %{?scl_prefix}php-sqlite3 = %{version}-%{release}, %{?scl_prefix}php-sqlite3%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_sqlite = %{version}-%{release}, %{?scl_prefix}php-pdo_sqlite%{?_isa} = %{version}-%{release}

%description pdo
The %{?scl_prefix}php-pdo package contains a dynamic shared object that will add
a database access abstraction layer to PHP.  This module provides
a common interface for accessing MySQL, PostgreSQL or other
databases.

%package mysqlnd
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-mysql = %{version}-%{release}
Provides: %{?scl_prefix}php-mysql = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_mysql = %{version}-%{release}, %{?scl_prefix}php-pdo_mysql = %{version}-%{release}

%description mysqlnd
The %{?scl_prefix}php-mysqlnd package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.

This package use the MySQL Native Driver

%package posix
Summary: Modules for PHP scripts that need access to POSIX functions
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-posix = %{version}-%{release}, %{?scl_prefix}php-posix%{?_isa} = %{version}-%{release}

%description posix
The php-posix package adds a PHP interface to those functions defined
in the IEEE 1003.1 (POSIX.1) standards document which are not
accessible through other means.

%package pgsql
Summary: A PostgreSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_pgsql = %{version}-%{release}, %{?scl_prefix}php-pdo_pgsql = %{version}-%{release}

BuildRequires: krb5-devel

%if 0%{?rhel} >= 10
BuildRequires: postgresql-private-devel
%else
BuildRequires: postgresql-devel
%endif

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

%description pgsql
The %{?scl_prefix}php-pgsql package add PostgreSQL database support to PHP.
PostgreSQL is an object-relational database management
system that supports almost all SQL constructs. PHP is an
HTML-embedded scripting language. If you need back-end support for
PostgreSQL, you should install this package in addition to the main
php package.

%package process
Summary: Modules for PHP script using system process interfaces
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-shmop = %{version}-%{release}, %{?scl_prefix}php-shmop%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvsem = %{version}-%{release}, %{?scl_prefix}php-sysvsem%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvshm = %{version}-%{release}, %{?scl_prefix}php-sysvshm%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvmsg = %{version}-%{release}, %{?scl_prefix}php-sysvmsg%{?_isa} = %{version}-%{release}

%description process
The %{?scl_prefix}php-process package contains dynamic shared objects which add
support to PHP using system interfaces for inter-process
communication.

%package odbc
Summary: A module for PHP applications that use ODBC databases
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# pdo_odbc is licensed under PHP version 3.0
License: PHP
Requires: %{?scl_prefix}php-pdo = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_odbc = %{version}-%{release}, %{?scl_prefix}php-pdo_odbc = %{version}-%{release}
BuildRequires: unixODBC-devel

%description odbc
The %{?scl_prefix}php-odbc package contains a dynamic shared object that will add
database support through ODBC to PHP. ODBC is an open specification
which provides a consistent API for developers to use for accessing
data sources (which are often, but not always, databases). PHP is an
HTML-embeddable scripting language. If you need ODBC support for PHP
applications, you will need to install this package and the php
package.

%package soap
Summary: A module for PHP applications that use the SOAP protocol
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: ea-libxml2-devel

%description soap
The %{?scl_prefix}php-soap package contains a dynamic shared object that will add
support to PHP for using the SOAP web services protocol.

%package sockets
Summary: A module for PHP applications that need low-level access to sockets
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sockets = %{version}-%{release}, %{?scl_prefix}php-sockets%{?_isa} = %{version}-%{release}

%description sockets
The php-sockets package delivers a module which will allow PHP scripts
access to a low-level interface to the socket communication functions
based on the popular BSD sockets, providing the possibility to act as
a socket server as well as a client.

%package snmp
Summary: A module for PHP applications that query SNMP-managed devices
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: net-snmp-devel

%description snmp
The %{?scl_prefix}php-snmp package contains a dynamic shared object that will add
support for querying SNMP devices to PHP.  PHP is an HTML-embeddable
scripting language. If you need SNMP support for PHP applications, you
will need to install this package and the php package.

%package xml
Summary: A module for PHP applications which use XML
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-dom = %{version}-%{release}, %{?scl_prefix}php-dom%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-domxml = %{version}-%{release}, %{?scl_prefix}php-domxml%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xmlreader = %{version}-%{release}, %{?scl_prefix}php-xmlreader%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xmlwriter = %{version}-%{release}, %{?scl_prefix}php-xmlwriter%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xsl = %{version}-%{release}, %{?scl_prefix}php-xsl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-simplexml = %{version}-%{release}, %{?scl_prefix}php-simplexml%{?_isa} = %{version}-%{release}
BuildRequires: libxslt-devel >= 1.0.18-1, ea-libxml2-devel
Requires: ea-libxml2
BuildRequires: libxslt >= 1.0.18-1
Requires: libxslt >= 1.0.18-1

%description xml
The %{?scl_prefix}php-xml package contains dynamic shared objects which add support
to PHP for manipulating XML documents using the DOM tree,
and performing XSL transformations on XML documents.

%package xmlrpc
Summary: A module for PHP applications which use the XML-RPC protocol
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libXMLRPC is licensed under BSD
License: PHP and BSD
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description xmlrpc
The %{?scl_prefix}php-xmlrpc package contains a dynamic shared object that will add
support for the XML-RPC protocol to PHP.

%package mbstring
Summary: A module for PHP applications which need multi-byte string handling
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libmbfl is licensed under LGPLv2
# onigurama is licensed under BSD
# ucgendat is licensed under OpenLDAP
License: PHP and LGPLv2 and BSD and OpenLDAP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: ea-oniguruma-devel
Requires: ea-oniguruma-devel

%description mbstring
The %{?scl_prefix}php-mbstring package contains a dynamic shared object that will add
support for multi-byte string handling to PHP.

%package gd
Summary: A module for PHP applications for using the gd graphics library
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Requires: libjpeg-turbo%{?_isa}, libpng%{?_isa}, libXpm%{?_isa}, freetype%{?_isa}
BuildRequires: libjpeg-turbo-devel%{?_isa}, libpng-devel%{?_isa}, libXpm-devel%{?_isa}, freetype-devel%{?_isa}
Requires: libwebp%{?_isa}
BuildRequires: libwebp-devel%{?_isa}
%if %{with_avif}
Requires: libavif%{?_isa}
BuildRequires: libavif-devel%{?_isa}
%endif

%description gd
The %{?scl_prefix}php-gd package contains a dynamic shared object that will add
support for using the gd graphics library to PHP.

%package gmp
Summary: A module for PHP applications for using the GNU MP library
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: gmp-devel%{?_isa}
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description gmp
These functions allow you to work with arbitrary-length integers
using the GNU MP library.

%package bcmath
Summary: A module for PHP applications for using the bcmath library
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libbcmath is licensed under LGPLv2+
License: PHP and LGPLv2+
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description bcmath
The %{?scl_prefix}php-bcmath package contains a dynamic shared object that will add
support for using the bcmath library to PHP.

%package dba
Summary: A database abstraction layer module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: %{db_devel}, tokyocabinet-devel
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description dba
The %{?scl_prefix}php-dba package contains a dynamic shared object that will add
support for using the DBA database abstraction layer to PHP.

%package tidy
Summary: Standard PHP module provides tidy library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Requires: %{ns_name}-libtidy
BuildRequires: %{ns_name}-libtidy-devel

%description tidy
The %{?scl_prefix}php-tidy package contains a dynamic shared object that will add
support for using the tidy library to PHP.

%package intl
Summary: Internationalization extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%if 0%{?rhel} >= 10
Requires: libicu
BuildRequires: libicu-devel >= 50.1
%else
Requires: ea-libicu
BuildRequires: ea-libicu-devel >= 50.1
%endif

%description intl
The %{?scl_prefix}php-intl package contains a dynamic shared object that will add
support for using the ICU library to PHP.

%package enchant
Summary: Enchant spelling extension for PHP applications
# All files licensed under PHP version 3.0
License: PHP
Group: System Environment/Libraries
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
%if 0%{?rhel} >= 8
BuildRequires: enchant2-devel
Requires: enchant2
%else
BuildRequires: enchant-devel >= 1.2.4
%endif

%description enchant
The %{?scl_prefix}php-enchant package contains a dynamic shared object that will add
support for using the enchant library to PHP.

%package zip
Summary: A module for PHP applications that need to handle .zip files
Group: Development/Languages
License: PHP
Requires: ea-libzip
Requires: %{?scl_prefix}php-common = %{version}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-zip = %{version}-%{release}, %{?scl_prefix}php-zip%{?_isa} = %{version}-%{release}

%description zip
The %{?scl_prefix}php-zip package delivers a module which will allow PHP scripts
to transparently read or write ZIP compressed archives and the files
inside them.


%prep
: Building %{name}-%{version}-%{release} with systemd=%{with_systemd} sqlite3=%{with_sqlite3} tidy=%{with_tidy} zip=%{with_zip}

%setup -q -n php-%{version}

%patch42 -p1 -b .systemdpackage
%patch43 -p1 -b .phpize
%patch100 -p1 -b .cpanelmailheader
%patch102 -p1 -b .cpanelea4ini
%patch104 -p1 -b .fpmuserini
%patch105 -p1 -b .fpmjailshell
%patch106 -p1 -b .fpmepoll
%patch107 -p1 -b .systzdata
%patch402 -p1 -b .missedkill
%patch403 -p1 -b .userini
%patch404 -p1 -b .kill_all_lockers

# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE Zend/ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE

# TODO: REVISIT THIS ON RELEASE
#cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE

cp ext/bcmath/libbcmath/LICENSE libbcmath_LICENSE

# Remove the bundled version of litespeed
# and replace it with the latest version
# Note in litespeed 8.1 they changed the name of the top directory
# so I need to copy from the top dir

pushd sapi
tar -xvf %{SOURCE1} --exclude=Makefile.frag --exclude=config.m4
cp litespeed-%{litespeed_version}/* litespeed
popd

# Multiple builds for multiple SAPIs
mkdir \
build-fpm \
build-cgi

# ----- Manage known as failed test -------
# affected by systzdata patch
rm -f ext/date/tests/timezone_location_get.phpt
rm -f ext/date/tests/timezone_version_get.phpt
rm -f ext/date/tests/timezone_version_get_basic1.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt
# Should be skipped but fails sometime
rm ext/standard/tests/file/file_get_contents_error001.phpt
# cause stack exhausion
rm Zend/tests/bug54268.phpt
rm Zend/tests/bug68412.phpt

# Safety check for API version change.
# TODO: REVISIT ON RELEASE
#pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
#if test "x${pver}" != "x%{version}"; then
#   : Error: Upstream PHP version is now ${pver}, expecting %{version}.
#   : Update the version macros and rebuild.
#   exit 1
#fi

vapi=`sed -n '/#define PHP_API_VERSION/{s/.* //;p}' main/php.h`
if test "x${vapi}" != "x%{apiver}"; then
   : Error: Upstream API version is now ${vapi}, expecting %{apiver}.
   : Update the apiver macro and rebuild.
   exit 1
fi

vzend=`sed -n '/#define ZEND_MODULE_API_NO/{s/^[^0-9]*//;p;}' Zend/zend_modules.h`
if test "x${vzend}" != "x%{zendver}"; then
   : Error: Upstream Zend ABI version is now ${vzend}, expecting %{zendver}.
   : Update the zendver macro and rebuild.
   exit 1
fi

# Safety check for PDO ABI version change
vpdo=`awk '/^#define PDO_DRIVER_API/ { print $3 } ' ext/pdo/php_pdo_driver.h`
if test "x${vpdo}" != "x%{pdover}"; then
   : Error: Upstream PDO ABI version is now ${vpdo}, expecting %{pdover}.
   : Update the pdover macro and rebuild.
   exit 1
fi

# https://bugs.php.net/63362 - Not needed but installed headers.
# Drop some Windows specific headers to avoid installation,
# before build to ensure they are really not needed.
rm -f TSRM/tsrm_win32.h \
      TSRM/tsrm_config.w32.h \
      Zend/zend_config.w32.h \
      ext/mysqlnd/config-win.h \
      ext/standard/winver.h \
      main/win32_internal_function_disabled.h \
      main/win95nt.h

# Fix some bogus permissions
find . -name \*.[ch] -exec chmod 644 {} \;
chmod 644 README.*

# Create the macros.php files
sed -e "s/@PHP_APIVER@/%{apiver}%{isasuffix}/" \
    -e "s/@PHP_ZENDVER@/%{zendver}%{isasuffix}/" \
    -e "s/@PHP_PDOVER@/%{pdover}%{isasuffix}/" \
    -e "s/@PHP_VERSION@/%{version}/" \
    -e "s:@LIBDIR@:%{_libdir}:" \
    -e "s:@ETCDIR@:%{_sysconfdir}:" \
    -e "s:@INCDIR@:%{_includedir}:" \
    -e "s:@BINDIR@:%{_bindir}:" \
    -e 's/@SCL@/%{ns_name}_%{pkg}_/' \
    %{SOURCE3} | tee macros.php
# php-fpm configuration files for tmpfiles.d
# TODO echo "d /run/php-fpm 755 root root" >php-fpm.tmpfiles

# Some extensions have their own configuration file
cp %{SOURCE50} 10-opcache.ini
%ifarch x86_64
sed -e '/opcache.huge_code_pages/s/0/1/' -i 10-opcache.ini
%endif
cp %{SOURCE51} .
sed -e 's:%{_root_sysconfdir}:%{_sysconfdir}:' \
    -i 10-opcache.ini



%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-8/enable
%endif

# aclocal workaround - to be improved
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >>aclocal.m4

# Force use of system libtool:
libtoolize --force --copy
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4

# Regenerate configure scripts (patches change config.m4's)
touch configure.in

./buildconf --force

C8FLAGS=""
%if 0%{?rhel} > 7
C8FLAGS="-mshstk"
%endif

CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign $C8FLAGS"
export CFLAGS

%if 0%{?rhel} >= 9
XFLAGS=`echo "$CFLAGS" | sed 's/-flto=auto/-fno-lto/g'`
XFLAGS=`echo "$XFLAGS" | sed 's/-ffat-lto-objects//g'`
export CFLAGS="$XFLAGS"
%endif

%if 0%{?rhel} > 7
export CURL_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-brotli/%{_lib}"
%else
export SNMP_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib}"
export CURL_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-brotli/%{_lib}"
%endif

# Install extension modules in %{_libdir}/php/modules.
EXTENSION_DIR=%{_libdir}/php/modules; export EXTENSION_DIR

# Set PEAR_INSTALLDIR to ensure that the hard-coded include_path
# includes the PEAR directory even though pear is packaged
# separately.
PEAR_INSTALLDIR=%{_datadir}/pear; export PEAR_INSTALLDIR
%if 0%{?rhel} >= 8
export XLDFLAGS=$LDFLAGS
%endif

# Shell function to configure and build a PHP tree.
build() {
# Old/recent bison version seems to produce a broken parser;
# upstream uses GNU Bison 2.3. Workaround:A

mkdir Zend
cp ../Zend/zend_{language,ini}_{parser,scanner}.* Zend

# Always static:
# date, filter, libxml, reflection, spl: not supported
# hash: for PHAR_SIG_SHA256 and PHAR_SIG_SHA512
# session: dep on hash, used by soap
# pcre: used by filter, zip
# pcntl, readline: only used by CLI sapi
# openssl: for PHAR_SIG_OPENSSL
# zlib: used by image

%if 0%{?rhel} > 7
export PKG_CONFIG_PATH=/opt/cpanel/ea-php84/root/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-php84/root/usr/share/pkgconfig:/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-libxml2/%{_lib}/pkgconfig:/opt/cpanel/ea-libicu/lib/pkgconfig:/opt/cpanel/ea-oniguruma/%{_lib}/pkgconfig:/opt/cpanel/libargon2/lib64/pkgconfig:/usr/lib64/pkgconfig:/usr/lib64/pkgconfig:/opt/cpanel/libargon2/lib64/pkgconfig
%else
export PKG_CONFIG_PATH=/opt/cpanel/ea-php84/root/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-php84/root/usr/share/pkgconfig:/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-openssl11/lib/pkgconfig:/opt/cpanel/ea-libxml2/%{_lib}/pkgconfig:/opt/cpanel/ea-libicu/lib/pkgconfig:/opt/cpanel/ea-oniguruma/%{_lib}/pkgconfig:/opt/cpanel/libargon2/lib64/pkgconfig:/usr/lib64/pkgconfig:/usr/lib64/pkgconfig:/opt/cpanel/libargon2/lib64/pkgconfig
%endif

export LIBXML_CFLAGS=-I/opt/cpanel/ea-libxml2/include/libxml2
export LIBXML_LIBS="-L/opt/cpanel/ea-libxml2/%{_lib} -lxml2"
export XSL_CFLAGS=-I/opt/cpanel/ea-libxml2/include/libxml2
export XSL_LIBS="-L/opt/cpanel/ea-libxml2/%{_lib} -lxml2"
%if 0%{?rhel} < 8
export CURL_CFLAGS=-I/opt/cpanel/libcurl/include
export CURL_LIBS="-L/opt/cpanel/libcurl/%{_lib} -lcurl"
%endif
export JPEG_CFLAGS=-I/usr/include
export JPEG_LIBS="-L/usr/%{_lib} -ljpeg"
export KERBEROS_CFLAGS=-I/usr/include
export KERBEROS_LIBS=-L/usr/%{_lib}
export SASL_CFLAGS=-I/usr/include
export SASL_LIBS=-L/usr/%{_lib}

%if 0%{?rhel} < 8
export OPENSSL_CFLAGS=-I/opt/cpanel/ea-openssl11/include
export OPENSSL_LIBS="-L/opt/cpanel/ea-openssl11/lib -lssl -lcrypto -lresolv"
%endif

export SYSTEMD_LIBS=-lsystemd

export LIBZIP_CFLAGS=-I/opt/cpanel/ea-libzip/include
export LIBZIP_LIBS="-L/opt/cpanel/ea-libzip/lib64 -lzip"

%if 0%{?rhel} >= 8
export LDFLAGS="$XLDFLAGS -Wl,-rpath,/opt/cpanel/ea-libzip/lib64 -Wl,-rpath-link,/lib64 -Wl,-rpath,/lib64"
%else
export LDFLAGS="-Wl,-rpath=/opt/cpanel/ea-brotli/lib"
%endif

export LDFLAGS="$LDFLAGS -Wl,-rpath,/opt/cpanel/libargon2/lib64 -L/opt/cpanel/libargon2/lib64 -largon2"
export ARGON2_CFLAGS=-I/opt/cpanel/libargon2/include

ln -sf ../configure
%configure \
    --cache-file=../config.cache \
    --with-libdir=%{_lib} \
    --with-config-file-path=%{_sysconfdir} \
    --with-config-file-scan-dir=%{_sysconfdir}/php.d \
    --disable-debug \
    --with-password-argon2=/opt/cpanel/libargon2 \
    --with-pic \
    --without-pear \
    --with-bz2 \
    --with-freetype \
    --with-xpm \
    --without-gdbm \
    --with-gettext \
    --with-iconv \
    --with-jpeg \
    --with-openssl=/opt/cpanel/ea-openssl11/lib \
%if %{with_pcre}
    --with-pcre-regex=%{_root_prefix} \
%endif
    --with-zlib \
    --with-layout=GNU \
    --enable-exif \
    --enable-ftp \
    --enable-sockets \
    --with-kerberos \
    --enable-shmop \
    --with-sodium=shared \
    --with-libxml \
    --with-system-tzdata \
    --with-mhash \
    $*
if test $? != 0; then
  tail -500 config.log
  : configure failed
  exit 1
fi

%if 0%{?rhel} >= 9
sed -i 's/-flto=auto/-fno-lto/' Makefile
sed -i 's/-ffat-lto-objects//' Makefile
%endif

# ZC-10931 - we are building libc-client in, but statically.  This allows us to deprecate and remove
# scl-libc-client, instead we have a build require for ea-libc-client
# There is no way I could find in the configure scripts to build against libc-client statically
# So I hit it with a hammer
sed -i 's/-lc-client/-l:c-client.a -lkrb5 -lgssapi_krb5 -lkrb5 -lgssapi_krb5/g' scripts/php-config Makefile

make %{?_smp_mflags}
}

# Build /usr/bin/php-cgi with the CGI SAPI, and most the shared extensions
pushd build-cgi

build --libdir=%{_libdir}/php \
      --enable-pcntl \
      --enable-opcache \
      --enable-phpdbg \
      --enable-mbstring=shared \
      --enable-litespeed \
      --with-webp \
%if %{with_avif}
      --with-avif \
%endif
      --enable-gd=shared \
      --with-gmp=shared \
      --enable-calendar=shared \
      --enable-bcmath=shared \
      --with-bz2=shared \
      --enable-ctype=shared \
      --enable-dba=shared --with-db4=%{_root_prefix} \
                          --with-tcadb=%{_root_prefix} \
      --enable-exif=shared \
      --enable-ftp=shared \
      --with-gettext=shared \
      --with-iconv=shared \
      --enable-sockets=shared \
      --enable-tokenizer=shared \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-simplexml=shared \
      --enable-xml=shared \
      --with-snmp=shared,%{_root_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_root_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
%if 0%{?rhel} >= 8
      --with-curl=shared \
%else
      --with-curl=shared,%{libcurl_prefix} \
%endif
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_root_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_root_prefix} \
      --with-pdo-sqlite=shared,%{_root_prefix} \
      --with-sqlite3=shared,%{_root_prefix} \
      --enable-json=shared \
      --with-zip=shared \
      --without-readline \
      --with-libedit \
      --enable-phar=shared \
      --with-tidy=shared,%{libtidy_prefix} \
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-shmop=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_root_prefix} \
      --enable-intl=shared \
      --with-enchant=shared,%{_root_prefix} \
      --enable-fileinfo=shared
popd

without_shared="--disable-gd \
      --disable-dom --disable-dba --without-unixODBC \
      --disable-opcache \
      --disable-xmlreader --disable-xmlwriter \
      --without-sqlite3 --disable-phar --disable-fileinfo \
      --disable-json \
      --without-curl --disable-posix --disable-xml \
      --disable-simplexml --disable-exif --without-gettext \
      --without-iconv --disable-ftp --without-bz2 --disable-ctype \
      --disable-shmop --disable-sockets --disable-tokenizer \
      --disable-sysvmsg --disable-sysvshm --disable-sysvsem \
      --without-gmp --disable-calendar"

# Build php-fpm
pushd build-fpm
build --enable-fpm \
      --with-fpm-systemd \
      --libdir=%{_libdir}/php \
      --without-mysqli \
      --disable-pdo \
      --enable-pcntl \
      ${without_shared}
popd

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Make the eaphp## symlinks
install -d $RPM_BUILD_ROOT/usr/local/bin
ln -sf /opt/cpanel/ea-php84/root/usr/bin/php $RPM_BUILD_ROOT/usr/local/bin/ea-php84
install -d $RPM_BUILD_ROOT/usr/bin
ln -sf /opt/cpanel/ea-php84/root/usr/bin/php-cgi $RPM_BUILD_ROOT/usr/bin/ea-php84

make -C build-fpm install-fpm \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# Install everything from the CGI SAPI build
make -C build-cgi install \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# Install the default configuration file and icons
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/php.ini

# For third-party packaging:
install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/php

install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib

install -m 755 build-cgi/sapi/litespeed/lsphp $RPM_BUILD_ROOT%{_bindir}/lsphp

# PHP-FPM stuff
# Log

# we need to do the following to compensate for the way
# EA4 on OBS was built rather than EA4-Opensuse

install -d $RPM_BUILD_ROOT/opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm
install -d $RPM_BUILD_ROOT/opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm

ln -sf /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm $RPM_BUILD_ROOT%{_localstatedir}/log/php-fpm
ln -sf /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm $RPM_BUILD_ROOT%{_localstatedir}/run/php-fpm

# Config
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -e 's:/etc:%{_sysconfdir}:' \
    -i $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf
sed -e 's:/var/lib:%{_localstatedir}/lib:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -i $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf
mv $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf.example
mv $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf.default .
# tmpfiles.d
# install -m 755 -d $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d
# install -m 644 php-fpm.tmpfiles $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/php-fpm.conf
# install systemd unit files and scripts for handling server startup
install -m 755 -d $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_unitdir}/%{?scl_prefix}php-fpm.service
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/etc:%{_sysconfdir}:' \
    -e 's:/usr/sbin:%{_sbindir}:' \
    -i $RPM_BUILD_ROOT%{_unitdir}/%{?scl_prefix}php-fpm.service

# LogRotate
install -m 755 -d $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -i $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
# Environment file
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/php-fpm


# make the cli commands available in standard root for SCL build
%if 0%{?scl:1}
#install -m 755 -d $RPM_BUILD_ROOT%{_root_bindir}
#ln -s %{_bindir}/php       $RPM_BUILD_ROOT%{_root_bindir}/%{?scl_prefix}php
#ln -s %{_bindir}/phar.phar $RPM_BUILD_ROOT%{_root_bindir}/%{?scl_prefix}phar
%endif

# Generate files lists and stub .ini files for each subpackage

for mod in pgsql odbc ldap snmp \
    mysqlnd mysqli pdo_mysql \
    mbstring gd dom xsl soap bcmath dba xmlreader xmlwriter \
    simplexml bz2 calendar ctype exif ftp gettext gmp iconv \
    sockets tokenizer opcache \
    pdo pdo_pgsql pdo_odbc \
    pdo_sqlite sqlite3 \
    enchant \
    phar fileinfo \
    intl \
    zip \
    tidy \
    sodium \
    curl xml \
    posix shmop sysvshm sysvsem sysvmsg
do
    # for extension load order
    case $mod in
      opcache)
        # Zend extensions
        ini=10-${mod}.ini;;
      pdo_*|mysqli|xmlreader)
        # Extensions with dependencies on 20-*
        ini=30-${mod}.ini;;
      *)
        # Extensions with no dependency
        ini=20-${mod}.ini;;
    esac
    # Some extensions have their own config file
    #
    # NOTE: rpmlint complains about the spec file using %{_sourcedir} macro.
    #       However, our usage acceptable given the transient nature of the ini files.
    #       https://fedoraproject.org/wiki/Packaging:RPM_Source_Dir?rd=PackagingDrafts/RPM_Source_Dir
    if [ -f %{_sourcedir}/$ini ]; then
      cp -p %{_sourcedir}/$ini %{buildroot}%{_sysconfdir}/php.d/$ini
    else
      cat > %{buildroot}%{_sysconfdir}/php.d/$ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
    fi
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/php/modules/${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php.d/${ini}
EOF
done

# The dom, xsl and xml* modules are all packaged in php-xml
cat files.dom files.xsl files.xml{reader,writer} \
    files.simplexml >> files.xml

# mysqlnd
cat files.mysqli \
    files.pdo_mysql \
    >> files.mysqlnd

# Split out the PDO modules
cat files.pdo_pgsql >> files.pgsql
cat files.pdo_odbc >> files.odbc

# sysv* packaged in php-process
cat files.shmop files.sysv* > files.process

cat files.pdo_sqlite >> files.pdo
cat files.sqlite3 >> files.pdo
# Package json and phar in -common.
cat files.phar \
    files.ctype \
    files.tokenizer > files.common

# The default Zend OPcache blacklist file
install -m 644 %{SOURCE51} $RPM_BUILD_ROOT%{_sysconfdir}/php.d/opcache-default.blacklist

# Install the macros file:
install -d $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm
install -m 644 -c macros.php \
           $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm/macros.%{name}

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{_libdir}/php/modules/*.a \
       $RPM_BUILD_ROOT%{_bindir}/{phptar} \
       $RPM_BUILD_ROOT%{_datadir}/pear \
       $RPM_BUILD_ROOT%{_libdir}/libphp8.la

# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

echo "FINAL FILE LIST"
find . -type f -print | sort

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
rm files.* macros.*

%post fpm
%if 0%{?systemd_post:1}
%systemd_post %{?scl_prefix}php-fpm.service
%else
if [ $1 = 1 ]; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%endif

%preun fpm
%if 0%{?systemd_preun:1}
%systemd_preun %{?scl_prefix}php-fpm.service
%else
if [ $1 = 0 ]; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
    /bin/systemctl stop %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
fi
%endif

%postun fpm
%if 0%{?systemd_postun_with_restart:1}
%systemd_postun_with_restart %{?scl_prefix}php-fpm.service
%else
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
fi
%endif

# Handle upgrading from SysV initscript to native systemd unit.
# We can tell if a SysV version of php-fpm was previously installed by
# checking to see if the initscript is present.
%triggerun fpm -- %{?scl_prefix}php-fpm
if [ -f /etc/rc.d/init.d/%{?scl_prefix}php-fpm ]; then
    # Save the current service runlevel info
    # User must manually run systemd-sysv-convert --apply php-fpm
    # to migrate them to systemd targets
    /usr/bin/systemd-sysv-convert --save %{?scl_prefix}php-fpm >/dev/null 2>&1 || :

    # Run these because the SysV package being removed won't do them
    /sbin/chkconfig --del %{?scl_prefix}php-fpm >/dev/null 2>&1 || :
    /bin/systemctl try-restart %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
fi

%{!?_licensedir:%global license %%doc}

%files
%defattr(-,root,root)

%files common -f files.common
%defattr(-,root,root)
%doc CODING_STANDARDS.md EXTENSIONS LICENSE NEWS README*
%doc Zend/ZEND_* TSRM_LICENSE
# TODO: REVISIT THIS ON RELEASE
#%doc libmagic_LICENSE
%doc php.ini-*
%config(noreplace) %{_sysconfdir}/php.ini
%dir %{_sysconfdir}/php.d
%dir %{_libdir}/php
%dir %{_libdir}/php/modules
%dir %{_localstatedir}/lib
%dir %{_datadir}/php

%files sodium
%defattr(-, root, root)
%{_libdir}/php/modules/sodium.so
%config(noreplace) %{_sysconfdir}/php.d/20-sodium.ini

%files cli
%defattr(-,root,root)
%{_bindir}/php
# Add the ea-php## symlinks
/usr/bin/%{ns_name}-%{pkg}
/usr/local/bin/%{ns_name}-%{pkg}
%{_bindir}/php-cgi
%{_bindir}/phar.phar
%{_bindir}/phar
# provides phpize here (not in -devel) for pecl command
%{_bindir}/phpize
%{_mandir}/man1/php.1*
%{_mandir}/man1/php-cgi.1*
%{_mandir}/man1/phar.1*
%{_mandir}/man1/phar.phar.1*
%{_mandir}/man1/phpize.1*

#{?scl: %{_root_bindir}/%{?scl_prefix}php}
#{?scl: %{_root_bindir}/%{?scl_prefix}phar}

%files dbg
%defattr(-,root,root)
%{_bindir}/phpdbg
%{_mandir}/man1/phpdbg.1*
%doc sapi/phpdbg/CREDITS

%files fpm
%defattr(-,root,root)
# we need to do the following to compensate for the way
# EA4 on OBS was built rather than EA4-Opensuse
%dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm
%dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm
#%attr(770,nobody,root) %dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm
#%attr(711,root,root) %dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm
%doc php-fpm.conf.default
%license fpm_LICENSE
%config(noreplace) %{_sysconfdir}/php-fpm.conf
%config(noreplace) %{_sysconfdir}/php-fpm.d/www.conf.example
%config(noreplace) %{_sysconfdir}/php-fpm.d/www.conf.default
%config(noreplace) %{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
%config(noreplace) %{_sysconfdir}/sysconfig/php-fpm
# %{_prefix}/lib/tmpfiles.d/php-fpm.conf
%{_unitdir}/%{?scl_prefix}php-fpm.service
%{_sbindir}/php-fpm
%attr(0710,root,root) %dir %{_sysconfdir}/php-fpm.d
# log owned by nobody for log
#%attr(770,nobody,root) %{_localstatedir}/log/php-fpm
#%attr(711,root,root) %{_localstatedir}/run/php-fpm
%{_localstatedir}/log/php-fpm
%{_localstatedir}/run/php-fpm
%{_mandir}/man8/php-fpm.8*
%dir %{_datadir}/fpm
%{_datadir}/fpm/status.html
%dir %{_sysconfdir}/sysconfig
%dir %{_mandir}/man8
%dir %{_localstatedir}/log
%dir %{_localstatedir}/run

%files litespeed
%defattr(-,root,root,-)
%{_bindir}/lsphp

%files devel
%defattr(-,root,root,-)
%{_bindir}/php-config
%{_includedir}/php
%{_libdir}/php/build
%{_mandir}/man1/php-config.1*
%{_root_sysconfdir}/rpm/macros.%{name}

%files bz2 -f files.bz2
%files calendar -f files.calendar
%files curl -f files.curl
%files exif -f files.exif
%files fileinfo -f files.fileinfo
%files ftp -f files.ftp
%files gettext -f files.gettext
%files iconv -f files.iconv
%files sockets -f files.sockets
%files posix -f files.posix
%files pgsql -f files.pgsql
%files odbc -f files.odbc
%files ldap -f files.ldap
%files snmp -f files.snmp
%files xml -f files.xml
%files mbstring -f files.mbstring
%defattr(-,root,root,-)
%doc libmbfl_LICENSE
%files gd -f files.gd
%defattr(-,root,root,-)
%files soap -f files.soap
%files bcmath -f files.bcmath
%defattr(-,root,root,-)
%license libbcmath_LICENSE
%files gmp -f files.gmp
%files dba -f files.dba
%files pdo -f files.pdo
%files tidy -f files.tidy
%files intl -f files.intl
%files process -f files.process
%files enchant -f files.enchant
%files mysqlnd -f files.mysqlnd
%files opcache -f files.opcache
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/php.d/opcache-default.blacklist
%files zip -f files.zip

%changelog
* Thu Jul 03 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.10-1
- EA-12995: Update ea-php84 from v8.4.8 to v8.4.10
- Fixed GHSA-hrwm-9436-5mv3 (pgsql extension does not check for errors during escaping). (CVE-2025-1735)
- Fixed GHSA-453j-q27h-5p8x (NULL Pointer Dereference in PHP SOAP Extension via Large XML Namespace Prefix). (CVE-2025-6491)
- Fixed GHSA-3cr5-j632-f35r (Null byte termination in hostnames). (CVE-2025-1220)


* Thu Jun 05 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.8-1
- EA-12918: Update ea-php84 from v8.4.7 to v8.4.8

* Thu May 08 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.7-1
- EA-12851: Update ea-php84 from v8.4.6 to v8.4.7

* Thu Apr 10 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.6-1
- EA-12808: Update ea-php84 from v8.4.5 to v8.4.6

* Thu Mar 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.5-1
- EA-12768: Update ea-php84 from v8.4.4 to v8.4.5
    - Fixed GHSA-hgf54-96fm-v528 (Stream HTTP wrapper header check might omit basic auth header). (CVE-2025-1736)
    - Fixed GHSA-52jp-hrpf-2jff (Stream HTTP wrapper truncate redirect location to 1024 bytes). (CVE-2025-1861)
    - Fixed GHSA-pcmh-g36c-qc44 (Streams HTTP wrapper does not fail for headers without colon). (CVE-2025-1734)
    - Fixed GHSA-v8xr-gpvj-cx9g (Header parser of `http` stream wrapper does not handle folded headers). (CVE-2025-1217)
    - Fixed GHSA-p3x9-6h7p-cgfc (libxml streams use wrong `content-type` header when requesting a redirected resource). (CVE-2025-1219)
    - Fixed GHSA-rwp7-7vc6-8477 (Reference counting in php_request_shutdown causes Use-After-Free). (CVE-2024-11235)

* Thu Feb 13 2025 Cory McIntire <cory.mcintire@webpros.com> - 8.4.4-1
- EA-12709: Update ea-php84 from v8.4.3 to v8.4.4

* Fri Jan 17 2025 Cory McIntire <cory@cpanel.net> - 8.4.3-1
- EA-12652: Update ea-php84 from v8.4.2 to v8.4.3

* Thu Dec 19 2024 Cory McIntire <cory@cpanel.net> - 8.4.2-1
- EA-12619: Update ea-php84 from v8.4.1 to v8.4.2

* Thu Nov 21 2024 Dan Muey <daniel.muey@webpros.com> - 8.4.1-1
- EA-12579: Update ea-php84 from v8.4.0 to v8.4.1

* Fri Oct 04 2024 Julian Brown <julian.brown@cpanel.net> - 8.4.0-1
- ZC-12235: First build


# Define if it's a locaweb package
%bcond_with locaweb

# Build a static package
%bcond_with static

%if %{with static}
# Package suffix
%global _suffix 54
%endif

# API/ABI check
%global apiver      20100412
%global zendver     20100525
%global pdover      20080721
# Extension version
%global fileinfover 1.0.5
%global pharver     2.0.1
%global zipver      1.11.0
%global jsonver     1.2.1

# version used for php embedded library soname
%global embed_version 5.4

%global mysql_sock %(mysql_config --socket 2>/dev/null || echo /var/lib/mysql/mysql.sock)

# Build for LiteSpeed Web Server (LSAPI)
%global with_lsws 1

# Regression tests take a long time, you can skip 'em with this
%{!?runselftest: %{expand: %%global runselftest 1}}

# Use the arch-specific mysql_config binary to avoid mismatch with the
# arch detection heuristic used by bindir/mysql_config.
%global mysql_config %{_bindir}/mysql_config

%global with_fpm 1

# /usr/sbin/apsx with httpd < 2.4 and defined as /usr/bin/apxs with httpd >= 2.4
%{!?_httpd_apxs:       %{expand: %%global _httpd_apxs       %%{_sbindir}/apxs}}
%{!?_httpd_mmn:        %{expand: %%global _httpd_mmn        %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}}
%{!?_httpd_confdir:    %{expand: %%global _httpd_confdir    %%{_sysconfdir}/httpd/conf.d}}
# /etc/httpd/conf.d with httpd < 2.4 and defined as /etc/httpd/conf.modules.d with httpd >= 2.4
%{!?_httpd_modconfdir: %{expand: %%global _httpd_modconfdir %%{_sysconfdir}/httpd/conf.d}}
%{!?_httpd_moddir:     %{expand: %%global _httpd_moddir     %%{_libdir}/httpd/modules}}
%{!?_httpd_contentdir: %{expand: %%global _httpd_contentdir /var/www}}

%if %{with locaweb}
%global _httpd_user webserver
%else
%global _httpd_user apache
%endif

%global macrosdir %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_sysconfdir}/rpm; echo $d)

%if 0%{?rhel} < 7
%global with_libzip  0
%else
%global with_libzip  1
%endif
%global with_zip     1
%global zipmod       zip

%if 0%{?rhel} < 7
%global db_devel  db4-devel
%else
%global db_devel  libdb-devel
%endif

Summary: PHP scripting language for creating dynamic web sites
Name: php%{?_suffix}
Version: 5.4.34
%if %{with locaweb}
Release: 1.lw
%else
Release: 1%{?dist}
%endif
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM is licensed under BSD
License: PHP and Zend and BSD
Group: Development/Languages
URL: http://www.php.net/

Source0: http://www.php.net/distributions/php-%{version}.tar.bz2
Source1: php54.conf
Source2: php54.ini
Source3: macros54.php
Source4: php54-fpm.conf
Source5: php54-fpm-www.conf
#Source6: php54-fpm.service
Source7: php54-fpm.logrotate
Source8: php54-fpm.sysconfig
Source9: php54.modconf
Source99: php54-fpm.init

# Build fixes
Patch5: php-5.2.0-includedir.patch
Patch6: php-5.2.4-embed.patch
Patch7: php-5.3.0-recode.patch
Patch8: php-5.4.7-libdb.patch

# Fixes for extension modules
# https://bugs.php.net/63171 no odbc call during timeout
Patch21: php-5.4.7-odbctimer.patch

# Functional changes
Patch40: php-5.4.0-dlopen.patch
Patch41: php-5.4.0-easter.patch
Patch42: php-5.3.1-systzdata-v10.patch
# See http://bugs.php.net/53436
Patch43: php-5.4.0-phpize.patch
# Use system libzip instead of bundled one
Patch44: php-5.4.15-system-libzip.patch
# Use -lldap_r for OpenLDAP
Patch45: php-5.4.8-ldap_r.patch
# Make php_config.h constant across builds
Patch46: php-5.4.9-fixheader.patch
# drop "Configure command" from phpinfo output
Patch47: php-5.4.9-phpinfo.patch

# Upstream fixes
# Backported from 5.5.18 for https://bugs.php.net/65641
Patch100: php-5.4.33-bug65641.patch

# Locaweb static patch
Patch212: php54-locaweb-static.patch

# Fixes for tests
# see https://bugzilla.redhat.com/971416
Patch302: php-5.4.30-noNO.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: bzip2-devel, curl-devel >= 7.9, gmp-devel
BuildRequires: httpd-devel >= 2.0.46-1, pam-devel
BuildRequires: libstdc++-devel, openssl-devel
%if 0%{?rhel} >= 6
# For Sqlite3 extension
BuildRequires: sqlite-devel >= 3.6.0
%else
BuildRequires: sqlite-devel >= 3.0.0
%endif
BuildRequires: zlib-devel, smtpdaemon, libedit-devel
%if 0%{?rhel} >= 7
BuildRequires: pcre-devel >= 8.10
%else
BuildRequires: pcre-devel >= 6.6
%endif
BuildRequires: bzip2, perl, libtool >= 1.4.3, gcc-c++
BuildRequires: libtool-ltdl-devel
%if %{with_libzip}
BuildRequires: libzip-devel >= 0.10
%endif
Provides: %{name}-zts = %{version}-%{release}
Requires: httpd-mmn = %{_httpd_mmn}
Provides: mod_php = %{version}-%{release}
Requires: %{name}-common = %{version}-%{release}
# For backwards-compatibility, require php-cli for the time being:
Requires: %{name}-cli = %{version}-%{release}
# To ensure correct /var/lib/php/session ownership:
Requires(pre): httpd

# Don't provides extensions, which are not shared library, as .so
%{?filter_provides_in: %filter_provides_in %{_libdir}/php%{?_suffix}/modules/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{_libdir}/php%{?_suffix}-zts/modules/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{_httpd_moddir}/.*\.so$}
%{?filter_setup}

%description
PHP is an HTML-embedded scripting language. PHP attempts to make it
easy for developers to write dynamically generated web pages. PHP also
offers built-in database integration for several commercial and
non-commercial database management systems, so writing a
database-enabled webpage with PHP is fairly simple. The most common
use of PHP coding is probably as a replacement for CGI scripts.

The php package contains the module (often referred to as mod_php)
which adds support for the PHP language to Apache HTTP Server.

%package cli
Group: Development/Languages
Summary: Command-line interface for PHP
Requires: %{name}-common = %{version}-%{release}
Provides: php-cgi = %{version}-%{release}, php-cli = %{version}-%{release}
Provides: php-pcntl
Provides: php-readline

%description cli
The php-cli package contains the command-line interface
executing PHP scripts, /usr/bin/php, and the CGI interface.

%if %{with_fpm}
%package fpm
Group: Development/Languages
Summary: PHP FastCGI Process Manager
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM and fpm are licensed under BSD
License: PHP and Zend and BSD
Requires: %{name}-common = %{version}-%{release}
Requires(pre): /usr/sbin/useradd
# This is for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts

%description fpm
PHP-FPM (FastCGI Process Manager) is an alternative PHP FastCGI
implementation with some additional features useful for sites of
any size, especially busier sites.
%endif

%if %{with_lsws}
%package litespeed
Summary: LiteSpeed Web Server PHP support
Group: Development/Languages
Requires: %{name}-common = %{version}-%{release}

%description litespeed
The php-litespeed package provides the %{_bindir}/lsphp command
used by the LiteSpeed Web Server (LSAPI enabled PHP).
%endif

%package common
Group: Development/Languages
Summary: Common files for PHP
# All files licensed under PHP version 3.01, except
# fileinfo is licensed under PHP version 3.0
# regex, libmagic are licensed under BSD
# main/snprintf.c, main/spprintf.c and main/rfc1867.c are ASL 1.0
License: PHP and BSD and ASL 1.0
# ABI/API check - Arch specific
Provides: php-api = %{apiver}, php-zend-abi = %{zendver}
Provides: php(api) = %{apiver}, php(zend-abi) = %{zendver}
Provides: php(language) = %{version}
# Provides for all builtin/shared modules:
Provides: php-bz2
Provides: php-calendar
Provides: php-core = %{version}
Provides: php-ctype
Provides: php-curl
Provides: php-date
Provides: php-ereg
Provides: php-exif
Provides: php-fileinfo
Provides: php-pecl-Fileinfo = %{fileinfover}
Provides: php-pecl(Fileinfo) = %{fileinfover}
Provides: php-filter
Provides: php-ftp
Provides: php-gettext
Provides: php-gmp
Provides: php-hash
Provides: php-mhash = %{version}
Provides: php-iconv
Provides: php-json
Provides: php-pecl-json = %{jsonver}
Provides: php-pecl(json) = %{jsonver}
Provides: php-libxml
Provides: php-openssl
Provides: php-pecl-phar = %{pharver}
Provides: php-pecl(phar) = %{pharver}
Provides: php-phar
Provides: php-pcre
Provides: php-reflection
Provides: php-session
Provides: php-shmop
Provides: php-simplexml
Provides: php-sockets
Provides: php-spl
Provides: php-standard = %{version}
Provides: php-tokenizer
%if %{with_zip}
Provides: php-zip
Provides: php-pecl-zip = %{zipver}
Provides: php-pecl(zip) = %{zipver}
%endif
Provides: php-zlib

%description common
The php-common package contains files used by both the php
package and the php-cli package.

%package devel
Group: Development/Libraries
Summary: Files needed for building PHP extensions
Requires: %{name}-cli = %{version}-%{release}, autoconf, automake
%if 0%{?rhel} >= 7
Requires: pcre-devel
%endif
Provides: %{name}-zts-devel = %{version}-%{release}

%description devel
The php-devel package contains the files needed for building PHP
extensions. If you need to compile your own PHP extensions, you will
need to install this package.

%package imap
Summary: A module for PHP applications that use IMAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: krb5-devel, openssl-devel, libc-client-devel

%description imap
The php-imap package contains a dynamic shared object (DSO) for the
Apache Web server. When compiled into Apache, the php-imap module will
add IMAP (Internet Message Access Protocol) support to PHP. IMAP is a
protocol for retrieving and uploading e-mail messages on mail
servers. PHP is an HTML-embedded scripting language. If you need IMAP
support for PHP applications, you will need to install this package
and the php package.

%package ldap
Summary: A module for PHP applications that use LDAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: cyrus-sasl-devel, openldap-devel, openssl-devel

%description ldap
The php-ldap package is a dynamic shared object (DSO) for the Apache
Web server that adds Lightweight Directory Access Protocol (LDAP)
support to PHP. LDAP is a set of protocols for accessing directory
services over the Internet. PHP is an HTML-embedded scripting
language. If you need LDAP support for PHP applications, you will
need to install this package in addition to the php package.

%package pdo
Summary: A database access abstraction module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
# ABI/API check - Arch specific
Provides: php-pdo-abi = %{pdover}
Provides: php(pdo-abi) = %{pdover}
Provides: php-sqlite3
Provides: php-pdo_sqlite

%description pdo
The php-pdo package contains a dynamic shared object that will add
a database access abstraction layer to PHP.  This module provides
a common interface for accessing MySQL, PostgreSQL or other
databases.

%package mysql
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-pdo = %{version}-%{release}
Provides: php_database
Provides: php-mysqli = %{version}-%{release}
Provides: php-pdo_mysql
Conflicts: %{name}-mysqlnd
%if %{with locaweb}
BuildRequires: Percona-Server-devel-51
%else
BuildRequires: mysql-devel >= 4.1.0
%endif

%description mysql
The php-mysql package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.

%package mysqlnd
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-pdo = %{version}-%{release}
Provides: php_database
Provides: php-mysql = %{version}-%{release}
Provides: php-mysqli = %{version}-%{release}
Provides: php-pdo_mysql

%description mysqlnd
The php-mysqlnd package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.

This package use the MySQL Native Driver

%package pgsql
Summary: A PostgreSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-pdo = %{version}-%{release}
Provides: php_database
Provides: php-pdo_pgsql
BuildRequires: krb5-devel, openssl-devel, postgresql-devel

%description pgsql
The php-pgsql package includes a dynamic shared object (DSO) that can
be compiled in to the Apache Web server to add PostgreSQL database
support to PHP. PostgreSQL is an object-relational database management
system that supports almost all SQL constructs. PHP is an
HTML-embedded scripting language. If you need back-end support for
PostgreSQL, you should install this package in addition to the main
php package.

%package process
Summary: Modules for PHP script using system process interfaces
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
Provides: php-posix
Provides: php-sysvsem
Provides: php-sysvshm
Provides: php-sysvmsg

%description process
The php-process package contains dynamic shared objects which add
support to PHP using system interfaces for inter-process
communication.

%package odbc
Summary: A module for PHP applications that use ODBC databases
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# pdo_odbc is licensed under PHP version 3.0
License: PHP
Requires: %{name}-pdo = %{version}-%{release}
Provides: php_database
Provides: php-pdo_odbc
BuildRequires: unixODBC-devel

%description odbc
The php-odbc package contains a dynamic shared object that will add
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
Requires: %{name}-common = %{version}-%{release}
BuildRequires: libxml2-devel

%description soap
The php-soap package contains a dynamic shared object that will add
support to PHP for using the SOAP web services protocol.

%package interbase
Summary: A module for PHP applications that use Interbase/Firebird databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: firebird-devel
Requires: %{name}-pdo = %{version}-%{release}
Provides: php_database
Provides: php-firebird
Provides: php-pdo_firebird

%description interbase
The php-interbase package contains a dynamic shared object that will add
database support through Interbase/Firebird to PHP.

InterBase is the name of the closed-source variant of this RDBMS that was
developed by Borland/Inprise.

Firebird is a commercially independent project of C and C++ programmers,
technical advisors and supporters developing and enhancing a multi-platform
relational database management system based on the source code released by
Inprise Corp (now known as Borland Software Corp) under the InterBase Public
License.

%package snmp
Summary: A module for PHP applications that query SNMP-managed devices
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}, net-snmp
BuildRequires: net-snmp-devel

%description snmp
The php-snmp package contains a dynamic shared object that will add
support for querying SNMP devices to PHP.  PHP is an HTML-embeddable
scripting language. If you need SNMP support for PHP applications, you
will need to install this package and the php package.

%package xml
Summary: A module for PHP applications which use XML
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
Provides: php-dom
Provides: php-xsl
Provides: php-domxml
Provides: php-wddx
Provides: php-xmlreader
Provides: php-xmlwriter
BuildRequires: libxslt-devel >= 1.0.18-1, libxml2-devel >= 2.4.14-1

%description xml
The php-xml package contains dynamic shared objects which add support
to PHP for manipulating XML documents using the DOM tree,
and performing XSL transformations on XML documents.

%package xmlrpc
Summary: A module for PHP applications which use the XML-RPC protocol
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libXMLRPC is licensed under BSD
License: PHP and BSD
Requires: %{name}-common = %{version}-%{release}

%description xmlrpc
The php-xmlrpc package contains a dynamic shared object that will add
support for the XML-RPC protocol to PHP.

%package mbstring
Summary: A module for PHP applications which need multi-byte string handling
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libmbfl is licensed under LGPLv2
# onigurama is licensed under BSD
# ucgendat is licensed under OpenLDAP
License: PHP and LGPLv2 and BSD and OpenLDAP
Requires: %{name}-common = %{version}-%{release}

%description mbstring
The php-mbstring package contains a dynamic shared object that will add
support for multi-byte string handling to PHP.

%package gd
Summary: A module for PHP applications for using the gd graphics library
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libgd is licensed under BSD
License: PHP and BSD
Requires: %{name}-common = %{version}-%{release}
# Required to build the bundled GD library
BuildRequires: libjpeg-devel, libpng-devel, freetype-devel
BuildRequires: libXpm-devel, t1lib-devel

%description gd
The php-gd package contains a dynamic shared object that will add
support for using the gd graphics library to PHP.

%package bcmath
Summary: A module for PHP applications for using the bcmath library
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libbcmath is licensed under LGPLv2+
License: PHP and LGPLv2+
Requires: %{name}-common = %{version}-%{release}

%description bcmath
The php-bcmath package contains a dynamic shared object that will add
support for using the bcmath library to PHP.

%package dba
Summary: A database abstraction layer module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: %{db_devel}, gdbm-devel, tokyocabinet-devel
Requires: %{name}-common = %{version}-%{release}

%description dba
The php-dba package contains a dynamic shared object that will add
support for using the DBA database abstraction layer to PHP.

%package mcrypt
Summary: Standard PHP module provides mcrypt library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: libmcrypt-devel

%description mcrypt
The php-mcrypt package contains a dynamic shared object that will add
support for using the mcrypt library to PHP.

%package tidy
Summary: Standard PHP module provides tidy library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: libtidy-devel

%description tidy
The php-tidy package contains a dynamic shared object that will add
support for using the tidy library to PHP.

%package mssql
Summary: MSSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-pdo = %{version}-%{release}
Provides: php-pdo_dblib
BuildRequires: freetds-devel

%description mssql
The php-mssql package contains a dynamic shared object that will
add MSSQL database support to PHP.  It uses the TDS (Tabular
DataStream) protocol through the freetds library, hence any
database server which supports TDS can be accessed.

%package embedded
Summary: PHP library for embedding in applications
Group: System Environment/Libraries
Requires: %{name}-common = %{version}-%{release}
# doing a real -devel package for just the .so symlink is a bit overkill
Provides: php-embedded-devel = %{version}-%{release}

%description embedded
The php-embedded package contains a library which can be embedded
into applications to provide PHP scripting language support.

%package pspell
Summary: A module for PHP applications for using pspell interfaces
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: aspell-devel >= 0.50.0

%description pspell
The php-pspell package contains a dynamic shared object that will add
support for using the pspell library to PHP.

%package recode
Summary: A module for PHP applications for using the recode library
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: recode-devel

%description recode
The php-recode package contains a dynamic shared object that will add
support for using the recode library to PHP.

%package intl
Summary: Internationalization extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: libicu-devel >= 3.6

%description intl
The php-intl package contains a dynamic shared object that will add
support for using the ICU library to PHP.

%package enchant
Summary: Enchant spelling extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.0
License: PHP
Requires: %{name}-common = %{version}-%{release}
BuildRequires: enchant-devel >= 1.2.4

%description enchant
The php-enchant package contains a dynamic shared object that will add
support for using the enchant library to PHP.

%prep
echo CIBLE = %{name}-%{version}-%{release} fpm=%{with_fpm} libzip=%{with_libzip}

# ensure than current httpd use prefork MPM.
httpd -V  | grep -q 'threaded:.*yes' && exit 1

%setup -q -n php-%{version}

%patch5 -p1 -b .includedir
%patch6 -p1 -b .embed
%patch7 -p1 -b .recode
%patch8 -p1 -b .libdb

rm -f ext/json/utf8_to_utf16.*

%patch21 -p1 -b .odbctimer

%patch40 -p1 -b .dlopen
%patch41 -p1 -b .easter
%if 0%{?rhel} >= 5
%patch42 -p1 -b .systzdata
%endif
%patch43 -p1 -b .headers
%if %{with_libzip}
%patch44 -p1 -b .systzip
%endif
%if 0%{?rhel} >= 7
%patch45 -p1 -b .ldap_r
%endif
%patch46 -p1 -b .fixheader
%patch47 -p1 -b .phpinfo

# upstream patches
%patch100 -p1 -b .bug65641

%if %{with static}
%patch212 -p1 -b .locaweb
%endif

# Fixes for tests
%patch302 -p0 -b .971416
 
# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE Zend/ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp ext/ereg/regex/COPYRIGHT regex_COPYRIGHT
cp ext/gd/libgd/README libgd_README
cp ext/gd/libgd/COPYING libgd_COPYING
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE
cp ext/mbstring/oniguruma/COPYING oniguruma_COPYING
cp ext/mbstring/ucgendat/OPENLDAP_LICENSE ucgendat_LICENSE
cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE
cp ext/phar/LICENSE phar_LICENSE
cp ext/bcmath/libbcmath/COPYING.LIB libbcmath_COPYING

# Multiple builds for multiple SAPIs
mkdir build-cgi build-apache build-embedded build-zts build-ztscli \
%if %{with_fpm}
    build-fpm
%endif

# ----- Manage known as failed test -------
# php_egg_logo_guid() removed by patch41
rm -f tests/basic/php_egg_logo_guid.phpt
# affected by systzdata patch
rm -f ext/date/tests/timezone_location_get.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt

# Safety check for API version change.
pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
if test "x${pver}" != "x%{version}"; then
   : Error: Upstream PHP version is now ${pver}, expecting %{version}.
   : Update the version/rcver macros and rebuild.
   exit 1
fi

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
vpdo=`sed -n '/#define PDO_DRIVER_API/{s/.*[ 	]//;p}' ext/pdo/php_pdo_driver.h`
if test "x${vpdo}" != "x%{pdover}"; then
   : Error: Upstream PDO ABI version is now ${vpdo}, expecting %{pdover}.
   : Update the pdover macro and rebuild.
   exit 1
fi

# Check for some extension version
ver=$(sed -n '/#define PHP_FILEINFO_VERSION /{s/.* "//;s/".*$//;p}' ext/fileinfo/php_fileinfo.h)
if test "$ver" != "%{fileinfover}"; then
   : Error: Upstream FILEINFO version is now ${ver}, expecting %{fileinfover}.
   : Update the fileinfover macro and rebuild.
   exit 1
fi
ver=$(sed -n '/#define PHP_PHAR_VERSION /{s/.* "//;s/".*$//;p}' ext/phar/php_phar.h)
if test "$ver" != "%{pharver}"; then
   : Error: Upstream PHAR version is now ${ver}, expecting %{pharver}.
   : Update the pharver macro and rebuild.
   exit 1
fi
ver=$(sed -n '/#define PHP_ZIP_VERSION_STRING /{s/.* "//;s/".*$//;p}' ext/zip/php_zip.h)
if test "$ver" != "%{zipver}"; then
   : Error: Upstream ZIP version is now ${ver}, expecting %{zipver}.
   : Update the zipver macro and rebuild.
   exit 1
fi
ver=$(sed -n '/#define PHP_JSON_VERSION /{s/.* "//;s/".*$//;p}' ext/json/php_json.h)
if test "$ver" != "%{jsonver}"; then
   : Error: Upstream JSON version is now ${ver}, expecting %{jsonver}.
   : Update the jsonver macro and rebuild.
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

%build
%if 0%{?rhel} >= 6
# aclocal workaround - to be improved
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >>aclocal.m4
%endif

# Force use of system libtool:
libtoolize --force --copy
%if 0%{?rhel} >= 6
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4
%else
cat `aclocal --print-ac-dir`/libtool.m4 > build/libtool.m4
%endif

# Regenerate configure scripts (patches change config.m4's)
touch configure.in
./buildconf --force
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign"
#CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign -fsanitize=address -ggdb"
export CFLAGS
#LDFLAGS="-fsanitize=address"
#export LDFLAGS

# Install extension modules in %{_libdir}/php/modules.
EXTENSION_DIR=%{_libdir}/php%{?_suffix}/modules; export EXTENSION_DIR

# Set PEAR_INSTALLDIR to ensure that the hard-coded include_path
# includes the PEAR directory even though pear is packaged
# separately.
PEAR_INSTALLDIR=%{_datadir}/pear%{?_suffix}; export PEAR_INSTALLDIR

# Shell function to configure and build a PHP tree.
build() {
# Old/recent bison version seems to produce a broken parser;
# upstream uses GNU Bison 2.3. Workaround:
mkdir Zend && cp ../Zend/zend_{language,ini}_{parser,scanner}.[ch] Zend
ln -sf ../configure
%configure \
	--cache-file=../config.cache \
	--with-libdir=%{_lib} \
	--libdir=%{_libdir}/php%{?_suffix} \
	--includedir=%{_includedir}/php%{?_suffix} \
	--datadir=%{_datadir}/php%{?_suffix} \
	--with-config-file-path=%{_sysconfdir}/php%{?_suffix}.d \
	--with-config-file-scan-dir=%{_sysconfdir}/php%{?_suffix}.d \
	--disable-debug \
	--with-pic \
	--disable-rpath \
	--without-pear \
	--with-bz2 \
	--with-freetype-dir=%{_prefix} \
	--with-png-dir=%{_prefix} \
	--with-xpm-dir=%{_prefix} \
	--enable-gd-native-ttf \
	--with-t1lib=%{_prefix} \
	--without-gdbm \
	--with-gettext \
	--with-iconv \
	--with-jpeg-dir=%{_prefix} \
	--with-openssl \
%if 0%{?rhel} >= 7
        --with-pcre-regex=%{_prefix} \
%endif
	--with-zlib \
	--with-layout=GNU \
	--enable-exif \
	--enable-ftp \
	--enable-sockets \
	--with-kerberos \
	--enable-shmop \
	--enable-calendar \
        --with-libxml-dir=%{_prefix} \
	--enable-xml \
%if 0%{?rhel} >= 5
        --with-system-tzdata \
%endif
	--with-mhash \
	$*
if test $? != 0; then
  tail -500 config.log
  : configure failed
  exit 1
fi

make %{?_smp_mflags}
}

# Build /usr/bin/php-cgi with the CGI SAPI, and all the shared extensions
pushd build-cgi
build --libdir=%{_libdir}/php%{?_suffix} \
      --includedir=%{_includedir}/php%{?_suffix} \
      --datadir=%{_datadir}/php%{?_suffix} \
      --enable-pcntl \
      --with-imap=shared --with-imap-ssl \
      --enable-mbstring=shared \
      --enable-mbregex \
      --with-gd=shared \
      --with-gmp=shared \
      --enable-bcmath=shared \
      --enable-dba=shared --with-db4=%{_prefix} \
                          --with-gdbm=%{_prefix} \
                          --with-tcadb=%{_prefix} \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysql=shared,mysqlnd \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
      --with-interbase=shared,%{_libdir}/firebird \
      --with-pdo-firebird=shared,%{_libdir}/firebird \
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-wddx=shared \
      --with-snmp=shared,%{_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
      --with-curl=shared,%{_prefix} \
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_prefix} \
      --with-pdo-sqlite=shared,%{_prefix} \
      --with-pdo-dblib=shared,%{_prefix} \
%if 0%{?rhel} >= 6
      --with-sqlite3=shared,%{_prefix} \
%else
      --without-sqlite3 \
%endif
      --enable-json=shared \
%if %{with_zip}
      --enable-zip=shared \
%endif
%if %{with_libzip}
      --with-libzip \
%endif
      --without-readline \
      --with-libedit \
      --with-pspell=shared \
      --enable-phar=shared \
      --with-mcrypt=shared,%{_prefix} \
      --with-tidy=shared,%{_prefix} \
      --with-mssql=shared,%{_prefix} \
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_prefix} \
      --enable-fileinfo=shared \
      --enable-intl=shared \
      --with-icu-dir=%{_prefix} \
      --with-enchant=shared,%{_prefix} \
      --with-recode=shared,%{_prefix}
popd

without_shared="--without-gd \
      --disable-dom --disable-dba --without-unixODBC \
      --disable-xmlreader --disable-xmlwriter \
      --without-sqlite3 --disable-phar --disable-fileinfo \
      --disable-json --without-pspell --disable-wddx \
      --without-curl --disable-posix \
      --disable-sysvmsg --disable-sysvshm --disable-sysvsem"

# Build Apache module, and the CLI SAPI, /usr/bin/php
pushd build-apache
build --with-apxs2=%{_httpd_apxs} \
      --libdir=%{_libdir}/php%{?_suffix} \
      --datadir=%{_datadir}/php%{?_suffix} \
      --includedir=%{_includedir}/php%{?_suffix} \
%if %{with_lsws}
      --with-litespeed \
%endif
      --enable-pdo=shared \
      --with-mysql=shared,%{_prefix} \
      --with-mysqli=shared,%{mysql_config} \
      --with-pdo-mysql=shared,%{mysql_config} \
      --without-pdo-sqlite \
      ${without_shared}
popd

%if %{with_fpm}
# Build php-fpm
pushd build-fpm
build --enable-fpm \
      --libdir=%{_libdir}/php%{?_suffix} \
      --datadir=%{_datadir} \
      --without-mysql --disable-pdo \
      ${without_shared}
popd
%endif

# Build for inclusion as embedded script language into applications,
# /usr/lib[64]/libphp5.so
pushd build-embedded
build --enable-embed \
      --libdir=%{_libdir} \
      --without-mysql --disable-pdo \
      ${without_shared}
popd

# Build a special thread-safe (mainly for modules)
pushd build-ztscli

EXTENSION_DIR=%{_libdir}/php%{?_suffix}-zts/modules
build --includedir=%{_includedir}/php%{?_suffix}-zts \
      --libdir=%{_libdir}/php%{?_suffix}-zts \
      --datadir=%{_datadir}/php%{?_suffix}-zts \
      --enable-maintainer-zts \
      --program-prefix=zts- \
      --disable-cgi \
      --with-config-file-scan-dir=%{_sysconfdir}/php%{?_suffix}-zts.d \
      --enable-pcntl \
      --with-imap=shared --with-imap-ssl \
      --enable-mbstring=shared \
      --enable-mbregex \
      --with-gd=shared \
      --with-gmp=shared \
      --enable-bcmath=shared \
      --enable-dba=shared --with-db4=%{_prefix} \
                          --with-gdbm=%{_prefix} \
                          --with-tcadb=%{_prefix} \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysql=shared,mysqlnd \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
      --with-interbase=shared,%{_libdir}/firebird \
      --with-pdo-firebird=shared,%{_libdir}/firebird \
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-wddx=shared \
      --with-snmp=shared,%{_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
      --with-curl=shared,%{_prefix} \
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_prefix} \
      --with-pdo-sqlite=shared,%{_prefix} \
      --with-pdo-dblib=shared,%{_prefix} \
%if 0%{?rhel} >= 6
      --with-sqlite3=shared,%{_prefix} \
%else
      --without-sqlite3 \
%endif
      --enable-json=shared \
%if %{with_zip}
      --enable-zip=shared \
%endif
%if %{with_libzip}
      --with-libzip \
%endif
      --without-readline \
      --with-libedit \
      --with-pspell=shared \
      --enable-phar=shared \
      --with-mcrypt=shared,%{_prefix} \
      --with-tidy=shared,%{_prefix} \
      --with-mssql=shared,%{_prefix} \
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_prefix} \
      --enable-fileinfo=shared \
      --enable-intl=shared \
      --with-icu-dir=%{_prefix} \
      --with-enchant=shared,%{_prefix} \
      --with-recode=shared,%{_prefix}
popd

# Build a special thread-safe Apache SAPI
pushd build-zts
build --with-apxs2=%{_httpd_apxs} \
      --includedir=%{_includedir}/php%{?_suffix}-zts \
      --libdir=%{_libdir}/php%{?_suffix}-zts \
      --datadir=%{_datadir}/php%{?_suffix}-zts \
      --enable-maintainer-zts \
      --with-config-file-scan-dir=%{_sysconfdir}/php%{?_suffix}-zts.d \
      --enable-pdo=shared \
      --with-mysql=shared,%{_prefix} \
      --with-mysqli=shared,%{mysql_config} \
      --with-pdo-mysql=shared,%{mysql_config} \
      --without-pdo-sqlite \
      ${without_shared}
popd
### NOTE!!! EXTENSION_DIR was changed for the -zts build, so it must remain
### the last SAPI to be built.

%check
%if %runselftest
cd build-apache
# Run tests, using the CLI SAPI
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
export SKIP_ONLINE_TESTS=1
unset TZ LANG LC_ALL
if ! make test; then
  set +x
  for f in `find .. -name \*.diff -type f -print`; do
    echo "TEST FAILURE: $f --"
    cat "$f"
    echo "-- $f result ends."
  done
  set -x
  #exit 1
fi
unset NO_INTERACTION REPORT_EXIT_STATUS MALLOC_CHECK_
%endif

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Install the extensions for the ZTS version
make -C build-ztscli install \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# rename extensions build with mysqlnd
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/mysqlnd_mysql.so
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/mysqli.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/mysqlnd_mysqli.so
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/pdo_mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/pdo_mysqlnd.so

# Install the extensions for the ZTS version modules for libmysql
make -C build-zts install-modules \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# Install the version for embedded script language in applications + php_embed.h
make -C build-embedded install-sapi install-headers \
     INSTALL_ROOT=$RPM_BUILD_ROOT

%if %{with_lsws}
install -m 755 build-apache/sapi/litespeed/php $RPM_BUILD_ROOT%{_bindir}/lsphp%{?_suffix}
%endif

# rename files to locaweb standard
mv $RPM_BUILD_ROOT%{_libdir}/libphp5-%{embed_version}.so \
     $RPM_BUILD_ROOT%{_libdir}/libphp%{?_suffix}-%{embed_version}.so
rm -f $RPM_BUILD_ROOT%{_libdir}/libphp5.so
(cd $RPM_BUILD_ROOT%{_libdir}; ln -sfn libphp%{?_suffix}-%{embed_version}.so libphp%{?_suffix}.so)

%if %{with_fpm}
# Install the php-fpm binary
make -C build-fpm install-fpm \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%endif

# Install everything from the CGI SAPI build
make -C build-cgi install \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# rename extensions build with mysqlnd
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/mysqlnd_mysql.so
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/mysqli.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/mysqlnd_mysqli.so
mv $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/pdo_mysql.so \
   $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/pdo_mysqlnd.so

# Install the mysql extension build with libmysql
make -C build-apache install-modules \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# Install the default configuration file and icons
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}.d
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}.d/php.ini
%if %{without static}
sed -i "s/php54/php/g" $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}.d/php.ini
%endif
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_contentdir}/icons
install -m 644 php.gif $RPM_BUILD_ROOT%{_httpd_contentdir}/icons/php%{?_suffix}.gif

# For third-party packaging:
install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/php%{?_suffix}

# install the DSO
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_moddir}
install -m 755 build-apache/libs/libphp5.so $RPM_BUILD_ROOT%{_httpd_moddir}/libphp%{?_suffix}.so

# install the ZTS DSO
install -m 755 build-zts/libs/libphp5.so $RPM_BUILD_ROOT%{_httpd_moddir}/libphp%{?_suffix}-zts.so

# Apache config fragment
%if "%{_httpd_modconfdir}" == "%{_httpd_confdir}"
# Single config file with httpd < 2.4
install -D -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_httpd_confdir}/php%{?_suffix}.conf
cat %{SOURCE1} >>$RPM_BUILD_ROOT%{_httpd_confdir}/php%{?_suffix}.conf
%if %{without static}
sed -i -e 's/php54_module/php5_module/g' -e 's/libphp54/libphp5/g' \
    -e 's/php54/php/g' $RPM_BUILD_ROOT%{_httpd_confdir}/php%{?_suffix}.conf
%endif
%else
# Dual config file with httpd >= 2.4
install -D -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_httpd_modconfdir}/10-php%{?_suffix}.conf
install -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_httpd_confdir}/php%{?_suffix}.conf
%if %{without static}
sed -i -e "s/php54_module/php5_module/g" -e "s/libphp54/libphp5/g" \
    "s/php54/php/g" $RPM_BUILD_ROOT%{_httpd_modconfdir}/10-php%{?_suffix}.conf \
    $RPM_BUILD_ROOT%{_httpd_confdir}/php%{?_suffix}.conf
%endif
%endif

install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}.d
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-zts.d
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/php%{?_suffix}
install -m 1777 -d $RPM_BUILD_ROOT%{_localstatedir}/lib/php%{?_suffix}/session

%if %{with_fpm}
# PHP-FPM stuff
# Log
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/log/php%{?_suffix}-fpm
# Config
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.d
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.conf
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.d/www.conf
mv $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.conf.default .
# LogRotate
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/php%{?_suffix}-fpm
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/run/php%{?_suffix}-fpm
sed -i -e 's:/run:/var/run:' $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.conf
sed -i -e 's:/run:/var/run:' $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/php%{?_suffix}-fpm
# Service
install -m 755 -d $RPM_BUILD_ROOT%{_initrddir}
install -m 755 %{SOURCE99} $RPM_BUILD_ROOT%{_initrddir}/php%{?_suffix}-fpm
# Environment file
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/php%{?_suffix}-fpm
# php-fpm should not fork on recent version
%if %{without static}
sed -i "s/php54/php/g" $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.conf \
    $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-fpm.d/www.conf \
    $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/php%{?_suffix}-fpm \
    $RPM_BUILD_ROOT%{_initrddir}/php%{?_suffix}-fpm \
    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/php%{?_suffix}-fpm
%endif
%endif

# Fix the link
(cd $RPM_BUILD_ROOT%{_bindir}; ln -sfn phar%{?_suffix}.phar phar%{?_suffix})

# Generate files lists and stub .ini files for each subpackage
for mod in pgsql mysql mysqli odbc ldap snmp xmlrpc imap \
    mysqlnd mysqlnd_mysql mysqlnd_mysqli pdo_mysqlnd \
    mbstring gd dom xsl soap bcmath dba xmlreader xmlwriter \
    gmp \
    pdo pdo_mysql pdo_pgsql pdo_odbc pdo_sqlite json %{zipmod} \
    pdo_dblib interbase pdo_firebird \
%if 0%{?rhel} >= 6
    sqlite3 \
%endif
    enchant phar fileinfo intl \
    mcrypt tidy pdo_dblib mssql pspell curl wddx \
    posix sysvshm sysvsem sysvmsg recode; do
    cat > $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}.d/${mod}.ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
    cat > $RPM_BUILD_ROOT%{_sysconfdir}/php%{?_suffix}-zts.d/${mod}.ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/php%{?_suffix}/modules/${mod}.so
%attr(755,root,root) %{_libdir}/php%{?_suffix}-zts/modules/${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php%{?_suffix}.d/${mod}.ini
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php%{?_suffix}-zts.d/${mod}.ini
EOF

done

# The dom, xsl and xml* modules are all packaged in php-xml
cat files.dom files.xsl files.xml{reader,writer} files.wddx > files.xml

# The mysql and mysqli modules are both packaged in php-mysql
cat files.mysqli >> files.mysql
# mysqlnd
cat files.mysqlnd_mysql \
    files.mysqlnd_mysqli \
    files.pdo_mysqlnd \
    >> files.mysqlnd

# Split out the PDO modules
cat files.pdo_dblib >> files.mssql
cat files.pdo_mysql >> files.mysql
cat files.pdo_pgsql >> files.pgsql
cat files.pdo_odbc >> files.odbc
cat files.pdo_firebird >> files.interbase

# sysv* and posix in packaged in php-process
cat files.sysv* files.posix > files.process

# Package sqlite3 and pdo_sqlite with pdo; isolating the sqlite dependency
# isn't useful at this time since rpm itself requires sqlite.
cat files.pdo_sqlite >> files.pdo
%if 0%{?rhel} >= 6
cat files.sqlite3 >> files.pdo
%endif

# Package json, zip, curl, phar and fileinfo in -common.
cat files.json files.curl files.phar files.fileinfo files.gmp > files.common
%if %{with_zip}
cat files.zip >> files.common
%endif

# Install the macros file:
sed -e "s/@PHP_APIVER@/%{apiver}/" \
    -e "s/@PHP_ZENDVER@/%{zendver}/" \
    -e "s/@PHP_PDOVER@/%{pdover}/" \
    -e "s/@PHP_VERSION@/%{version}/" \
    < %{SOURCE3} > macros%{?_suffix}.php
install -m 644 -D macros%{?_suffix}.php \
           $RPM_BUILD_ROOT%{macrosdir}/macros%{?_suffix}.php
%if %{without static}
sed -i "s/php54/php/g" $RPM_BUILD_ROOT%{macrosdir}/macros%{?_suffix}.php
%endif

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}/modules/*.a \
       $RPM_BUILD_ROOT%{_libdir}/php%{?_suffix}-zts/modules/*.a \
       $RPM_BUILD_ROOT%{_bindir}/{phptar} \
       $RPM_BUILD_ROOT%{_datadir}/pear \
       $RPM_BUILD_ROOT%{_libdir}/libphp5.la

%if %{with static}
# PHP 5.2/5.3 compatibility mode (Locaweb Shared Hosting)
mv $RPM_BUILD_ROOT%{_bindir}/php $RPM_BUILD_ROOT%{_bindir}/php%{?_suffix}
mv $RPM_BUILD_ROOT%{_bindir}/php-cgi $RPM_BUILD_ROOT%{_bindir}/php%{?_suffix}-cgi
mv $RPM_BUILD_ROOT%{_bindir}/php-config $RPM_BUILD_ROOT%{_bindir}/php%{?_suffix}-config
mv $RPM_BUILD_ROOT%{_bindir}/phpize $RPM_BUILD_ROOT%{_bindir}/phpize%{?_suffix}
mv $RPM_BUILD_ROOT%{_mandir}/man1/php.1 $RPM_BUILD_ROOT%{_mandir}/man1/php%{?_suffix}.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/php-config.1 $RPM_BUILD_ROOT%{_mandir}/man1/php%{?_suffix}-config.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/php-cgi.1 $RPM_BUILD_ROOT%{_mandir}/man1/php%{?_suffix}-cgi.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/phpize.1 $RPM_BUILD_ROOT%{_mandir}/man1/phpize%{?_suffix}.1

mv $RPM_BUILD_ROOT%{_bindir}/phar $RPM_BUILD_ROOT%{_bindir}/phar%{?_suffix}
mv $RPM_BUILD_ROOT%{_bindir}/phar.phar $RPM_BUILD_ROOT%{_bindir}/phar%{?_suffix}.phar
mv $RPM_BUILD_ROOT%{_mandir}/man1/phar.1 $RPM_BUILD_ROOT%{_mandir}/man1/phar%{?_suffix}.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/phar.phar.1 $RPM_BUILD_ROOT%{_mandir}/man1/phar%{?_suffix}.phar.1
sed -i 's/phar.1/phar%{?_suffix}.1/g' $RPM_BUILD_ROOT%{_mandir}/man1/phar%{?_suffix}.phar.1

mv $RPM_BUILD_ROOT%{_bindir}/zts-php $RPM_BUILD_ROOT%{_bindir}/zts-php%{?_suffix}
mv $RPM_BUILD_ROOT%{_bindir}/zts-phpize $RPM_BUILD_ROOT%{_bindir}/zts-phpize%{?_suffix}
mv $RPM_BUILD_ROOT%{_bindir}/zts-php-config $RPM_BUILD_ROOT%{_bindir}/zts-php%{?_suffix}-config
mv $RPM_BUILD_ROOT%{_mandir}/man1/zts-php.1 $RPM_BUILD_ROOT%{_mandir}/man1/zts-php%{?_suffix}.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/zts-phpize.1 $RPM_BUILD_ROOT%{_mandir}/man1/zts-phpize%{?_suffix}.1
mv $RPM_BUILD_ROOT%{_mandir}/man1/zts-php-config.1 $RPM_BUILD_ROOT%{_mandir}/man1/zts-php%{?_suffix}-config.1

# Fix php binary name and php include dir name
sed -i -e '/^include_dir=/s/\/php\"$/\"/g' \
     -e '/php_cli_binary=/s/}php\${/}php%{?_suffix}\${/g' \
     -e '/php_cgi_binary=/s/}php-cgi\${/}php%{?_suffix}-cgi\${/g' \
     $RPM_BUILD_ROOT%{_bindir}/php%{?_suffix}-config \
     $RPM_BUILD_ROOT%{_bindir}/zts-php%{?_suffix}-config
%endif

# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

exit 0

%if %{with_fpm}
%pre fpm
# Add the "%{_httpd_user}" user as we don't require httpd
getent group %{_httpd_user} >/dev/null || \
  groupadd -g 48 -r %{_httpd_user}
getent passwd webserver >/dev/null || \
  useradd -r -u 48 -g %{_httpd_user} -s /sbin/nologin \
    -d %{_httpd_contentdir} -c "Apache" %{_httpd_user}
exit 0

%post fpm
if [ $1 = 1 ]; then
    # Initial installation
    /sbin/chkconfig --add php%{?_suffix}-fpm
fi

%preun fpm
if [ $1 = 0 ]; then
    # Package removal, not upgrade
    /sbin/service php%{?_suffix}-fpm stop >/dev/null 2>&1
    /sbin/chkconfig --del php%{?_suffix}-fpm
fi

%postun fpm
if [ $1 -ge 1 ]; then
    /sbin/service php%{?_suffix}-fpm condrestart >/dev/null 2>&1 || :
fi

if [ -f /etc/rc.d/init.d/php%{?_suffix}-fpm ]; then
    /sbin/chkconfig --del php%{?_suffix}-fpm >/dev/null 2>&1 || :
fi
%endif
 
%preun
%if %{with static}
if [ -f %{_httpd_confdir}/php%{?_suffix}.conf.des ]; then
	mv %{_httpd_confdir}/php%{?_suffix}.conf.des %{_httpd_confdir}/php%{?_suffix}.conf
fi
%endif

%post
%if %{with static}
if [ -f %{_httpd_confdir}/php%{?_suffix}.conf ]; then
	mv %{_httpd_confdir}/php%{?_suffix}.conf %{_httpd_confdir}/php%{?_suffix}.conf.des
fi
%endif

%post embedded -p /sbin/ldconfig
%postun embedded -p /sbin/ldconfig

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
rm files.* macros*.php
rm -rf %{_builddir}/php-%{version}

%files
%defattr(-,root,root)
%{_httpd_moddir}/libphp%{?_suffix}.so
%{_httpd_moddir}/libphp%{?_suffix}-zts.so
%attr(1777,root,root) %dir %{_localstatedir}/lib/php%{?_suffix}/session
%config(noreplace) %{_httpd_confdir}/php%{?_suffix}.conf
%if "%{_httpd_modconfdir}" != "%{_httpd_confdir}"
%config(noreplace) %{_httpd_modconfdir}/10-php%{?_suffix}.conf
%endif
%{_httpd_contentdir}/icons/php%{?_suffix}.gif

%files common -f files.common
%defattr(-,root,root)
%doc CODING_STANDARDS CREDITS EXTENSIONS LICENSE NEWS README*
%doc Zend/ZEND_* TSRM_LICENSE regex_COPYRIGHT
%doc libmagic_LICENSE
%doc phar_LICENSE
%doc php.ini-*
%config(noreplace) %{_sysconfdir}/php%{?_suffix}.d/php.ini
%dir %{_sysconfdir}/php%{?_suffix}.d
%dir %{_sysconfdir}/php%{?_suffix}-zts.d
%dir %{_libdir}/php%{?_suffix}
%dir %{_libdir}/php%{?_suffix}/modules
%dir %{_libdir}/php%{?_suffix}-zts
%dir %{_libdir}/php%{?_suffix}-zts/modules
%dir %{_localstatedir}/lib/php%{?_suffix}
%dir %{_datadir}/php%{?_suffix}

%files cli
%defattr(-,root,root)
%{_bindir}/php%{?_suffix}
%{_bindir}/zts-php%{?_suffix}
%{_bindir}/php%{?_suffix}-cgi
%{_bindir}/phar%{?_suffix}.phar
%{_bindir}/phar%{?_suffix}
# provides phpize here (not in -devel) for pecl command
%{_bindir}/phpize%{?_suffix}
%{_mandir}/man1/php%{?_suffix}.1*
%{_mandir}/man1/zts-php%{?_suffix}.1*
%{_mandir}/man1/php%{?_suffix}-cgi.1*
%{_mandir}/man1/phar%{?_suffix}.1*
%{_mandir}/man1/phar%{?_suffix}.phar.1*
%{_mandir}/man1/phpize%{?_suffix}.1*
%doc sapi/cgi/README* sapi/cli/README

%if %{with_fpm}
%files fpm
%defattr(-,root,root)
%doc php%{?_suffix}-fpm.conf.default
%doc fpm_LICENSE
%attr(1777,root,root) %dir %{_localstatedir}/lib/php%{?_suffix}/session
%config(noreplace) %{_sysconfdir}/php%{?_suffix}-fpm.conf
%config(noreplace) %{_sysconfdir}/php%{?_suffix}-fpm.d/www.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/php%{?_suffix}-fpm
%config(noreplace) %{_sysconfdir}/sysconfig/php%{?_suffix}-fpm
%{_initrddir}/php%{?_suffix}-fpm
%attr(770,webserver,root) %dir %{_localstatedir}/run/php%{?_suffix}-fpm
%{_sbindir}/php%{?_suffix}-fpm
%dir %{_sysconfdir}/php%{?_suffix}-fpm.d
# log owned by webserver for log
%attr(770,webserver,root) %dir %{_localstatedir}/log/php%{?_suffix}-fpm
%{_mandir}/man8/php%{?_suffix}-fpm.8*
%if %{with static}
%dir %{_datadir}/php%{?_suffix}-fpm
%{_datadir}/php%{?_suffix}-fpm/status.html
%else
%dir %{_datadir}/fpm
%{_datadir}/fpm/status.html
%endif
%endif

%if %{with_lsws}
%files litespeed
%defattr(-,root,root)
%{_bindir}/lsphp%{?_suffix}
%endif

%files devel
%defattr(-,root,root)
%{_bindir}/php%{?_suffix}-config
%{_bindir}/zts-php%{?_suffix}-config
%{_bindir}/zts-phpize%{?_suffix}
%{_includedir}/php%{?_suffix}
%{_includedir}/php%{?_suffix}-zts
%{_libdir}/php%{?_suffix}/build
%{_libdir}/php%{?_suffix}-zts/build
%{_mandir}/man1/php%{?_suffix}-config.1*
%{_mandir}/man1/zts-php%{?_suffix}-config.1*
%{_mandir}/man1/zts-phpize%{?_suffix}.1*
%{macrosdir}/macros%{?_suffix}.php

%files embedded
%defattr(-,root,root,-)
%{_libdir}/libphp%{?_suffix}.so
%{_libdir}/libphp%{?_suffix}-%{embed_version}.so

%files pgsql -f files.pgsql
%files mysql -f files.mysql
%files odbc -f files.odbc
%files imap -f files.imap
%files ldap -f files.ldap
%files snmp -f files.snmp
%files xml -f files.xml
%files xmlrpc -f files.xmlrpc
%files mbstring -f files.mbstring
%doc libmbfl_LICENSE
%doc oniguruma_COPYING
%doc ucgendat_LICENSE
%files gd -f files.gd
%defattr(-,root,root,-)
%doc libgd_README
%doc libgd_COPYING
%files soap -f files.soap
%files bcmath -f files.bcmath
%doc libbcmath_COPYING
%files dba -f files.dba
%files pdo -f files.pdo
%files mcrypt -f files.mcrypt
%files tidy -f files.tidy
%files mssql -f files.mssql
%files pspell -f files.pspell
%files intl -f files.intl
%files process -f files.process
%files recode -f files.recode
%files interbase -f files.interbase
%files enchant -f files.enchant
%files mysqlnd -f files.mysqlnd

%changelog
* Thu Oct 24 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.34-1
- Merged with Remi changes:
  Update to 5.4.34
  http://www.php.net/releases/5_4_34.php
  build gmp as shared, so can be disabled by user

* Mon Sep 22 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.33-2
- Merged with Remi changes:
  openssl: fix regression introduce in changes for upstream
  bug #65137 and #41631, revert to 5.4.32 behavior

* Thu Sep 19 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.33-1
- Merged with Remi changes:
  Update to 5.4.33
  http://www.php.net/releases/5_4_33.php
  fpm: fix script_name with mod_proxy_fcgi / proxypass
  add upstream patch for https://bugs.php.net/65641

* Thu Sep 11 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.32-2
- add _suffix 54

* Mon Sep  1 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.32-1
- Merged with Remi changes:
- Update to 5.4.32
  http://www.php.net/releases/5_4_32.php
  fix zts-php-config --php-binary output #1124605
  fix segfault in php_wddx_serialize_var
  upstream patch for https://bugs.php.net/67873

* Mon Aug 18 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.31-1
- Merged with Remi changes:
- Update to 5.4.31
  http://www.php.net/releases/5_4_31.php
  add php-litespeed subpackage (/usr/bin/lsphp)

* Fri Jun 28 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.30-1
- Merged with Remi changes:
- Update to 5.4.30
  http://www.php.net/releases/5_4_30.php

* Tue Jun 17 2014 Remi Collet <rcollet@redhat.com> 5.4.30-0.2.RC1
- fix test for rhbz #971416

* Tue Jun 17 2014 Remi Collet <rcollet@redhat.com> 5.4.30-0.1.RC1
- Test build of 5.4.30RC1

* Thu Jun  5 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.29-3
- Merged with Remi changes:
- fix regression introduce in fix for #67118

* Tue Jun  3 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.29-2
- Merged with Remi changes:
- fileinfo: fix insufficient boundary check
- workaround regression introduce in fix for 67072 in
  serialize/unzerialize functions

* Wed May 28 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.29-1
- Merged with Remi changes:
- Update to 5.4.29
  http://www.php.net/releases/5_4_29.php
- sync php.ini with upstream php.ini-production

* Fri May  2 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.28-1
- Merged with Remi changes:
- Update to 5.4.28
  http://www.php.net/releases/5_4_28.php

* Tue Apr 15 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.27-4
- Fix %clean session order, this session must be before %files.

* Sun Apr 13 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.27-3
- Fix includedir and php binary name on php54-config and zts-php54-config.

* Wed Apr 12 2014 Claudio Filho <claudio.filho@locaweb.com.br> 5.4.27-2
- Remove oci8, systemd and fedora support.
- Remove isasuffix, snapdate and rcver.
- Fix mysql_config.
- Add locaweb and static conditional package builds
- Add locaweb static patch.
- Add php54 prefix on all files.
- Add pcre-devel >= 6.6 on BuildRequires if rhel < 7.
- Remove Obsoletes.
- Downgrade libicu-devel.
- Fix %configure to include --datadir and --includedir.
- Fix %configure to remove --with-exec-dir and --enable-mysqlnd-threading.
- Add pdo_dblib support.
- Fix apache username on %pre fpm.
- Fix permissions of the session directory.
- Fix pear install dir
- Rebuild for locaweb.

* Thu Apr  3 2014 Remi Collet <remi@fedoraproject.org> 5.4.27-1
- Update to 5.4.27
  http://www.php.net/ChangeLog-5.php#5.4.27

* Tue Mar 25 2014 Remi Collet <rcollet@redhat.com> 5.4.27-0.1.RC1
- test build of 5.4.24RC1
- patch for bug 66946

* Wed Mar  5 2014 Remi Collet <remi@fedoraproject.org> 5.4.26-1
- Update to 5.4.26 (security)
  http://www.php.net/ChangeLog-5.php#5.4.26

* Wed Feb 26 2014 Remi Collet <rcollet@redhat.com> 5.4.25-2.1
- php-fpm should own /var/lib/php/session

* Tue Feb 18 2014 Remi Collet <rcollet@redhat.com> 5.4.25-2
- upstream patch for https://bugs.php.net/66731

* Tue Feb 11 2014 Remi Collet <remi@fedoraproject.org> 5.4.25-1
- Update to 5.4.25
  http://www.php.net/ChangeLog-5.php#5.4.25
- Install macros to /usr/lib/rpm/macros.d where available.
- Add configtest option to php-fpm ini script (EL)
- Fix _httpd_mmn expansion in absence of httpd-devel

* Wed Jan  8 2014 Remi Collet <rcollet@redhat.com> 5.4.24-1
- update to 5.4.24

* Sat Dec 28 2013 Remi Collet <rcollet@redhat.com> 5.4.24-0.1.RC1
- test build of 5.4.24RC1

* Wed Dec 11 2013 Remi Collet <rcollet@redhat.com> 5.4.23-1
- update to 5.4.23, fix for CVE-2013-6420
- fix zend_register_functions breaks reflection, php bug 66218

* Wed Dec  4 2013 Remi Collet <rcollet@redhat.com> 5.4.23-0.2.RC1
- test build for https://bugs.php.net/66218
  zend_register_functions breaks reflection

* Thu Nov 28 2013 Remi Collet <rcollet@redhat.com> 5.4.23-0.1.RC1
- test build of 5.4.23RC1

* Wed Nov 13 2013 Remi Collet <remi@fedoraproject.org> 5.4.22-1
- update to 5.4.22

* Sat Nov  2 2013 Remi Collet <remi@fedoraproject.org> 5.4.22-0.1.RC1
- test build of 5.4.22RC1

* Sun Oct 27 2013 Remi Collet <remi@fedoraproject.org> 5.4.21-2
- rebuild using libicu-last 50.1.2

* Wed Oct 16 2013 Remi Collet <rcollet@redhat.com> - 5.4.21-1
- update to 5.4.21

* Wed Sep 18 2013 Remi Collet <rcollet@redhat.com> - 5.4.20-1
- update to 5.4.20

* Fri Aug 30 2013 Remi Collet <rcollet@redhat.com> - 5.4.19-2
- test build for https://bugs.php.net/65564

* Thu Aug 22 2013 Remi Collet <rcollet@redhat.com> - 5.4.19-1
- update to 5.4.19

* Mon Aug 19 2013 Remi Collet <remi@fedoraproject.org> 5.4.18-1
- update to 5.4.18, fix for CVE-2013-4248
- php-oci8 build with oracle instantclient 12.1

* Fri Jul 12 2013 Remi Collet <rcollet@redhat.com> - 5.4.17-2
- add security fix for CVE-2013-4113
- add missing ASL 1.0 license

* Wed Jul  3 2013 Remi Collet <rcollet@redhat.com> 5.4.17-1
- update to 5.4.17

* Tue Jul  2 2013 Remi Collet <rcollet@redhat.com> 5.4.16-2
- add missing man pages (phar, php-cgi)

* Wed Jun  5 2013 Remi Collet <rcollet@redhat.com> 5.4.16-1
- update to 5.4.16
- switch systemd unit to Type=notify
- patch for upstream Bug #64915 error_log ignored when daemonize=0
- patch for upstream Bug #64949 Buffer overflow in _pdo_pgsql_error
- patch for upstream bug #64960 Segfault in gc_zval_possible_root

* Thu May  9 2013 Remi Collet <rcollet@redhat.com> 5.4.15-1
- update to 5.4.15
- clean very old obsoletes

* Thu Apr 11 2013 Remi Collet <rcollet@redhat.com> 5.4.14-1
- update to 5.4.14
- clean old deprecated options

* Thu Mar 14 2013 Remi Collet <rcollet@redhat.com> 5.4.13-1
- update to 5.4.13
- security fixes for CVE-2013-1635 and CVE-2013-1643
- Remove %%config from %%{_sysconfdir}/rpm/macros.*
  (https://fedorahosted.org/fpc/ticket/259)

* Wed Feb 20 2013 Remi Collet <remi@fedoraproject.org> 5.4.12-1
- update to 5.4.12

* Wed Feb 13 2013 Remi Collet <remi@fedoraproject.org> 5.4.11-2
- enable tokyocabinet and gdbm dba handlers

* Wed Feb 13 2013 Remi Collet <rcollet@redhat.com> 5.4.11-2
- upstream patch (5.4.13) to fix dval to lval conversion
  https://bugs.php.net/64142
- upstream patch (5.4.13) for 2 failed tests
- fix buit-in web server on ppc64 (fdset usage)
  https://bugs.php.net/64128

* Wed Jan 16 2013 Remi Collet <rcollet@redhat.com> 5.4.11-1
- update to 5.4.11
- fix php.conf to allow MultiViews managed by php scripts

* Wed Dec 19 2012 Remi Collet <rcollet@redhat.com> 5.4.10-1
- update to 5.4.10
- remove patches merged upstream

* Tue Dec 11 2012 Remi Collet <rcollet@redhat.com> 5.4.9-3
- drop "Configure Command" from phpinfo output

* Tue Dec 11 2012 Joe Orton <jorton@redhat.com> - 5.4.9-2
- prevent php_config.h changes across (otherwise identical) rebuilds

* Fri Nov 23 2012 Remi Collet <remi@fedoraproject.org> 5.4.9-2
- add patch for https://bugs.php.net/63588
  duplicated implementation of php_next_utf8_char

* Thu Nov 22 2012 Remi Collet <remi@fedoraproject.org> 5.4.9-1
- update to 5.4.9

* Thu Nov 15 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.5.RC1
- switch back to upstream generated scanner/parser

* Thu Nov 15 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.4.RC1
- use _httpd_contentdir macro and fix php.gif path

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.3.RC1
- improve system libzip patch to use pkg-config

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.2.RC1
- use _httpd_moddir macro

* Wed Nov 14 2012 Remi Collet <rcollet@redhat.com> 5.4.9-0.1.RC1
- update to 5.4.9RC1
- improves php.conf (use FilesMatch + SetHandler)
- improves filter (httpd module)
- apply ldap_r patch on fedora >= 18 only

* Fri Nov  9 2012 Remi Collet <remi@fedoraproject.org> 5.4.9-0.2.RC1
- sync with rawhide

* Fri Nov  9 2012 Remi Collet <rcollet@redhat.com> 5.4.8-6
- clarify Licenses
- missing provides xmlreader and xmlwriter
- modernize spec

* Thu Nov  8 2012 Remi Collet <remi@fedoraproject.org> 5.4.9-0.1.RC1
- update to 5.4.9RC1
- change php embedded library soname version to 5.4

* Tue Nov  6 2012 Remi Collet <rcollet@redhat.com> 5.4.8-5
- fix _httpd_mmn macro definition

* Mon Nov  5 2012 Remi Collet <rcollet@redhat.com> 5.4.8-4
- fix mysql_sock macro definition

* Thu Oct 25 2012 Remi Collet <rcollet@redhat.com> 5.4.8-3
- fix installed headers

* Tue Oct 23 2012 Joe Orton <jorton@redhat.com> - 5.4.8-2
- use libldap_r for ldap extension

* Thu Oct 18 2012 Remi Collet <remi@fedoraproject.org> 5.4.8-1
- update to 5.4.8
- define both session.save_handler and session.save_path
- fix possible segfault in libxml (#828526)
- php-fpm: create apache user if needed
- use SKIP_ONLINE_TEST during make test
- php-devel requires pcre-devel and php-cli (instead of php)

* Fri Oct  5 2012 Remi Collet <remi@fedoraproject.org> 5.4.8-0.3.RC1
- provides php-phar

* Thu Oct  4 2012 Remi Collet <RPMS@famillecollet.com> 5.4.8-0.2.RC1
- update systzdata patch to v10, timezone are case insensitive

* Thu Oct  4 2012 Remi Collet <RPMS@famillecollet.com> 5.4.8-0.1.RC1
- update to 5.4.8RC1

* Mon Oct  1 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-10
- fix typo in systemd macro

* Mon Oct  1 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-9
- php-fpm: enable PrivateTmp
- php-fpm: new systemd macros (#850268)
- php-fpm: add upstream patch for startup issue (#846858)

* Fri Sep 28 2012 Remi Collet <rcollet@redhat.com> 5.4.7-8
- systemd integration, https://bugs.php.net/63085
- no odbc call during timeout, https://bugs.php.net/63171
- check sqlite3_column_table_name, https://bugs.php.net/63149

* Mon Sep 24 2012 Remi Collet <rcollet@redhat.com> 5.4.7-7
- most failed tests explained (i386, x86_64)

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-6
- fix for http://bugs.php.net/63126 (#783967)

* Wed Sep 19 2012 Remi Collet <RPMS@famillecollet.com> 5.4.7-6
- add --daemonize / --nodaemonize options to php-fpm
  upstream RFE: https://bugs.php.net/63085

* Wed Sep 19 2012 Remi Collet <RPMS@famillecollet.com> 5.4.7-5
- sync with rawhide
- patch to report libdb version https://bugs.php.net/63117

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-5
- patch to ensure we use latest libdb (not libdb4)

* Wed Sep 19 2012 Remi Collet <rcollet@redhat.com> 5.4.7-4
- really fix rhel tests (use libzip and libdb)

* Tue Sep 18 2012 Remi Collet <rcollet@redhat.com> 5.4.7-3
- fix test to enable zip extension on RHEL-7

* Mon Sep 17 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-2
- remove session.save_path from php.ini
  move it to apache and php-fpm configuration files

* Fri Sep 14 2012 Remi Collet <remi@fedoraproject.org> 5.4.7-1
- update to 5.4.7
  http://www.php.net/releases/5_4_7.php
- php-fpm: don't daemonize

* Thu Sep 13 2012 Remi Collet <RPMS@famillecollet.com> 5.4.7-1
- update to 5.4.7

* Mon Sep  3 2012 Remi Collet <RPMS@famillecollet.com> 5.4.7-0.2.RC1
- obsoletes php53* and php54*

* Fri Aug 31 2012 Remi Collet <RPMS@famillecollet.com> 5.4.7-0.1.RC1
- update to 5.4.7RC1

* Mon Aug 20 2012 Remi Collet <remi@fedoraproject.org> 5.4.6-2
- enable php-fpm on secondary arch (#849490)

* Thu Aug 16 2012 Remi Collet <remi@fedoraproject.org> 5.4.6-1
- update to 5.4.6

* Thu Aug 02 2012 Remi Collet <RPMS@famillecollet.com> 5.4.6-0.1.RC1
- update to 5.4.6RC1

* Fri Jul 20 2012 Remi Collet <RPMS@famillecollet.com> 5.4.5-1
- update to 5.4.5

* Sat Jul 07 2012 Remi Collet <RPMS@famillecollet.com> 5.4.5-0.2.RC1
- update patch for system libzip

* Wed Jul 04 2012 Remi Collet <RPMS@famillecollet.com> 5.4.5-0.1.RC1
- update to 5.4.5RC1 with bundled libzip.

* Mon Jul 02 2012 Remi Collet <RPMS@famillecollet.com> 5.4.4-4
- use system pcre only on fedora >= 14 (version 8.10)
- drop BR for libevent (#835671)
- provide php(language) to allow version check
- define %%{php_version}

* Thu Jun 21 2012 Remi Collet <RPMS@famillecollet.com> 5.4.4-2
- clean spec, sync with rawhide
- add missing provides (core, ereg, filter, standard)

* Wed Jun 13 2012 Remi Collet <Fedora@famillecollet.com> 5.4.4-1
- update to 5.4.4 finale
- fedora >= 15: use /usr/lib/tmpfiles.d instead of /etc/tmpfiles.d
- fedora >= 15: use /run/php-fpm instead of /var/run/php-fpm

* Thu May 31 2012 Remi Collet <Fedora@famillecollet.com> 5.4.4-0.2.RC2
- update to 5.4.4RC2

* Thu May 17 2012 Remi Collet <Fedora@famillecollet.com> 5.4.4-0.1.RC1
- update to 5.4.4RC1

* Wed May 09 2012 Remi Collet <Fedora@famillecollet.com> 5.4.3-1
- update to 5.4.3 (CVE-2012-2311, CVE-2012-2329)

* Thu May 03 2012 Remi Collet <remi@fedoraproject.org> 5.4.2-1
- update to 5.4.2 (CVE-2012-1823)

* Fri Apr 27 2012 Remi Collet <remi@fedoraproject.org> 5.4.1-1
- update to 5.4.1
- use libdb in fedora >= 18 instead of db4

* Fri Apr 13 2012 Remi Collet <remi@fedoraproject.org> 5.4.1-0.3.RC2
- update to 5.4.1RC2

* Sat Mar 31 2012 Remi Collet <remi@fedoraproject.org> 5.4.1-0.2.RC1
- rebuild

* Sat Mar 31 2012 Remi Collet <remi@fedoraproject.org> 5.4.1-0.1.RC1
- update to 5.4.1RC1, split php conf when httpd 2.4

* Tue Mar 27 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-1.1
- sync with rawhide (httpd 2.4 stuff)

* Mon Mar 26 2012 Joe Orton <jorton@redhat.com> - 5.4.0-2
- rebuild against httpd 2.4
- use _httpd_mmn, _httpd_apxs macros
- fix --without-system-tzdata build for Debian et al

* Fri Mar 02 2012 Remi Collet <remi@fedoraproject.org> 5.4.0-1
- update to PHP 5.4.0 finale

* Sat Feb 18 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.16.RC8
- update to 5.4.0RC8

* Sat Feb 04 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.15.RC7
- update to 5.4.0RC7

* Fri Jan 27 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.14.RC6
- build against system libzip (fedora >= 17), patch from spot

* Thu Jan 26 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.13.RC6
- add /etc/sysconfig/php-fpm environment file (#784770)

* Wed Jan 25 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.12.RC6
- keep all ZTS binaries in /usr/bin (with zts prefix)

* Thu Jan 19 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.11.RC6
- update to 5.4.0RC6

* Wed Jan 18 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.10.RC5
- add some fedora patches back (dlopen, easter, phpize)

* Mon Jan 16 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.9.RC5
- improves mysql.sock default path

* Fri Jan 13 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.8.RC5
- update to 5.4.0RC5
- patch for https://bugs.php.net/60748 (mysql.sock hardcoded)
- move session.path from php.ini to httpd/conf.d/php.conf
- provides both ZTS mysql extensions (libmysql/mysqlnd)
- build php cli ZTS binary, in -devel, mainly for test

* Wed Jan 04 2012 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.7.201201041830
- new snapshot (5.4.0RC5-dev) with fix for https://bugs.php.net/60627

* Fri Dec 30 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.6.201112300630
- new snapshot (5.4.0RC5-dev)

* Mon Dec 26 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.6.201112261030
- new snapshot (5.4.0RC5-dev)

* Sat Dec 17 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.5.201112170630
- new snapshot (5.4.0RC4-dev)

* Mon Dec 12 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.4.201112121330
- new snapshot (5.4.0RC4-dev)
- switch to systemd

* Fri Dec 09 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.3.201112091730
- new snapshot (5.4.0RC4-dev)
- removed patch merged upstream for https://bugs.php.net/60392
- clean ini (from upstream production default)

* Sun Nov 13 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.3.201111260730
- new snapshot (5.4.0RC3-dev)
- patch for https://bugs.php.net/60392 (old libicu on EL-5)

* Sun Nov 13 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.3.201111130730
- new snapshot (5.4.0RC2-dev)
- sync with latest changes in 5.3 spec

* Thu Sep 08 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.2.201109081430
- new snapshot
- build mysql/mysqli against both libmysql and mysqlnd (new mysqlnd sub-package)

* Sat Sep 03 2011 Remi Collet <Fedora@famillecollet.com> 5.4.0-0.1.201109031230
- first work on php 5.4
- remove -sqlite subpackage
- move php/modules-zts to php-zts/modules

* Wed Aug 24 2011 Remi Collet <Fedora@famillecollet.com> 5.3.8-2
- provides zts devel stuff

* Tue Aug 23 2011 Remi Collet <Fedora@famillecollet.com> 5.3.8-1.1
- EL-5 build with latest libcurl 7.21.7

* Tue Aug 23 2011 Remi Collet <Fedora@famillecollet.com> 5.3.8-1
- update to 5.3.8
  http://www.php.net/ChangeLog-5.php#5.3.8

* Sun Aug 21 2011 Remi Collet <Fedora@famillecollet.com> 5.3.7-2.1
- EL-5 build with latest libcurl 7.21.7

* Sat Aug 20 2011 Remi Collet <Fedora@famillecollet.com> 5.3.7-2
- add patch for https://bugs.php.net/55439

* Fri Aug 19 2011 Remi Collet <Fedora@famillecollet.com> 5.3.7-1.1
- EL-5 build with latest libcurl 7.21.7

* Thu Aug 18 2011 Remi Collet <Fedora@famillecollet.com> 5.3.7-1
- update to 5.3.7
  http://www.php.net/ChangeLog-5.php#5.3.7
- merge php-zts into php (#698084)

* Mon May 16 2011 Remi Collet <rpms@famillecollet.com> 5.3.6-4
- backport patch for #50755 (multiple rowset in pdo_dblib)

* Fri Apr 15 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-3
- add patch to fix build against MySQL 5.5 on EL-4

* Mon Apr  4 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-3
- enable mhash extension (emulated by hash extension)

* Tue Mar 29 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-2
- fix relocated (php53) build

* Thu Mar 17 2011 Remi Collet <Fedora@famillecollet.com> 5.3.6-1
- update to 5.3.6
  http://www.php.net/ChangeLog-5.php#5.3.6

* Tue Mar 15 2011 Joe Orton <jorton@redhat.com> - 5.3.5-6
- disable zip extension per "No Bundled Libraries" policy (#551513)

* Mon Mar 07 2011 Caolán McNamara <caolanm@redhat.com> 5.3.5-5
- rebuild for icu 4.6

* Mon Feb 28 2011 Remi Collet <Fedora@famillecollet.com> 5.3.5-4
- fix systemd-units requires

* Thu Feb 24 2011 Remi Collet <Fedora@famillecollet.com> 5.3.5-3
- add tmpfiles.d configuration for php-fpm
- add Arch specific requires/provides

* Fri Feb 11 2011 Remi Collet <rpms@famillecollet.com> 5.3.5-1.2
- rebuild against MySQL 5.5 (fedora <= 8)

* Sat Jan 22 2011 Remi Collet <rpms@famillecollet.com> 5.3.5-1.1
- rebuild against freetds 0.82 (EL <= 5, fedora <= 10)

* Fri Jan 07 2011 Remi Collet <rpms@famillecollet.com> 5.3.5-1
- update to 5.3.5
  http://www.php.net/ChangeLog-5.php#5.3.5

* Sun Dec 26 2010 Remi Collet <rpms@famillecollet.com> 5.3.4-3
- relocate using phpname macro
- rebuild against MySQL 5.5

* Sun Dec 12 2010 Remi Collet <rpms@famillecollet.com> 5.3.4-2
- security patch from upstream for #660517

* Sat Dec 11 2010 Remi Collet <rpms@famillecollet.com> 5.3.4-1
- update to 5.3.4
  http://www.php.net/ChangeLog-5.php#5.3.4
- move phpize to php-cli (see #657812)
- create php-sqlite subpackage (for old sqlite2 ext)

* Wed Sep 29 2010 Remi Collet <rpms@famillecollet.com> 5.3.3-1.2
- use SIGUSR2 for service reload
- fix slowlog comment + set default value

* Fri Jul 30 2010 Remi Collet <rpms@famillecollet.com> 5.3.3-1.1
- use system pcre only on fedora >= 10 (version 7.8)
- rebuild

* Thu Jul 22 2010 Remi Collet <rpms@famillecollet.com> 5.3.3-1.
- update to 5.3.3
- add php-fpm sub-package
- systzdata-v7.patch

* Tue Apr 27 2010 Remi Collet <rpms@famillecollet.com> 5.3.2-2
- garbage collector upstream  patches

* Fri Mar  5 2010 Remi Collet <rpms@famillecollet.com> 5.3.2-1.###.remi
- update to 5.3.2

* Wed Feb 24 2010 Remi Collet <rpms@famillecollet.com> 5.3.2-0.2.RC3.###.remi
- update to 5.3.2RC3

* Fri Feb 12 2010 Remi Collet <rpms@famillecollet.com> 5.3.2-0.1.RC2.###.remi
- update to 5.3.2RC2

* Sat Dec 26 2009 Remi Collet <rpms@famillecollet.com> 5.3.2-0.1.RC1.###.remi
- update to 5.3.2RC1
- remove mime_magic option (now provided by fileinfo, by emu)

* Fri Nov 20 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-1.###.remi
- PHP 5.3.1 Released!

* Sat Nov 14 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.6.RC4.###.remi
- fix mysql default socket

* Sat Nov 14 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.5.RC4.###.remi
- Rebuild with most extension for ZTS

* Fri Nov 13 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.4.RC4.###.remi
- update to 5.3.1RC4

* Wed Nov 04 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.3.RC3.###.remi
- update to 5.3.1RC3

* Wed Oct 21 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.2.RC2.###.remi
- update to 5.3.1RC2

* Sat Sep 05 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.2.RC1.###.remi
- update to 5.3.1RC1

* Sat Aug 15 2009 Remi Collet <rpms@famillecollet.com> 5.3.1-0.1.200908150630.###.remi
- update to 5.3.1RC1
- swicth back to v6 of systzdata patch (to be synced with rawhide)

* Sat Jul 18 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-2.###.remi.2
- update to v7 of systzdata patch (only enabled on maintained distro)

* Fri Jul 17 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-2.###.remi.1
- update to v6 of systzdata patch

* Tue Jul 14 2009 Joe Orton <jorton@redhat.com> 5.3.0-2
- update to v5 of systzdata patch; parses zone.tab and extracts
  timezone->{country-code,long/lat,comment} mapping table

* Fri Jun 19 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-1.###.remi
- PHP 5.3.0 Released!

* Fri Jun 19 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.6.RC4.###.remi
- Version 5.3.0RC4
- fix session.save_path in php.ini
- obsolete php-pecl-json

* Fri Jun 12 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.5.RC3.###.remi
- Version 5.3.0RC3

* Sat May 09 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.5.RC2.###.remi
- add php-interbase subpackage

* Fri May 08 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.4.RC2.###.remi
- Version 5.3.0RC2

* Thu Apr 30 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.4.RC1.fc11.remi
- F11 build
- fix provides for obsoleted pecl extension

* Sun Apr 05 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.4.RC1.el5.remi
- EL5 rebuild without new sqlite3 extension

* Wed Mar 25 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.4.RC1.fc10.remi
- add php-enchant sub-package (new extension)

* Tue Mar 24 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.3.RC1.fc10.remi
- Version 5.3.0RC1
- new php.ini from upstream php.ini-production

* Sat Feb 28 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.2.beta1.fc10.remi
- Sync with rawhide (add php-process + php-recode)

* Thu Jan 29 2009 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.beta1.fc10.remi
- Version 5.3.0beta1

* Sat Dec 27 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha4-dev.200812271530.fc10.remi
- new snapshot (5.3.0alpha4-dev)

* Sat Dec 13 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha4-dev.200812131330.fc10.remi
- new snapshot (5.3.0alpha4-dev)
- remove mhash sub-package

* Sat Oct 18 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200810181430.fc9.remi
- new snapshot (5.3.0alpha3-dev)

* Sun Oct 12 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200810120830.fc9.remi
- new snapshot (5.3.0alpha3-dev)

* Sat Oct  4 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200810041630.fc9.remi
- new snapshot (5.3.0alpha3-dev)
- add Requires to Sqlite 3.5.9-2 to get the loadextension option

* Sat Sep 27 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200809270830.fc9.remi
- new snapshot (5.3.0alpha3-dev)

* Sat Sep 13 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200809131430.fc9.remi
- new snapshot (5.3.0alpha3-dev)
- switch to oracle instant client 11.1.0.6 on i386, x86_64

* Sun Sep 07 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha3-dev.200809070630.fc9.remi
- new snapshot (5.3.0alpha3-dev)
- remove gd-devel from BR and add with-xpm-dir (bundled GD provided more functions)

* Sat Aug 30 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808300430.fc9.remi
- new snapshot (5.3.0alpha2-dev)
- (re)enable mime-magic
- use bundled GD (build fails with system one)

* Wed Aug 20 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808200630.fc9.remi
- new snapshot (5.3.0alpha2-dev)
- use system GD instead of bundled GD when >= 2.0.35 (Fedora >= 6)

* Sun Aug 17 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808170830.fc9.remi
- new snapshot (5.3.0alpha2-dev)
- php-5.2.4-tests-dashn.patch applied upstream

* Sun Aug 10 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808101630.fc9.remi
- new snapshot (5.3.0alpha2-dev)
- no more dbase extension

* Wed Aug 06 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808061630.fc9.remi
- new snapshot (5.3.0alpha2-dev) (not published)
- PHP Bug #45636 fixed

* Mon Aug 04 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808041430.fc9.remi
- new snapshot (5.3.0alpha2-dev) (not published)

* Sat Aug 02 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.1.alpha2-dev.200808020430.fc9.remi
- new snapshot (5.3.0alpha2-dev)
- add php-intl sub-package

* Thu Jul 31 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807311430.fc9.remi
- new snapshot
- fix fileinfo in php-common (not in php-xml)

* Mon Jul 28 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807281630.fc9.remi
- new snapshot
- awfull hack on fileinfo/libmagic/softmagic.c

* Sun Jul 27 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807271430.fc9.remi
- new snapshot
- php-common now provide Fileinfo extension (obsoletes php-pecl-Fileinfo)
- php-pdo now provides SQLite3 extension

* Tue Jul 22 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807221630.fc9.remi
- new snapshot
- PHP Bug #45557 fixed
- PHP Bug #45564 fixed

* Mon Jul 21 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807211430.fc9.remi
- new snapshot
- PHP Bug #45572 fixed

* Sun Jul 20 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807201630.fc9.remi
- new snapshot
- more visibility patch (mbfl)

* Sun Jul 20 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807200630.fc9.remi
- new snapshot
- merge php-phar in php-commonn and php-cli (phar.phar command)
- get t2lib option back

* Sat Jul 19 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807191230.fc9.remi
- new snapshot

* Fri Jul 18 2008 Remi Collet <rpms@famillecollet.com> 5.3.0-0.dev.200807181430.fc9.remi
- first 5.3.0 build

* Sun May 11 2008 Remi Collet <rpms@famillecollet.com> 5.2.6-2.###.remi
- sync with rawhide (add php-pspell)

* Thu May  8 2008 Joe Orton <jorton@redhat.com> 5.2.6-2
- update to 5.2.6

* Tue May  6 2008 Remi Collet <rpms@famillecollet.com> 5.2.6-1.###.remi
- update to 5.2.6

* Thu Apr 24 2008 Joe Orton <jorton@redhat.com> 5.2.5-7
- split pspell extension out into php-pspell (#443857)

* Sat Apr 12 2008 Remi Collet <rpms@famillecollet.com> 5.2.6-0.1.RC.fc8.remi
- update to 5.2.6RC5 for testing

* Wed Apr 09 2008 Remi Collet <rpms@famillecollet.com> 5.2.5-2.###.remi
- resync with rawhide
- use bundled pcre if system one too old
- enable t1lib in GD (Fedora >= 5 and EL >= 5)

* Fri Jan 11 2008 Joe Orton <jorton@redhat.com> 5.2.5-5
- ext/date: use system timezone database

* Sat Nov 10 2007 Remi Collet <rpms@famillecollet.com> 5.2.5-1.fc8.remi
- update to 5.2.5

* Fri Nov 09 2007 Remi Collet <rpms@famillecollet.com> 5.2.4-3.fc8.remi
- resync with rawhide, F-8 rebuild

* Mon Oct 15 2007 Joe Orton <jorton@redhat.com> 5.2.4-3
- correct pcre BR version (#333021)
- restore metaphone fix (#205714)
- add READMEs to php-cli

* Sat Sep  1 2007 Remi Collet <rpms@famillecollet.com> 5.2.4-1.fc7.remi.1
- F-7 rebuild to add missing oci8

* Fri Aug 31 2007 Remi Collet <rpms@famillecollet.com> 5.2.4-1.###.remi
- update to 5.2.4

* Wed Aug 15 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-5.###.remi
- rebuild from lastest rawhide spec
- rebuild against MySQL 5.1.20

* Fri Aug 10 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 5.2.3-7
- add php-embedded sub-package

* Fri Aug 10 2007 Joe Orton <jorton@redhat.com> 5.2.3-6
- fix build with new glibc
- fix License

* Mon Jul 16 2007 Joe Orton <jorton@redhat.com> 5.2.3-5
- define php_extdir in macros.php

* Sun Jul 15 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-4.###.remi
- rebuild from lastest rawhide spec

* Mon Jul  2 2007 Joe Orton <jorton@redhat.com> 5.2.3-4
- obsolete php-dbase

* Tue Jun 19 2007 Joe Orton <jorton@redhat.com> 5.2.3-3
- add mcrypt, mhash, tidy, mssql subpackages (Dmitry Butskoy)
- enable dbase extension and package in -common

* Fri Jun  8 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-2.###.remi
- rebuild from lastest rawhide spec

* Fri Jun  8 2007 Joe Orton <jorton@redhat.com> 5.2.3-2
- update to 5.2.3 (thanks to Jeff Sheltren)

* Thu Jun 07 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-1.fc#.remi.2
- see https://www.redhat.com/archives/fedora-php-devel-list/2007-June/msg00000.html

* Tue Jun 05 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-1.fc#.remi.1
- rebuild against libtidy-0.99.0-12-20070228

* Sat Jun 02 2007 Remi Collet <rpms@famillecollet.com> 5.2.3-1.fc#.remi
- update to 5.2.3

* Tue May 22 2007 Remi Collet <rpms@famillecollet.com> 5.2.2-3.fc7.remi
- F7 rebuild with all extensions

* Tue May  8 2007 Joe Orton <jorton@redhat.com> 5.2.2-3
- rebuild against uw-imap-devel

* Fri May  4 2007 Remi Collet <rpms@famillecollet.com> 5.2.2-1.###.remi
- update to 5.2.2 (from rawhide)

* Fri May  4 2007 Joe Orton <jorton@redhat.com> 5.2.2-2
- update to 5.2.2
- synch changes from upstream recommended php.ini

* Sun Apr 01 2007 Remi Collet <rpms@famillecollet.com> 5.2.1-4.fc{3-6}.remi
- use system sqlite2 (not bundled copy)

* Sat Mar 31 2007 Remi Collet <rpms@famillecollet.com> 5.2.1-3.fc{3-6}.remi
- build --with-sqlite (in php-pdo)

* Thu Mar 29 2007 Joe Orton <jorton@redhat.com> 5.2.1-5
- enable SASL support in LDAP extension (#205772)

* Wed Mar 21 2007 Joe Orton <jorton@redhat.com> 5.2.1-4
- drop mime_magic extension (deprecated by php-pecl-Fileinfo)

* Sat Feb 17 2007 Remi Collet <rpms@famillecollet.com> 5.2.1-2.fc{3-6}.remi
- latest patches from rawhide
- fix regression in str_{i,}replace (from upstream)
- keep memory_limit to 128M (defaut php-5.2.1 value)

* Thu Feb 15 2007 Joe Orton <jorton@redhat.com> 5.2.1-2
- update to 5.2.1
- add Requires(pre) for httpd
- trim %%changelog to versions >= 5.0.0

* Fri Feb 09 2007 Remi Collet <rpms@famillecollet.com> 5.2.1-1.fc{3-6}.remi
- update to 5.2.1
- remove php-5.1.6-curl716.patch and php-5.2.0-filterm4.patch (included upstream)

* Thu Feb  8 2007 Joe Orton <jorton@redhat.com> 5.2.0-10
- bump default memory_limit to 32M (#220821)
- mark config files noreplace again (#174251)
- drop trailing dots from Summary fields
- use standard BuildRoot
- drop libtool15 patch (#226294)

* Sat Feb 03 2007 Remi Collet <rpms@famillecollet.com> 5.2.0-5.fc{3-6}.remi
- rebuild from rawhide
- del Requires libclntsh.so.10.1 (not provided by Oracle RPM)
- build with oracle-instantclient 10.2.0.3

* Tue Jan 30 2007 Joe Orton <jorton@redhat.com> 5.2.0-9
- add php(api), php(zend-abi) provides (#221302)
- package /usr/share/php and append to default include_path (#225434)

* Wed Dec 20 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-4.fc{3-6}.remi
- rebuild from rawhide

* Tue Dec  5 2006 Joe Orton <jorton@redhat.com> 5.2.0-8
- fix filter.h installation path
- fix php-zend-abi version (Remi Collet, #212804)

* Fri Dec 01 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-3.fc{3-6}.remi
- rebuild from rawhide

* Mon Nov 27 2006 Joe Orton <jorton@redhat.com> 5.2.0-5
- build json and zip shared, in -common (Remi Collet, #215966)
- obsolete php-json and php-pecl-zip
- build readline extension into /usr/bin/php* (#210585)
- change module subpackages to require php-common not php (#177821)

* Thu Nov 16 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-2.fc6.remi
- rebuild with rawhide patches

* Wed Nov 15 2006 Joe Orton <jorton@redhat.com> 5.2.0-4
- provide php-zend-abi (#212804)
- add /etc/rpm/macros.php exporting interface versions
- synch with upstream recommended php.ini

* Wed Nov 15 2006 Joe Orton <jorton@redhat.com> 5.2.0-3
- update to 5.2.0 (#213837)
- php-xml provides php-domxml (#215656)
- fix php-pdo-abi provide (#214281)

* Sat Nov  4 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-1.1.fc6.remi
- split php-json

* Thu Nov  2 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-1.fc{3-6}.remi
- update to 5.2.0 final
- add disclaimer

* Sat Oct 14 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-0.200610140830.fc5.remi
- latest snapshot

* Sun Oct  8 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-0.200610081430.fc5.remi
- latest snapshot

* Sun Oct  1 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-0.200610011230.fc5.remi
- latest snapshot for http://bugs.php.net/bug.php?id=37103

* Sun Sep 17 2006 Remi Collet <rpms@famillecollet.com> 5.2.0-0.200609171630.fc5.remi
- first try for php 5.2 from snaps.php.net
- add Requires pcre >= 6.6

* Thu Aug 31 2006 Remi Collet <rpms@famillecollet.com> 5.1.6-2.fc{3,4,5}.remi
- rebuild from FC3, FC4 & FC5 (from rawhide)

* Tue Aug 29 2006 Joe Orton <jorton@redhat.com> 5.1.6-2
- update to 5.1.6 (security fixes)
- bump default memory_limit to 16M (#196802)

* Sun Aug 20 2006 Remi Collet <rpms@famillecollet.com> 5.1.5-1.fc{3,4,5}.remi
- update to 5.1.5

* Mon Jul 24 2006 Remi Collet <rpms@famillecollet.com> 5.1.4-3.fc{3,4,5}.remi
- path to install libmbfl headers : http://bugs.php.net/bug.php?id=37103

* Sat Jun 24 2006 Remi Collet <rpms@famillecollet.com> 5.1.4-2.fc{3,4,5}.remi
- rebuild fromFC3, FC4 & FC5 (from rawhide)
- build with oracle-instantclient 10.2.0.2
- requires libclntsh.so.10.1 (not oracle-instantclient-basic)

* Fri Jun  9 2006 Joe Orton <jorton@redhat.com> 5.1.4-8
- Provide php-posix (#194583)
- only provide php-pcntl from -cli subpackage
- add missing defattr's (thanks to Matthias Saou)

* Fri Jun  9 2006 Joe Orton <jorton@redhat.com> 5.1.4-7
- move Obsoletes for php-openssl to -common (#194501)
- Provide: php-cgi from -cli subpackage

* Fri Jun  2 2006 Joe Orton <jorton@redhat.com> 5.1.4-6
- split out php-cli, php-common subpackages (#177821)
- add php-pdo-abi version export (#193202)

* Wed May 24 2006 Radek Vokal <rvokal@redhat.com> 5.1.4-5.1
- rebuilt for new libnetsnmp

* Thu May 18 2006 Joe Orton <jorton@redhat.com> 5.1.4-5
- provide mod_php (#187891)
- provide php-cli (#192196)
- use correct LDAP fix (#181518)
- define _GNU_SOURCE in php_config.h and leave it defined
- drop (circular) dependency on php-pear

* Sat May 06 2006 Remi Collet <rpms@famillecollet.com> 5.1.4-1.fc{3,4,5}.remi
- update to 5.1.4

* Fri May 05 2006 Remi Collet <rpms@famillecollet.com> 5.1.3-1.fc{3,4,5}.remi
- rebuild with additional packages

* Wed May  3 2006 Joe Orton <jorton@redhat.com> 5.1.3-3
- update to 5.1.3

* Mon Apr 17 2006 Remi Collet <rpms@famillecollet.com> 5.1.2-5.2.fc5.remi
- path to install libmbfl headers : http://bugs.php.net/bug.php?id=37103

* Fri Apr  7 2006 Joe Orton <jorton@redhat.com> 5.1.2-5.1
- fix use of LDAP on 64-bit platforms (#181518)

* Sun Apr 02 2006 Remi Collet <rpms@famillecollet.com> 5.1.2-5.fc5.remi
- add dbase, readline & tidy from php-extras
- build for FC5 (for mssql & oci8 only)

* Tue Feb 28 2006 Joe Orton <jorton@redhat.com> 5.1.2-5
- provide php-api (#183227)
- add provides for all builtin modules (Tim Jackson, #173804)
- own %%{_libdir}/php/pear for PEAR packages (per #176733)
- add obsoletes to allow upgrade from FE4 PDO packages (#181863)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5.1.2-4.3
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5.1.2-4.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Joe Orton <jorton@redhat.com> 5.1.2-4
- rebuild for new libc-client soname

* Mon Jan 16 2006 Joe Orton <jorton@redhat.com> 5.1.2-3
- only build xmlreader and xmlwriter shared (#177810)

* Sat Jan 14 2006 Remi Collet <remi.collet@univ-reims.fr> 5.1.2-2.fc{3,4}.remi
- update to 5.1.2 (see #177810)

* Fri Jan 13 2006 Joe Orton <jorton@redhat.com> 5.1.2-2
- update to 5.1.2

* Sat Jan  7 2006 Remi Collet <remi.collet@univ-reims.fr> 5.1.1-2.fc{3,4}.remi
- rebuild with mhash and mcrypt

* Thu Jan  5 2006 Joe Orton <jorton@redhat.com> 5.1.1-8
- rebuild again

* Mon Jan  2 2006 Joe Orton <jorton@redhat.com> 5.1.1-7
- rebuild for new net-snmp

* Mon Dec 12 2005 Joe Orton <jorton@redhat.com> 5.1.1-6
- enable short_open_tag in default php.ini again (#175381)

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  8 2005 Joe Orton <jorton@redhat.com> 5.1.1-5
- require net-snmp for php-snmp (#174800)

* Sun Dec  4 2005 Joe Orton <jorton@redhat.com> 5.1.1-4
- add /usr/share/pear back to hard-coded include_path (#174885)

* Sat Dec  3 2005 Remi Collet <remi.collet@univ-reims.fr> 5.1.1-2.fc#.remi
- rebuild for FC3 et FC4 (with oci8 and mssql)

* Mon Nov 28 2005 Joe Orton <jorton@redhat.com> 5.1.1-2
- update to 5.1.1
- remove pear subpackage
- enable pdo extensions (php-pdo subpackage)
- remove non-standard conditional module builds
- enable xmlreader extension

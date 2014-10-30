#
# Interface versions exposed by PHP:
# 
%php_core_api @PHP_APIVER@
%php_zend_api @PHP_ZENDVER@
%php_pdo_api  @PHP_PDOVER@
%php_version  @PHP_VERSION@

%php_extdir    %{_libdir}/php54/modules
%php_ztsextdir %{_libdir}/php54-zts/modules

%php_inidir    %{_sysconfdir}/php54.d
%php_ztsinidir %{_sysconfdir}/php54-zts.d

%php_incldir    %{_includedir}/php54
%php_ztsincldir %{_includedir}/php54-zts

%__php         %{_bindir}/php54
%__ztsphp      %{_bindir}/zts-php54

dnl -*-autoconf-*-
dnl bcm2835: Autoconf script
dnl 
dnl $Id: configure.in,v 1.1 2012/12/01 22:56:52 mikem Exp mikem $
dnl (C) 2016 Jon McClintock (jammer@weak.org)

dnl Dont forget to update ADS1256_VERSION and .tar.gz in ads1256.h
dnl and the zip file.
AC_INIT([ads1256], [0.01], [jammer@weak.org])

AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE()
LT_INIT()
AC_CHECK_LIB([bcm2835], [bcm2835_init])
AC_PROG_CC
AC_CONFIG_MACRO_DIR([m4])
AC_OUTPUT(Makefile src/Makefile examples/Makefile)

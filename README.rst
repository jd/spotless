Introduction
============

spotless is a set of flake8 plugins that test and enforce the good Python
guidelines.

Installation
============

spotless is available from pypi, so just run:

  ``pip install spotless``

This will install ``flake8``, the ``hacking`` extension and ``spotless``.

Origin
======

I am too pedantic sometimes about good code, and those extensions were not
possible to put into ``hacking`` itself, the OpenStack hacking guideline tool.

Versioning
==========

spotless uses the major.minor.maintenance release notation, where maintenance
releases cannot contain new checks.  This way projects can gate on hacking
by pinning on the major.minor number while accepting maintenance updates
without being concerned that a new version will break the gate with a new
check.

# Copyright 2013 Google Inc. All Rights Reserved.

"""Does some initial setup and checks for all the bootstrapping scripts."""


from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys


# We don't want to import any libraries at this point so we handle py2/3
# manually.
SITE_PACKAGES = 'CLOUDSDK_PYTHON_SITEPACKAGES'
VIRTUAL_ENV = 'VIRTUAL_ENV'
if sys.version_info[0] == 2:
  SITE_PACKAGES = SITE_PACKAGES.encode('utf-8')
  VIRTUAL_ENV = VIRTUAL_ENV.encode('utf-8')


# If we're in a virtualenv, always import site packages. Also, upon request.
# We can't import anything from googlecloudsdk here so we are just going to
# assume no one has done anything as silly as to put any unicode in either of
# these env vars.
import_site_packages = (os.environ.get(SITE_PACKAGES) or
                        os.environ.get(VIRTUAL_ENV))

if import_site_packages:
  # pylint:disable=unused-import
  # pylint:disable=g-import-not-at-top
  import site

# Put Google Cloud CLI libs on the path
root_dir = os.path.normpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', '..'))
lib_dir = os.path.join(root_dir, 'lib')
third_party_dir = os.path.join(lib_dir, 'third_party')

sys.path = [lib_dir, third_party_dir] + sys.path

# When python is not invoked with the -S option, it can preload google module
# via .pth file setting its __path__. After this happens, our vendored google
# package may not in the __path__. After our vendored dependency directory is
# put at the first place in the sys.path, google module should be reloaded,
# so that our vendored copy can be preferred.
if 'google' in sys.modules:
  import google  # pylint: disable=g-import-not-at-top
  try:
    reload(google)
  except NameError:
    import importlib  # pylint: disable=g-import-not-at-top
    importlib.reload(google)


# pylint: disable=g-import-not-at-top
from googlecloudsdk.core.util import platforms


# Add more methods to this list for universal checks that need to be performed
def DoAllRequiredChecks():
  if not platforms.PythonVersion().IsCompatible():
    sys.exit(1)


DoAllRequiredChecks()

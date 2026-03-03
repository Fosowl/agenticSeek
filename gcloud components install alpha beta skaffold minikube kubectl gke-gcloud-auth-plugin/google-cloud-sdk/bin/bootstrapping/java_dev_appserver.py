# Copyright 2017 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting dev_appserver for appengine for Java."""

from __future__ import absolute_import
from __future__ import unicode_literals
import os

import bootstrapping
from googlecloudsdk.command_lib.util import java
from googlecloudsdk.core.updater import update_manager


# Path to the jar's directory relative to the SDK root
_JAR_DIR = os.path.join('platform', 'google_appengine', 'google', 'appengine',
                        'tools', 'java', 'lib')

# Filename of the jar
_JAR_NAME = 'appengine-tools-api.jar'

# Flags, (enable assertions)
_FLAGS = ['-ea']

# Name of the main class
_CLASSNAME = 'com.google.appengine.tools.KickStart'

# Additional arguments, comes before sys.argv.
# The KickStart main class accepts this classname as its first arg
_ARGS = [
    'com.google.appengine.tools.development.DevAppServerMain',
    '--promote_yaml'
]


def main():
  """Launches the Java dev_appserver 1."""
  update_manager.UpdateManager.EnsureInstalledAndRestart(
      ['app-engine-java'],
      command=__file__)
  java_bin = java.RequireJavaInstalled('Java local development server')
  bootstrapping.ExecuteJarTool(
      java_bin, _JAR_DIR, _JAR_NAME, _CLASSNAME, _FLAGS, *_ARGS)


if __name__ == '__main__':
  bootstrapping.DisallowIncompatiblePythonVersions()
  bootstrapping.CommandStart('dev_appserver_java', component_id='core')
  bootstrapping.CheckUpdates('dev_appserver_java')
  main()

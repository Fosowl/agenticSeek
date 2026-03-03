#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting dev_appserver for appengine for python."""

from __future__ import absolute_import
from __future__ import unicode_literals
import os
import sys

from bootstrapping import bootstrapping
from googlecloudsdk.api_lib.app import wrapper_util
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.emulators import datastore_util
from googlecloudsdk.command_lib.util import java
from googlecloudsdk.core import metrics
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import platforms


def main():
  """Launches dev_appserver.py."""
  argv = bootstrapping.GetDecodedArgv()
  runtimes = wrapper_util.GetRuntimes(argv[1:])
  options = wrapper_util.ParseDevAppserverFlags(sys.argv[1:])
  if options.support_datastore_emulator:
    java.RequireJavaInstalled(datastore_util.DATASTORE_TITLE, min_version=8)
  components = wrapper_util.GetComponents(runtimes)
  components.append('cloud-datastore-emulator')
  update_manager.UpdateManager.EnsureInstalledAndRestart(
      components,
      command=__file__)

  args = [
      '--skip_sdk_update_check=True'
  ]

  google_analytics_client_id = metrics.GetCIDIfMetricsEnabled()
  google_analytics_user_agent = metrics.GetUserAgentIfMetricsEnabled()
  if google_analytics_client_id:
    args.extend([
        '--google_analytics_client_id={}'.format(google_analytics_client_id),
        '--google_analytics_user_agent={}'.format(google_analytics_user_agent)
    ])

  # Pass the path to cloud datastore emulator to dev_appserver.
  # realpath is needed in the case where __file__ is a path containing symlinks.
  sdk_root = os.path.dirname(
      os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
  emulator_dir = os.path.join(sdk_root, 'platform', 'cloud-datastore-emulator')
  emulator_script = (
      'cloud_datastore_emulator.cmd' if platforms.OperatingSystem.IsWindows()
      else 'cloud_datastore_emulator')
  args.append('--datastore_emulator_cmd={}'.format(
      os.path.join(emulator_dir, emulator_script)))

  bootstrapping.ExecutePythonTool(
      os.path.join('platform', 'google_appengine'), 'dev_appserver.py', *args)


if __name__ == '__main__':
  bootstrapping.DisallowIncompatiblePythonVersions()
  try:
    bootstrapping.CommandStart('dev_appserver', component_id='core')
    bootstrapping.CheckUpdates('dev_appserver')
    main()
  except Exception as e:  # pylint: disable=broad-except
    exceptions.HandleError(e, 'dev_appserver')

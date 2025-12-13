#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""Do initial setup for the Cloud CLI."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import bootstrapping

# pylint:disable=g-bad-import-order
import argparse
import os
import sys

from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import platforms_install
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.updater import python_manager
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import encoding
from googlecloudsdk.core.util import platforms
from googlecloudsdk import gcloud_main

# pylint:disable=superfluous-parens

_CLI = gcloud_main.CreateCLI([])


def ParseArgs():
  """Parse args for the installer, so interactive prompts can be avoided."""

  def Bool(s):
    return s.lower() in ['true', '1']

  parser = argparse.ArgumentParser()

  parser.add_argument(
      '--usage-reporting',
      default=None,
      type=Bool,
      help='(true/false) Enable anonymous usage reporting.',
  )
  parser.add_argument(
      '--screen-reader',
      default=None,
      type=Bool,
      help='(true/false) Enable screen reader mode.',
  )
  parser.add_argument(
      '--universe-domain',
      default=None,
      help=(
          'Universe domain to default to. If specified, sets the'
          ' [core/universe_domain] property installation-wide.'
      ),
  )
  parser.add_argument(
      '--rc-path',
      help=(
          'Profile to update with PATH and completion. If'
          ' given without --command-completion or'
          ' --path-update in "quiet" mode, a line will be'
          ' added to this profile for both command completion'
          ' and path updating.'
      ),
  )
  parser.add_argument(
      '--command-completion',
      '--bash-completion',
      default=None,
      type=Bool,
      help=(
          '(true/false) Add a line for command completion in'
          ' the profile. In "quiet" mode, if True and you do'
          ' not provide--rc-path, the default profile'
          ' will be updated.'
      ),
  )
  parser.add_argument(
      '--path-update',
      default=None,
      type=Bool,
      help=(
          '(true/false) Add a line for path updating in the'
          ' profile. In "quiet" mode, if True and you do not'
          ' provide --rc-path, the default profile will be'
          ' updated.'
      ),
  )
  parser.add_argument(
      '--disable-installation-options',
      action='store_true',
      help='DEPRECATED.  This flag is no longer used.',
  )
  parser.add_argument(
      '--override-components',
      nargs='*',
      help=(
          'Override the components that would be installed by '
          'default and install these instead.'
      ),
  )
  parser.add_argument(
      '--additional-components',
      nargs='+',
      help=(
          'Additional components to install by default.  These'
          ' components will either be added to the default install '
          'list, or to the override-components (if provided).'
      ),
  )
  parser.add_argument(
      '--update-installed-components',
      action='store_true',
      help=(
          'Update previously installed components. Checks the install folder '
          'to make sure that there are no installed components that need '
          'to be updated. This is currently just used for updating gcloud '
          'via homebrew.'
      )
  )
  # Must have a None default so properties are not always overridden when the
  # arg is not provided.
  parser.add_argument(
      '--quiet',
      '-q',
      default=None,
      action=actions.StoreConstProperty(
          properties.VALUES.core.disable_prompts, True
      ),
      help=(
          'Disable all interactive prompts. If input is '
          'required, defaults will be used or an error will be '
          'raised'
      ),
  )
  parser.add_argument(
      '--install-python',
      default=True,
      type=Bool,
      help='(true/false) Attempt to install Python. MacOS only.',
  )
  parser.add_argument(
      '--no-compile-python',
      action='store_false',
      help=(
          'False. If set, skips python compilation after component'
          ' installation.'
      ),
  )

  return parser.parse_args(bootstrapping.GetDecodedArgv()[1:])


def Prompts(usage_reporting, universe_domain):
  """Display prompts to opt out of usage reporting.

  Args:
    usage_reporting: bool, If True, enable usage reporting. If None, check the
      environmental variable. If None, check if its alternate release channel.
      If not, ask.
    universe_domain: str, if specified and not 'googleapis.com', set
      usage-reporting to False.
  """
  if usage_reporting is None:

    if (
        encoding.GetEncodedValue(
            os.environ, 'CLOUDSDK_CORE_DISABLE_USAGE_REPORTING'
        )
        is not None
    ):
      usage_reporting = not encoding.GetEncodedValue(
          os.environ, 'CLOUDSDK_CORE_DISABLE_USAGE_REPORTING'
      )
    else:
      if (
          universe_domain is not None
          and universe_domain != properties.VALUES.core.universe_domain.default
      ):
        usage_reporting = False
      elif config.InstallationConfig.Load().IsAlternateReleaseChannel():
        usage_reporting = True
        print("""
    Usage reporting is always on for alternate release channels.
    """)
      else:
        print("""
To help improve the quality of this product, we collect anonymized usage data
and anonymized stacktraces when crashes are encountered; additional information
is available at <https://cloud.google.com/sdk/usage-statistics>. This data is
handled in accordance with our privacy policy
<https://cloud.google.com/terms/cloud-privacy-notice>. You may choose to opt in this
collection now (by choosing 'Y' at the below prompt), or at any time in the
future by running the following command:

    gcloud config set disable_usage_reporting false
""")

        usage_reporting = console_io.PromptContinue(
            prompt_string='Do you want to help improve the Google Cloud CLI',
            default=False)
  properties.PersistProperty(
      properties.VALUES.core.disable_usage_reporting, not usage_reporting,
      scope=properties.Scope.INSTALLATION)


def GetInstalledComponents():
  # Check if .install folder already has components installed
  platform = platforms.Platform.Current()
  manager = update_manager.UpdateManager(platform_filter=platform, warn=False)
  installed_components = manager.GetCurrentVersionsInformation()
  return list(installed_components.keys())


def Install(
    override_components, update_installed_components,
    additional_components, compile_python):
  """Do the normal installation of the Cloud CLI."""
  # Install the OS specific wrapper scripts for gcloud and any pre-configured
  # components for the CLI.
  to_install = (override_components if override_components is not None
                else bootstrapping.GetDefaultInstalledComponents())

  # If there are components that are to be installed by default, this means we
  # are working with an incomplete Cloud CLI package.  This comes from the curl
  # installer or the Windows installer or downloading a seed directly.  In this
  # case, we will update to the latest version of the CLI.  If there are no
  # default components, this is a fully packaged CLI.  If there are additional
  # components requested, just install them without updating the version.
  update = bool(to_install)

  # If gcloud was previously installed, there may still be some old installed
  # components. Ensure those components are up to date. This ensures
  # upgrades outside of `gcloud components update` still update installed
  # components.
  if (update_installed_components and
      (installed_components := GetInstalledComponents())):
    to_install.extend(installed_components)

  if additional_components:
    to_install.extend(additional_components)

  InstallOrUpdateComponents(to_install, compile_python, update=update)

  # Show the list of components if there were no pre-configured ones.
  if not to_install:
    _CLI.Execute(['--quiet', 'components', 'list'])


def ReInstall(component_ids, compile_python):
  """Do a forced reinstallation of Google Cloud CLI.

  Args:
    component_ids: [str], The components that should be automatically installed.
    compile_python: bool, False if we skip compile python
  """
  to_install = bootstrapping.GetDefaultInstalledComponents()
  to_install.extend(component_ids)

  # We always run in update mode here because we are reinstalling and trying
  # to get the latest version anyway.
  InstallOrUpdateComponents(component_ids, compile_python, update=True)


def InstallOrUpdateComponents(component_ids, compile_python, update):
  """Installs or updates the given components.

  Args:
    component_ids: [str], The components to install or update.
    compile_python: bool, False if we skip compile python
    update: bool, True if we should run update, False to run install.  If there
      are no components to install, this does nothing unless in update mode (in
      which case everything gets updated).
  """
  # If we are in installation mode, and there are no specific components to
  # install, there is nothing to do.  If there are no components in update mode
  # things will still get updated to latest.
  if not update and not component_ids:
    return

  print(
      """
This will install all the core command line tools necessary for working with
the Google Cloud Platform.
"""
  )

  verb = 'update' if update else 'install'
  execute_arg_list = ['--quiet', 'components', verb]
  if not compile_python:
    execute_arg_list.append('--no-compile-python')
  else:
    execute_arg_list.append('--compile-python')
  _CLI.Execute(
      execute_arg_list + component_ids
  )


def main():
  properties.VALUES.context_aware.use_client_certificate.Set(False)

  pargs = ParseArgs()
  if pargs.screen_reader is not None:
    properties.PersistProperty(properties.VALUES.accessibility.screen_reader,
                               pargs.screen_reader,
                               scope=properties.Scope.INSTALLATION)
  if pargs.universe_domain is not None:
    properties.PersistProperty(properties.VALUES.core.universe_domain,
                               pargs.universe_domain,
                               scope=properties.Scope.INSTALLATION)
  update_manager.RestartIfUsingBundledPython(sdk_root=config.Paths().sdk_root,
                                             command=__file__)
  reinstall_components = encoding.GetEncodedValue(
      os.environ, 'CLOUDSDK_REINSTALL_COMPONENTS')
  try:
    if reinstall_components:
      ReInstall(reinstall_components.split(','), pargs.no_compile_python)
    else:
      Prompts(pargs.usage_reporting, pargs.universe_domain)
      bootstrapping.CommandStart('INSTALL', component_id='core')
      if not config.INSTALLATION_CONFIG.disable_updater:
        Install(
            pargs.override_components,
            pargs.update_installed_components,
            pargs.additional_components,
            pargs.no_compile_python,
        )

      platforms_install.UpdateRC(
          completion_update=pargs.command_completion,
          path_update=pargs.path_update,
          rc_path=pargs.rc_path,
          bin_path=bootstrapping.BIN_DIR,
          sdk_root=bootstrapping.SDK_ROOT,
      )
      if pargs.install_python:
        python_manager.PromptAndInstallPythonOnMac()
      print("""\

For more information on how to get started, please visit:
  https://cloud.google.com/sdk/docs/quickstarts

""")
  except exceptions.ToolException as e:
    print(e)
    sys.exit(1)


if __name__ == '__main__':
  main()

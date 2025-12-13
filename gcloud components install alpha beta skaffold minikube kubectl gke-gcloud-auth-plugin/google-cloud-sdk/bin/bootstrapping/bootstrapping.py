# Copyright 2013 Google Inc. All Rights Reserved.

"""Common bootstrapping functionality used by the wrapper scripts."""

# Disables import order warning and unused import.  Setup changes the python
# path so cloud sdk imports will actually work, so it must come first.
# pylint: disable=C6203
# pylint: disable=W0611
from __future__ import absolute_import
from __future__ import unicode_literals

# Python 3 is strict about imports and we use this file in different ways, which
# makes sub-imports difficult. In general, when a script is executed, that
# directory is put on the PYTHONPATH. The issue is that some of the wrapper
# scripts are executed from within the bootstrapping/ directory and some are
# executed from within the bin/ directory.
# pylint: disable=g-statement-before-imports
if '.' in __name__:
  # Here, __name__ will be bootstrapping.bootstrapping. This indicates that this
  # file was loaded as a member of package bootstrapping. This in turn indicates
  # that the main file that was executed was not in the bootstrapping directory,
  # so bin/ is on the path and bootstrapping is considered a python package.
  # Do an import of setup from this current package.
  from . import setup  # pylint:disable=g-import-not-at-top
else:
  # In this case, __name__ is bootstrapping, which indicates that the main
  # script was executed from within this directory meaning that Python doesn't
  # consider this a package but rather the root of the PYTHONPATH. We can't do
  # the above import because since we are not in a package, the '.' doesn't
  # refer to anything. Just do a direct import which will find setup on the
  # PYTHONPATH (which is just this directory).
  import setup  # pylint:disable=g-import-not-at-top

import gcloud
import sys
# Reorder sys.path if needed right now before more modules loaded and cached
sys.path = gcloud.reorder_sys_path(sys.path)

# pylint: disable=g-import-not-at-top
import json
# pylint: enable=g-import-not-at-top
import os
import platform

from googlecloudsdk.core import config
from googlecloudsdk.core import execution_utils
from googlecloudsdk.core import metrics
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_attr
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core.updater import local_state
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import encoding
from googlecloudsdk.core.util import files
from googlecloudsdk.core.util import platforms
from six.moves import input


BOOTSTRAPPING_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_DIR = os.path.dirname(BOOTSTRAPPING_DIR)
SDK_ROOT = os.path.dirname(BIN_DIR)


def DisallowIncompatiblePythonVersions():
  if not platforms.PythonVersion().IsCompatible():
    sys.exit(1)


def GetDecodedArgv():
  return [console_attr.Decode(arg) for arg in sys.argv]


def _FullPath(tool_dir, exec_name):
  return os.path.join(SDK_ROOT, tool_dir, exec_name)


def ExecutePythonTool(tool_dir, exec_name, *args):
  """Execute the given python script with the given args and command line.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  py_path = None  # Let execution_utils resolve the path.
  # Gsutil allows users to set the desired Python interpreter using a separate
  # environment variable, so as to allow users to run gsutil using Python 3
  # without forcing the rest of Google Cloud CLI to use Python 3 (as it would
  # likely break at the time this comment was written).
  extra_popen_kwargs = {}
  if exec_name == 'gsutil':
    gsutil_py = encoding.GetEncodedValue(os.environ, 'CLOUDSDK_GSUTIL_PYTHON')
    # Since PY3, Python closes open FDs in child processes, since we need them
    # open for completions to work we set the close_fds kwarg to Popen.
    extra_popen_kwargs['close_fds'] = False
    if gsutil_py:
      py_path = gsutil_py

  if exec_name == 'bq.py':
    bq_py = encoding.GetEncodedValue(os.environ, 'CLOUDSDK_BQ_PYTHON')
    if bq_py:
      py_path = bq_py

  _ExecuteTool(
      execution_utils.ArgsForPythonTool(
          _FullPath(tool_dir, exec_name), *args, python=py_path),
      **extra_popen_kwargs)


def ExecuteJarTool(java_bin, jar_dir, jar_name, classname, flags=None, *args):
  """Execute a given jar with the given args and command line.

  Args:
    java_bin: str, path to the system Java binary
    jar_dir: str, the directory the jar is located in
    jar_name: str, file name of the jar under tool_dir
    classname: str, name of the main class in the jar
    flags: [str], flags for the java binary
    *args: args for the command
  """
  flags = flags or []
  jar_path = _FullPath(jar_dir, jar_name)
  classname_arg = [classname] if classname else []
  java_args = ['-cp', jar_path] + flags + classname_arg + list(args)
  _ExecuteTool(
      execution_utils.ArgsForExecutableTool(java_bin, *java_args))


def ExecuteJavaClass(java_bin,
                     jar_dir,
                     main_jar,
                     main_class,
                     java_flags=None,
                     main_args=None):
  """Execute a given java class within a directory of jars.

  Args:
    java_bin: str, path to the system Java binary
    jar_dir: str, directory of jars to put on class path
    main_jar: str, main jar (placed first on class path)
    main_class: str, name of the main class in the jar
    java_flags: [str], flags for the java binary
    main_args: args for the command
  """
  java_flags = java_flags or []
  main_args = main_args or []
  jar_dir_path = os.path.join(SDK_ROOT, jar_dir, '*')
  main_jar_path = os.path.join(SDK_ROOT, jar_dir, main_jar)
  classpath = main_jar_path + os.pathsep + jar_dir_path
  java_args = (['-cp', classpath]
               + list(java_flags)
               + [main_class]
               + list(main_args))
  _ExecuteTool(execution_utils.ArgsForExecutableTool(java_bin, *java_args))


def ExecuteShellTool(tool_dir, exec_name, *args):
  """Execute the given bash script with the given args.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  _ExecuteTool(
      execution_utils.ArgsForExecutableTool(_FullPath(tool_dir, exec_name),
                                            *args))


def ExecuteCMDTool(tool_dir, exec_name, *args):
  """Execute the given batch file with the given args.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  _ExecuteTool(
      execution_utils.ArgsForCMDTool(_FullPath(tool_dir, exec_name), *args))


def _GetToolEnv():
  env = dict(os.environ)
  encoding.SetEncodedValue(env, 'CLOUDSDK_WRAPPER', '1')
  encoding.SetEncodedValue(env, 'CLOUDSDK_VERSION', config.CLOUD_SDK_VERSION)
  encoding.SetEncodedValue(env, 'CLOUDSDK_PYTHON',
                           execution_utils.GetPythonExecutable())
  return env


def _ExecuteTool(args, **extra_popen_kwargs):
  """Executes a new tool with the given args, plus the args from the cmdline.

  Args:
    args: [str], The args of the command to execute.
    **extra_popen_kwargs: [dict], kwargs to be unpacked in Popen call for tool.
  """
  execution_utils.Exec(
      args + sys.argv[1:], env=_GetToolEnv(), **extra_popen_kwargs)


def GetDefaultInstalledComponents():
  """Gets the list of components to install by default.

  Returns:
    list(str), The component ids that should be installed.  It will return []
    if there are no default components, or if there is any error in reading
    the file with the defaults.
  """
  default_components_file = os.path.join(BOOTSTRAPPING_DIR,
                                         '.default_components')
  try:
    with open(default_components_file) as f:
      return json.load(f)
  # pylint:disable=bare-except, If the file does not exist or is malformed,
  # we don't want to expose this as an error.  Setup will just continue
  # without installing any components by default and will tell the user how
  # to install the components they want manually.
  except:
    pass
  return []


def WarnAndExitOnBlockedCommand(args, blocked_commands):
  """Block certain subcommands, warn the user, and exit.

  Args:
    args: the command line arguments, including the 0th argument which is
      the program name.
    blocked_commands: a map of blocked commands to the messages that should be
      printed when they're run.
  """
  bad_arg = None
  for arg in args[1:]:
    # Flags are skipped and --flag=value are skipped. It is possible for
    # '--flag value' to result in a false positive if value happens to be a
    # blocked command.
    if arg and arg[0] == '-':
      continue
    if arg in blocked_commands:
      bad_arg = arg
      break

  blocked = bad_arg is not None

  if blocked:
    sys.stderr.write('It looks like you are trying to run "%s %s".\n'
                     % (args[0], bad_arg))
    sys.stderr.write('The "%s" command is no longer needed with '
                     'Google Cloud CLI.\n' % bad_arg)
    sys.stderr.write(blocked_commands[bad_arg] + '\n')
    answer = input('Really run this command? (y/N) ')
    if answer not in ['y', 'Y']:
      sys.exit(1)


def CheckUpdates(command_path):
  """Check for updates and inform the user.

  Args:
    command_path: str, The '.' separated path of the command that is currently
      being run (i.e. gcloud.foo.bar).
  """
  try:
    update_manager.UpdateManager.PerformUpdateCheck(command_path=command_path)
  # pylint:disable=broad-except, We never want this to escape, ever. Only
  # messages printed should reach the user.
  except Exception:
    pass


def CommandStart(command_name, component_id=None, version=None):
  """Logs that the given command is being executed.

  Args:
    command_name: str, The name of the command being executed.
    component_id: str, The component id that this command belongs to.  Used for
      version information if version was not specified.
    version: str, Directly use this version instead of deriving it from
      component.
  """
  if version is None and component_id:
    version = local_state.InstallationState.VersionForInstalledComponent(
        component_id)
  metrics.Executions(command_name, version)


def GetActiveProjectAndAccount():
  """Get the active project name and account for the active credentials.

  For use with wrapping legacy tools that take projects and credentials on
  the command line.

  Returns:
    (str, str), A tuple whose first element is the project, and whose second
    element is the account.
  """
  project_name = properties.VALUES.core.project.Get(validate=False)
  account = properties.VALUES.core.account.Get(validate=False)
  return (project_name, account)


def GetActiveImpersonateServiceAccount():
  """Get the active impersonate_service_account property.

  For use with wrapping legacy tools that take impersonate_service_account on
  the command line.

  Returns:
    str, The name of the service account to impersonate.
  """
  return properties.VALUES.auth.impersonate_service_account.Get(validate=False)


def ReadFileContents(*path_parts):
  """Returns file content at specified relative path wrt SDK root path."""
  return files.ReadFileContents(os.path.join(SDK_ROOT, *path_parts)).strip()


# Register some other sources for credentials and project.
c_store.GceCredentialProvider().Register()

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sources.tools import sandbox
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.PyInterpreter import PyInterpreter

_SECRETS = {
    "OPENAI_API_KEY": "sk-should-not-leak",
    "AGENTICSEEK_API_TOKEN": "api-token-should-not-leak",
    "github_token": "lowercase-should-not-leak",
    "DB_PASSWORD": "pw-should-not-leak",
}


@unittest.skipUnless(os.name == "posix", "POSIX process isolation")
class TestScrubbedEnv(unittest.TestCase):
    """Agent code must not read provider keys or the API token from its env."""

    def test_drops_credentials_and_keeps_runtime_vars(self):
        with mock.patch.dict(os.environ, {**_SECRETS, "PATH": "/usr/bin", "LANG": "C"}):
            env = sandbox.scrubbed_env()
        self.assertFalse(set(_SECRETS) & set(env))
        self.assertEqual((env["PATH"], env["LANG"]), ("/usr/bin", "C"))

    def test_bash_and_python_children_cannot_see_secrets(self):
        work_dir = tempfile.mkdtemp()
        with mock.patch.dict(os.environ, {**_SECRETS, "WORK_DIR": work_dir}):
            bash_output = BashInterpreter().execute(["env"])
            python_output = PyInterpreter().execute(["import os; print(dict(os.environ))"])
        for leaked in _SECRETS.values():
            self.assertNotIn(leaked, bash_output)
            self.assertNotIn(leaked, python_output)
        self.assertIn("PATH=", bash_output)


@unittest.skipUnless(os.name == "posix", "POSIX process isolation")
class TestExecIdentity(unittest.TestCase):
    """The uid drop applies only to a root backend with AGENTICSEEK_EXEC_UID set."""

    def _identity(self, env, euid):
        with mock.patch.dict(os.environ, env), mock.patch("os.geteuid", return_value=euid):
            return sandbox.exec_identity()

    def test_no_drop_without_configured_uid(self):
        with mock.patch.dict(os.environ):
            os.environ.pop(sandbox.EXEC_UID_ENV, None)
            self.assertIsNone(self._identity({}, euid=0))

    def test_no_drop_when_backend_is_not_root(self):
        self.assertIsNone(self._identity({sandbox.EXEC_UID_ENV: "1000"}, euid=501))

    def test_uid_zero_means_no_drop(self):
        self.assertIsNone(self._identity({sandbox.EXEC_UID_ENV: "0"}, euid=0))

    def test_root_backend_drops_to_uid_with_matching_gid(self):
        env = {sandbox.EXEC_UID_ENV: "1000", sandbox.EXEC_GID_ENV: ""}
        self.assertEqual(self._identity(env, euid=0), (1000, 1000))

    def test_explicit_gid_wins(self):
        env = {sandbox.EXEC_UID_ENV: "1000", sandbox.EXEC_GID_ENV: "2000"}
        self.assertEqual(self._identity(env, euid=0), (1000, 2000))

    def test_invalid_uid_fails_loudly(self):
        with self.assertRaises(ValueError):
            self._identity({sandbox.EXEC_UID_ENV: "agent"}, euid=0)

    def test_drop_clears_supplementary_groups_and_sets_home(self):
        env = {sandbox.EXEC_UID_ENV: "1000", sandbox.EXEC_GID_ENV: ""}
        with mock.patch.dict(os.environ, env), mock.patch("os.geteuid", return_value=0), \
                mock.patch.object(sandbox, "_home_for", return_value="/home/agent"):
            kwargs = sandbox.subprocess_isolation("/opt/workspace")
        self.assertEqual((kwargs["user"], kwargs["group"], kwargs["extra_groups"]), (1000, 1000, []))
        self.assertEqual(kwargs["env"]["HOME"], "/home/agent")


if __name__ == "__main__":
    unittest.main()

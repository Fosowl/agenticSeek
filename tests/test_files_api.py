import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sources import files_api

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


class FilesApiTestCase(unittest.TestCase):
    def setUp(self):
        self._root = tempfile.mkdtemp()
        self._work_dir = os.path.join(self._root, "workspace")
        os.makedirs(os.path.join(self._work_dir, "src"))
        self._old_work_dir = os.environ.get("WORK_DIR")
        self._old_token = os.environ.get("AGENTICSEEK_API_TOKEN")
        os.environ["AGENTICSEEK_API_TOKEN"] = "files-test-token"
        os.environ["WORK_DIR"] = self._work_dir

        app = FastAPI()
        app.include_router(files_api.router)
        self.client = TestClient(app, headers={"Authorization": "Bearer files-test-token"})

    def tearDown(self):
        if self._old_work_dir is None:
            os.environ.pop("WORK_DIR", None)
        else:
            os.environ["WORK_DIR"] = self._old_work_dir
        if self._old_token is not None:
            os.environ["AGENTICSEEK_API_TOKEN"] = self._old_token
        else:
            os.environ.pop("AGENTICSEEK_API_TOKEN", None)
        shutil.rmtree(self._root, ignore_errors=True)

    def _write(self, relative, data):
        path = os.path.join(self._work_dir, relative)
        with open(path, "wb") as handle:
            handle.write(data)
        return path


class TestListDirectory(FilesApiTestCase):
    def test_root_lists_directories_first_then_files_case_insensitive(self):
        self._write("b.txt", b"b")
        self._write("A.txt", b"a")
        response = self.client.get("/files/list")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["path"], "")
        self.assertEqual(
            [(e["name"], e["type"], e["path"]) for e in body["entries"]],
            [("src", "directory", "src"), ("A.txt", "file", "A.txt"), ("b.txt", "file", "b.txt")],
        )

    def test_nested_entries_carry_workspace_relative_paths(self):
        self._write("src/main.py", b"print(1)\n")
        body = self.client.get("/files/list", params={"path": "src"}).json()
        self.assertEqual(body["entries"][0]["path"], "src/main.py")
        self.assertEqual(body["entries"][0]["size"], 9)

    def test_traversal_outside_workspace_is_forbidden(self):
        response = self.client.get("/files/list", params={"path": "../"})
        self.assertEqual(response.status_code, 403)

    def test_symlink_escaping_workspace_is_hidden(self):
        outside = os.path.join(self._root, "secret")
        os.makedirs(outside)
        os.symlink(outside, os.path.join(self._work_dir, "escape"))
        names = [e["name"] for e in self.client.get("/files/list").json()["entries"]]
        self.assertNotIn("escape", names)
        response = self.client.get("/files/list", params={"path": "escape"})
        self.assertEqual(response.status_code, 403)

    def test_file_path_is_rejected(self):
        self._write("a.txt", b"a")
        response = self.client.get("/files/list", params={"path": "a.txt"})
        self.assertEqual(response.status_code, 400)

    def test_api_token_is_enforced_when_configured(self):
        os.environ["AGENTICSEEK_API_TOKEN"] = "s3cret"
        self.assertEqual(self.client.get("/files/list").status_code, 401)
        response = self.client.get("/files/list", headers={"Authorization": "Bearer s3cret"})
        self.assertEqual(response.status_code, 200)


class TestReadFile(FilesApiTestCase):
    def test_text_file_returns_content(self):
        self._write("src/main.py", "print('é')\n".encode())
        body = self.client.get("/files/content", params={"path": "src/main.py"}).json()
        self.assertEqual(body["kind"], "text")
        self.assertEqual(body["content"], "print('é')\n")
        self.assertFalse(body["truncated"])

    def test_large_text_file_is_truncated(self):
        self._write("big.log", b"x" * (files_api.MAX_TEXT_BYTES + 10))
        body = self.client.get("/files/content", params={"path": "big.log"}).json()
        self.assertTrue(body["truncated"])
        self.assertEqual(len(body["content"]), files_api.MAX_TEXT_BYTES)

    def test_binary_file_has_no_content(self):
        self._write("blob.bin", b"abc\x00def")
        body = self.client.get("/files/content", params={"path": "blob.bin"}).json()
        self.assertEqual(body["kind"], "binary")
        self.assertIsNone(body["content"])

    def test_image_is_reported_as_image(self):
        self._write("pic.png", PNG_BYTES)
        body = self.client.get("/files/content", params={"path": "pic.png"}).json()
        self.assertEqual((body["kind"], body["mime"]), ("image", "image/png"))

    def test_missing_file_is_not_found(self):
        response = self.client.get("/files/content", params={"path": "nope.txt"})
        self.assertEqual(response.status_code, 404)

    def test_file_outside_workspace_is_forbidden(self):
        with open(os.path.join(self._root, "secret.txt"), "w") as handle:
            handle.write("secret")
        response = self.client.get("/files/content", params={"path": "../secret.txt"})
        self.assertEqual(response.status_code, 403)


class TestRawImage(FilesApiTestCase):
    def test_image_bytes_are_served_with_image_type(self):
        self._write("pic.png", PNG_BYTES)
        response = self.client.get("/files/raw", params={"path": "pic.png"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertEqual(response.content, PNG_BYTES)

    def test_non_image_is_refused(self):
        self._write("page.html", b"<script>alert(1)</script>")
        response = self.client.get("/files/raw", params={"path": "page.html"})
        self.assertEqual(response.status_code, 415)


class TestUpload(FilesApiTestCase):
    def _upload(self, *files):
        parts = [("files", (name, data, "application/octet-stream")) for name, data in files]
        return self.client.post("/files/upload", files=parts)

    def _read(self, relative):
        with open(os.path.join(self._work_dir, relative), "rb") as handle:
            return handle.read()

    def test_files_are_saved_in_user_uploads(self):
        response = self._upload(("finance.pdf", b"%PDF-1.4"), ("notes.txt", b"hi"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["paths"],
            [".user_uploads/finance.pdf", ".user_uploads/notes.txt"],
        )
        self.assertEqual(self._read(".user_uploads/finance.pdf"), b"%PDF-1.4")

    def test_existing_file_is_never_overwritten(self):
        self._upload(("a.txt", b"first"))
        paths = self._upload(("a.txt", b"second")).json()["paths"]
        self.assertEqual(paths, [".user_uploads/a (1).txt"])
        self.assertEqual(self._read(".user_uploads/a.txt"), b"first")
        self.assertEqual(self._read(".user_uploads/a (1).txt"), b"second")

    def test_directory_parts_in_name_are_dropped(self):
        paths = self._upload(("../../escape.txt", b"x")).json()["paths"]
        self.assertEqual(paths, [".user_uploads/escape.txt"])
        self.assertFalse(os.path.exists(os.path.join(self._root, "escape.txt")))

    def test_tag_and_list_characters_are_replaced_in_name(self):
        paths = self._upload(("a<b>c,d.txt", b"x")).json()["paths"]
        self.assertEqual(paths, [".user_uploads/a_b_c_d.txt"])

    def test_name_without_file_part_is_rejected(self):
        self.assertEqual(self._upload(("..", b"x")).status_code, 400)

    def test_too_long_name_is_rejected_before_any_write(self):
        response = self._upload(("ok.txt", b"x"), ("é" * 200 + ".pdf", b"x"))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(os.path.exists(os.path.join(self._work_dir, ".user_uploads")))

    def test_too_large_upload_writes_nothing(self):
        with mock.patch.object(files_api, "MAX_UPLOAD_BYTES", 4):
            response = self._upload(("ok.txt", b"1234"), ("big.txt", b"12345"))
        self.assertEqual(response.status_code, 413)
        self.assertFalse(os.path.exists(os.path.join(self._work_dir, ".user_uploads")))

    def test_symlinked_upload_dir_is_refused(self):
        outside = os.path.join(self._root, "outside")
        os.makedirs(outside)
        os.symlink(outside, os.path.join(self._work_dir, ".user_uploads"))
        response = self._upload(("a.txt", b"x"))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(os.listdir(outside), [])



if __name__ == "__main__":
    unittest.main()

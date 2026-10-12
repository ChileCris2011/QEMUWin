import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import app_version
from tools.generate_version import generate


class VersionTests(unittest.TestCase):
    def git(self, tags="v1.1.0", distance="3", dirty=False):
        def run(root, *args):
            if args == ("rev-parse", "--short", "HEAD"):
                return "abc1234"
            if args == ("status", "--porcelain"):
                return " M main.py" if dirty else ""
            if args == ("tag", "--merged", "HEAD"):
                return tags
            if args[0] == "describe":
                self.assertIn("--match", args)
                return f"{tags.splitlines()[0]}-{distance}-gabc1234"
            if args == ("rev-list", "--count", "HEAD"):
                return "12"
            if args[0] == "rev-parse":
                return "full-head-sha"
            self.fail(f"Unexpected Git call: {args}")
        return patch.object(app_version, "_git", side_effect=run)

    def test_tag_validation(self):
        for tag in ("v1.1.0", "v1.2.0-beta.1", "v0.0.0-0", "v1.2.3-01alpha"):
            self.assertEqual(app_version.version_from_tag(tag), tag[1:])
        for tag in ("1.1.0", "v01.1.0", "v1.2", "v1.2.3-beta.01", "v1.2.3-", "v1.2.3+build"):
            with self.assertRaises(ValueError):
                app_version.version_from_tag(tag)

    def test_source_and_development_versions(self):
        cases = [
            ("v1.1.0", "0", False, False, "1.1.0"),
            ("v1.2.0-beta.1", "0", False, False, "1.2.0-beta.1"),
            ("v1.1.0", "3", False, False, "1.1.0-dev.3+abc1234"),
            ("v1.1.0", "0", True, False, "1.1.0-dev.0+abc1234.dirty"),
            ("v1.1.0", "0", False, True, "1.1.0-dev.0+abc1234"),
            ("v1.2.0-beta.1", "3", False, True, "1.2.0-beta.1.dev.3+abc1234"),
            ("invalid", "3", False, False, "0.0.0-dev.12+abc1234"),
            ("", "3", True, False, "0.0.0-dev.12+abc1234.dirty"),
        ]
        for tags, distance, dirty, development, expected in cases:
            with self.subTest(expected=expected), self.git(tags, distance, dirty):
                self.assertEqual(app_version.resolve_version(development=development), expected)

    def test_missing_git(self):
        for error in (FileNotFoundError(), subprocess.CalledProcessError(128, "git")):
            with patch.object(app_version, "_git", side_effect=error):
                self.assertEqual(app_version.resolve_version(), "0.0.0-dev")

    def test_explicit_release(self):
        for tag in ("v1.1.0", "v1.2.0-beta.1"):
            with self.git():
                self.assertEqual(app_version.resolve_version(release_tag=tag), tag[1:])
        with self.git(dirty=True), self.assertRaises(ValueError):
            app_version.resolve_version(release_tag="v1.1.0")
        with patch.object(app_version, "_git", side_effect=["tag-sha", "other-sha"]), self.assertRaises(ValueError):
            app_version.resolve_version(release_tag="v1.1.0")
        with self.assertRaises(ValueError):
            app_version.resolve_version(release_tag="vwrong")

    def test_generated_inputs_and_frozen_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("tools.generate_version.resolve_version", return_value="1.2.0-beta.1"):
                self.assertEqual(generate(root), "1.2.0-beta.1")
            snapshot = root / "build/version/build_version.json"
            self.assertEqual(json.loads(snapshot.read_text())["version"], "1.2.0-beta.1")
            self.assertEqual((root / "build/version/version.iss").read_text(), '#define MyAppVersion "1.2.0-beta.1"\n')
            self.assertTrue(snapshot.read_bytes().endswith(b"\r\n"))
            with patch.object(app_version.sys, "frozen", True, create=True), patch.object(app_version, "ROOT", snapshot.parent), patch.object(app_version, "_git", side_effect=AssertionError("Frozen runtime used Git")):
                self.assertEqual(app_version.get_app_version(), "1.2.0-beta.1")


if __name__ == "__main__":
    unittest.main()

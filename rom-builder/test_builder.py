import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import builder


class BuilderTests(unittest.TestCase):
    def demo(self, platform):
        return builder.ROOT / ("nofrendo/src/2048.nes" if platform == "nes" else "peanutgb/src/flappyboy.gb")

    def test_selection_errors(self):
        with self.assertRaises(ValueError):
            builder.validate_selection("unknown", [])
        for paths in ([], [self.demo("nes")] * 65, [self.demo("nes")] * 2, [self.demo("gbc")]):
            with self.assertRaises(ValueError):
                builder.validate_selection("nes", paths)

    def test_real_pack_both_platforms(self):
        with tempfile.TemporaryDirectory() as folder:
            for platform, config in builder.PLATFORMS.items():
                result = builder.build(platform, [self.demo(platform)], folder, False, lambda line: None)
                blob = (result / config.blob).read_bytes()
                self.assertEqual(blob[:8], b"NWROMS\0\1")
                self.assertEqual(struct.unpack_from("<I", blob, 8)[0], 1)
                self.assertFalse(list(result.glob("*.nwa")))
                self.assertTrue((result / "LISEZMOI.txt").is_file())
                self.assertTrue((result / "compilation.log").is_file())

    def test_special_names_and_multiple_roms(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = root / "Démo [1] & jeu.nes"
            second = root / "Autre jeu.NES"
            for path in (first, second):
                shutil.copy2(self.demo("nes"), path)
            result = builder.build("nes", [first, second], folder, False, lambda line: None)
            blob = (result / "roms.nes").read_bytes()
            self.assertEqual(struct.unpack_from("<I", blob, 8)[0], 2)
            self.assertEqual(first.read_bytes(), self.demo("nes").read_bytes())

    def test_invalid_rom_does_not_publish_partial_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = Path(folder) / "invalid.nes"
            bad.write_bytes(b"invalid")
            with self.assertRaisesRegex(ValueError, "refusees"):
                builder.build("nes", [self.demo("nes"), bad], folder, False, lambda line: None)
            self.assertEqual(list(Path(folder).iterdir()), [bad])

    def test_same_display_names_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [root / ("a" * 24 + suffix + ".nes") for suffix in ("1", "2")]
            for path in paths:
                shutil.copy2(self.demo("nes"), path)
            with self.assertRaises(RuntimeError):
                builder.build("nes", paths, folder, False, lambda line: None)
            self.assertEqual(set(root.iterdir()), set(paths))

    def test_existing_result_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            first = builder.build("nes", [self.demo("nes")], folder, False, lambda line: None)
            before = {p.name: p.read_bytes() for p in first.iterdir()}
            second = builder.build("nes", [self.demo("nes")], folder, False, lambda line: None)
            self.assertNotEqual(first, second)
            self.assertEqual(before, {p.name: p.read_bytes() for p in first.iterdir()})

    def test_compile_command_and_publication(self):
        real_run = builder.run_command
        for platform, config in builder.PLATFORMS.items():
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as folder:
                def fake_compile(command, cwd, emit):
                    self.assertNotIn("--install", command)
                    if any(Path(arg).name == "build.py" for arg in command):
                        output = Path(command[command.index("--output") + 1])
                        output.mkdir()
                        (output / (config.project + ".nwa")).write_bytes(b"test application")
                        (output / (config.project + ".bin")).write_bytes(b"test link")
                    else:
                        real_run(command, cwd, emit)
                with patch.object(builder, "run_command", side_effect=fake_compile), patch.object(builder, "require_tools"):
                    result = builder.build(platform, [self.demo(platform)], folder, True, lambda line: None)
                self.assertEqual((result / (config.project + ".nwa")).read_bytes(), b"test application")
                self.assertFalse(list(result.glob("*.bin")))

    def test_compile_failure_leaves_destination_unchanged(self):
        real_run = builder.run_command
        with tempfile.TemporaryDirectory() as folder:
            def fail_compile(command, cwd, emit):
                if any(Path(arg).name == "build.py" for arg in command):
                    raise RuntimeError("compiler absent")
                real_run(command, cwd, emit)
            with patch.object(builder, "run_command", side_effect=fail_compile), patch.object(builder, "require_tools"):
                with self.assertRaisesRegex(RuntimeError, "compiler absent"):
                    builder.build("nes", [self.demo("nes")], folder, True, lambda line: None)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_worker_protocol(self):
        with tempfile.TemporaryDirectory() as folder:
            request = {"platform": "gbc", "paths": [str(self.demo("gbc"))],
                       "destination": folder, "compile_app": False}
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            result = subprocess.run([builder.python_executable(), "-B", str(Path(builder.__file__)), "--worker"],
                                    input=json.dumps(request), capture_output=True, text=True,
                                    encoding="utf-8", env=env, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            events = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertTrue(any("log" in event for event in events))
            self.assertTrue(Path(events[-1]["result"]).is_dir())

    def test_missing_tools_fail_before_packing(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(builder, "check_tools", return_value=[
                ("ARM", False, "absent"), ("Node", True, "node")]), patch.object(builder, "run_command") as run:
            with self.assertRaisesRegex(RuntimeError, "Outils de compilation manquants"):
                builder.build("nes", [self.demo("nes")], folder, True, lambda line: None)
            run.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_tool_detection(self):
        with patch.object(builder.runpy, "run_path", return_value={"find_gcc": lambda: "gcc-arm"}), \
                patch.object(builder.shutil, "which", side_effect=lambda name: "/bin/" + name):
            self.assertTrue(all(found for _, found, _ in builder.check_tools("nes")))
        with patch.object(builder.runpy, "run_path", side_effect=SystemExit("ARM absent")), \
                patch.object(builder.shutil, "which", return_value=None):
            self.assertFalse(any(found for _, found, _ in builder.check_tools("gbc")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
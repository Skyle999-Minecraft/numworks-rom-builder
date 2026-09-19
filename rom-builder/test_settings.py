import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import settings


class SettingsTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config/settings.json"
            data = settings.defaults()
            data.update(platform="gbc", compile_app=False, destination=folder)
            data["paths"]["gbc"] = [str(Path(folder) / "Pokémon.gbc")]
            settings.save(path, data)
            self.assertEqual(settings.load(path), data)

    def test_invalid_settings_fall_back_safely(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            self.assertEqual(settings.load(path), settings.defaults())
            for content in ("invalid", "[]", '{"platform":[],"paths":42}',
                            '{"compile_app":"false","destination":null}'):
                path.write_text(content, encoding="utf-8")
                self.assertEqual(settings.load(path), settings.defaults())
            path.write_text(json.dumps({"paths": {"nes": [None, [], "relative.nes",
                                                           str(Path(folder) / "wrong.gb")]}}))
            self.assertEqual(settings.load(path)["paths"]["nes"], [])

    def test_failed_save_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            settings.save(path, settings.defaults())
            original = path.read_bytes()
            with patch("settings.os.replace", side_effect=PermissionError("blocked")):
                with self.assertRaises(PermissionError):
                    settings.save(path, {"platform": "gbc"})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(folder).iterdir()), [path])


if __name__ == "__main__":
    unittest.main(verbosity=2)
"""Smoke test Tk avec vrai worker et ROMs de demo, sans compilation ARM."""
from pathlib import Path
import tempfile
import time
import tkinter as tk
import unittest
from unittest.mock import patch

from app import RomBuilder
from builder import ROOT


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.preferences = tempfile.TemporaryDirectory()
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = RomBuilder(self.root, Path(self.preferences.name) / "settings.json")

    def tearDown(self):
        self.root.update_idletasks()
        self.app.after_cancel(self.app.after_id)
        self.root.destroy()
        self.preferences.cleanup()

    def test_platform_lists_and_remove(self):
        demo = ROOT / "nofrendo/src/2048.nes"
        with patch("app.filedialog.askopenfilenames", return_value=(str(demo), str(demo))):
            self.app.add_roms()
        self.assertEqual(self.app.paths["nes"], [demo])
        self.app.platform.set("gbc")
        self.app.refresh()
        self.assertEqual(self.app.tree.get_children(), ())
        self.app.platform.set("nes")
        self.app.refresh()
        self.app.tree.selection_set("0")
        self.app.remove_roms()
        self.assertEqual(self.app.paths["nes"], [])

    def test_async_pack_and_error(self):
        with tempfile.TemporaryDirectory() as folder, patch("app.messagebox.showerror") as errors:
            self.app.paths["nes"] = [ROOT / "nofrendo/src/2048.nes"]
            self.app.destination.set(folder)
            self.app.compile_app.set(False)
            self.app.start()
            self.assertTrue(self.app.busy)
            self.assertTrue(self.app.start_button.instate(["disabled"]))
            self.wait_for_job()
            self.assertTrue((self.app.result / "roms.nes").is_file())
            self.assertFalse(self.app.start_button.instate(["disabled"]))
            errors.assert_not_called()
            bad = Path(folder) / "bad.nes"
            bad.write_bytes(b"broken")
            self.app.paths["nes"] = [bad]
            self.app.start()
            self.wait_for_job()
            errors.assert_called_once()
            self.assertIsNone(self.app.result)
            self.assertFalse(self.app.start_button.instate(["disabled"]))

    def wait_for_job(self):
        deadline = time.monotonic() + 30
        while self.app.busy and time.monotonic() < deadline:
            self.root.update()
            time.sleep(0.01)
        self.assertFalse(self.app.busy, "Le worker ne termine pas")

    def test_preferences_restore_and_missing_files(self):
        import settings
        absent = Path(self.preferences.name) / "absent.nes"
        self.app.paths["nes"] = [absent]
        self.app.platform.set("gbc")
        self.app.compile_app.set(False)
        self.app.destination.set(self.preferences.name)
        self.app.save_preferences()
        saved = settings.load(self.app.settings_path)
        self.assertEqual(saved["platform"], "gbc")
        self.assertEqual(saved["paths"]["nes"], [str(absent)])
        self.app.platform.set("nes")
        self.app.refresh()
        self.assertIn("missing", self.app.tree.item("0", "tags"))
        self.assertIn("absent", self.app.count.get())
        # Un ancien fichier manquant n'empeche pas d'ajouter de nouveaux jeux.
        self.app.add_paths([ROOT / "nofrendo/src/2048.nes"])
        self.assertEqual(len(self.app.paths["nes"]), 2)
        self.app.after_cancel(self.app.after_id)
        self.app.destroy()
        self.app = RomBuilder(self.root, Path(self.preferences.name) / "settings.json")
        self.assertFalse(self.app.compile_app.get())
        self.assertEqual(len(self.app.paths["nes"]), 2)

    def test_folder_import_and_log_export(self):
        with patch("app.filedialog.askdirectory", return_value=str(ROOT / "peanutgb/src")):
            self.app.platform.set("gbc")
            self.app.add_folder()
        self.assertEqual(self.app.paths["gbc"], [ROOT / "peanutgb/src/flappyboy.gb"])
        self.app.append_log("\x1b[31mERREUR : test\x1b[0m")
        self.assertTrue(self.app.log.tag_ranges("error"))
        log = Path(self.preferences.name) / "essai.log"
        with patch("app.filedialog.asksaveasfilename", return_value=str(log)):
            self.app.save_log()
        self.assertEqual(log.read_text(encoding="utf-8"), "ERREUR : test\n")

    def test_tools_dialog(self):
        with patch("app.check_tools", return_value=[("ARM", False, "absent")]), \
                patch("app.messagebox.showinfo") as dialog:
            self.app.show_tools()
        self.assertIn("absent", dialog.call_args.args[1])

    def test_journal_visible_at_default_size(self):
        self.root.deiconify()
        self.app.tabs.select(self.app.journal_tab)
        self.root.update()
        self.assertGreater(self.app.log.winfo_height(), 80)
        self.assertGreater(self.app.log.winfo_width(), 300)
        self.assertLess(self.app.start_button.winfo_rooty() + self.app.start_button.winfo_height(),
                        self.root.winfo_rooty() + self.root.winfo_height())


if __name__ == "__main__":
    unittest.main(verbosity=2)
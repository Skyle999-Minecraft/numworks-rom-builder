"""Interface graphique NumWorks ROM Builder, Python 3.10+ et tkinter."""
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import webbrowser

from builder import PLATFORMS, ROOT, check_tools, python_executable, validate_selection
import settings


class RomBuilder(ttk.Frame):
    def __init__(self, master, settings_path=None):
        super().__init__(master, padding=18)
        self.pack(fill="both", expand=True)
        master.title("NumWorks — ROM Builder")
        master.geometry("1020x820")
        master.minsize(940, 760)
        master.protocol("WM_DELETE_WINDOW", self.close)
        self.settings_path = Path(settings_path) if settings_path is not None else settings.default_path()
        saved = settings.load(self.settings_path)
        self.platform = tk.StringVar(value=saved["platform"])
        self.destination = tk.StringVar(value=saved["destination"])
        self.compile_app = tk.BooleanVar(value=saved["compile_app"])
        self.status = tk.StringVar(value="Ajoutez vos ROMs pour commencer.")
        self.count = tk.StringVar(value="0 / 64 ROMs")
        self.paths = {key: [Path(p) for p in saved["paths"][key]] for key in PLATFORMS}
        self.events = queue.Queue()
        self.busy = False
        self.result = Path(saved["last_result"]) if saved["last_result"] else None
        self.started_at = None
        self.elapsed = tk.StringVar(value="")
        self.follow_log = tk.BooleanVar(value=True)
        self.controls = []
        self._layout()
        self.refresh()
        if self.result and self.result.is_dir():
            self.open_button.configure(state="normal")
        self.master.bind("<Control-o>", lambda event: self.add_roms())
        self.master.bind("<Control-Return>", lambda event: self.start())
        self.after_id = self.after(100, self.poll_events)

    def _layout(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        ttk.Label(self, text="NumWorks ROM Builder", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(self, text="Regroupez vos jeux et compilez leur émulateur pour la calculatrice.").pack(anchor="w", pady=(3, 14))
        platforms = ttk.LabelFrame(self, text="1. Choisir la console", padding=10)
        platforms.pack(fill="x")
        for key, config in PLATFORMS.items():
            button = ttk.Radiobutton(platforms, text=config.label, variable=self.platform,
                                     value=key, command=self.refresh)
            button.pack(side="left", padx=(0, 30))
            self.controls.append(button)
        self.tabs = ttk.Notebook(self, height=250)
        self.tabs.pack(fill="both", expand=True, pady=10)
        games = ttk.Frame(self.tabs, padding=10)
        self.journal_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(games, text="2. Jeux sélectionnés")
        self.tabs.add(self.journal_tab, text="Journal de compilation")
        toolbar = ttk.Frame(games)
        toolbar.pack(fill="x", pady=(0, 8))
        for label, command in (("Ajouter des ROMs…", self.add_roms),
                               ("Ajouter un dossier…", self.add_folder),
                               ("Retirer la sélection", self.remove_roms), ("Vider la liste", self.clear_roms)):
            button = ttk.Button(toolbar, text=label, command=command)
            button.pack(side="left", padx=(0, 6))
            self.controls.append(button)
        ttk.Label(games, textvariable=self.count).pack(anchor="w", pady=(0, 6))
        table = ttk.Frame(games)
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=("name", "size", "path"), show="headings", height=8)
        for name, label, width in (("name", "Jeu / fichier", 200), ("size", "Taille", 85), ("path", "Chemin", 430)):
            self.tree.heading(name, text=label)
            self.tree.column(name, width=width, minwidth=65, stretch=name != "size")
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Delete>", lambda event: self.remove_roms())
        self.tree.tag_configure("missing", foreground="#b3261e")
        self.tree.bind("<Control-a>", self.select_all)
        ttk.Label(games, text="NES : .nes  •  Game Boy Color : .gb et .gbc  •  64 jeux maximum, classés par nom.\n"
                  "Sélectionnez des ROMs individuelles, pas des archives ZIP ni des conteneurs déjà créés.").pack(anchor="w", pady=(8, 0))
        output = ttk.LabelFrame(self, text="3. Sortie", padding=10)
        output.pack(fill="x")
        row = ttk.Frame(output)
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=self.destination)
        entry.pack(side="left", fill="x", expand=True)
        browse = ttk.Button(row, text="Parcourir…", command=self.choose_destination)
        browse.pack(side="right", padx=(8, 0))
        check = ttk.Checkbutton(output, text="Compiler aussi l’application .nwa (outils ARM et Node.js requis)",
                                variable=self.compile_app)
        check.pack(anchor="w", pady=(8, 0))
        self.controls.extend((entry, browse, check))
        ttk.Label(output, text="Un nouveau sous-dossier est créé à chaque réussite : aucun ancien résultat n’est écrasé.").pack(anchor="w", pady=(4, 0))
        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=10)
        self.start_button = ttk.Button(actions, text="Préparer / compiler", command=self.start)
        self.start_button.pack(side="left")
        self.controls.append(self.start_button)
        self.open_button = ttk.Button(actions, text="Ouvrir le résultat", command=self.open_result, state="disabled")
        self.open_button.pack(side="left", padx=8)
        self.tools_button = ttk.Button(actions, text="Vérifier les outils", command=self.show_tools)
        self.tools_button.pack(side="left")
        self.controls.append(self.tools_button)
        ttk.Button(actions, text="Site d’installation", command=lambda: webbrowser.open("https://my.numworks.com/apps")).pack(side="right")
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x")
        ttk.Label(self, textvariable=self.status, wraplength=850).pack(anchor="w", pady=(6, 4))
        journal = ttk.Frame(self.journal_tab)
        journal.pack(fill="x", pady=(0, 4))
        ttk.Label(journal, text="Journal", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Checkbutton(journal, text="Défilement automatique", variable=self.follow_log).pack(side="left", padx=10)
        ttk.Button(journal, text="Enregistrer le journal…", command=self.save_log).pack(side="right")
        ttk.Label(journal, textvariable=self.elapsed).pack(side="right", padx=10)
        self.log = scrolledtext.ScrolledText(self.journal_tab, height=9, state="disabled", font=("Consolas", 9), wrap="word")
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("error", foreground="#b3261e")
        self.log.tag_configure("warning", foreground="#9a5700")
        self.log.tag_configure("stage", foreground="#175a9e")
        ttk.Label(self, text="Attention : installer sur la calculatrice remplace ses autres applications externes.\n"
                  "Cette interface ne lance aucune installation USB. Utilisez des ROMs que vous avez le droit d’utiliser.",
                  wraplength=850).pack(anchor="w", pady=(8, 0))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        paths = self.paths[self.platform.get()]
        total, missing = 0, 0
        for index, path in enumerate(paths):
            tags = ()
            try:
                if not path.is_file():
                    raise FileNotFoundError(str(path))
                length = path.stat().st_size
                total += length
                size = "%.1f Ko" % (length / 1024)
            except OSError:
                size = "Absent"
                missing += 1
                tags = ("missing",)
            self.tree.insert("", "end", iid=str(index), values=(path.name, size, str(path)), tags=tags)
        self.count.set("%d / 64 ROMs — %.1f Ko de jeux%s" %
                       (len(paths), total / 1024, " — %d fichier(s) absent(s)" % missing if missing else ""))

    def select_all(self, event=None):
        self.tree.selection_set(*self.tree.get_children())
        return "break"

    def save_preferences(self):
        try:
            settings.save(self.settings_path, {
                "platform": self.platform.get(), "destination": self.destination.get(),
                "compile_app": self.compile_app.get(),
                "paths": {key: [str(p) for p in paths] for key, paths in self.paths.items()},
                "last_result": str(self.result) if self.result else "",
            })
        except OSError as exc:
            self.append_log("ATTENTION : préférences non enregistrées : " + str(exc))

    def show_tools(self):
        if self.busy:
            return
        rows = check_tools(self.platform.get())
        details = "\n\n".join(("✓ " if found else "✗ ") + label + "\n" + detail
                               for label, found, detail in rows)
        details += "\n\nDétection locale uniquement. La disponibilité de nwlink et du réseau est vérifiée lors de la compilation."
        messagebox.showinfo("Outils de compilation", details, parent=self)

    def add_folder(self):
        if self.busy:
            return
        folder = filedialog.askdirectory(parent=self, title="Ajouter les ROMs d’un dossier (sans sous-dossiers)", mustexist=True)
        if not folder:
            return
        try:
            extensions = PLATFORMS[self.platform.get()].extensions
            paths = sorted((p for p in Path(folder).iterdir() if p.is_file() and p.suffix.lower() in extensions),
                           key=lambda p: p.name.casefold())
            if not paths:
                messagebox.showinfo("Aucune ROM", "Ce dossier ne contient pas de ROM compatible avec la console choisie.", parent=self)
                return
            self.add_paths(paths)
        except OSError as exc:
            messagebox.showerror("Dossier inaccessible", str(exc), parent=self)

    def add_roms(self):
        if self.busy:
            return
        config = PLATFORMS[self.platform.get()]
        filenames = filedialog.askopenfilenames(parent=self, title="Ajouter des ROMs — " + config.label,
                                                filetypes=[(config.label, tuple("*" + ext for ext in config.extensions))])
        self.add_paths(filenames)

    def add_paths(self, filenames):
        if self.busy or not filenames:
            return
        paths = self.paths[self.platform.get()]
        candidates = list(paths)
        try:
            incoming = validate_selection(self.platform.get(), list(dict.fromkeys(filenames)))
            for path in incoming:
                if path not in candidates:
                    candidates.append(path)
            if len(candidates) > 64:
                raise ValueError("La sélection dépasserait 64 ROMs. Aucun fichier ajouté.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Sélection invalide", str(exc), parent=self)
            return
        paths[:] = candidates
        self.refresh()
        self.save_preferences()

    def remove_roms(self):
        if self.busy:
            return
        paths = self.paths[self.platform.get()]
        for index in sorted((int(item) for item in self.tree.selection()), reverse=True):
            del paths[index]
        self.refresh()
        self.save_preferences()

    def clear_roms(self):
        if not self.busy:
            self.paths[self.platform.get()].clear()
            self.refresh()
            self.save_preferences()

    def choose_destination(self):
        folder = filedialog.askdirectory(parent=self, title="Dossier de sortie", mustexist=True)
        if folder:
            self.destination.set(folder)
            self.save_preferences()

    def append_log(self, text):
        # Retirer les sequences ANSI des outils Node/Windows.
        text = re.sub(r"\x1b\][^\x07]*(?:\x07|\x1b\\)|\x1b\[[0-?]*[ -/]*[@-~]", "", text)
        tag = "error" if "ERREUR" in text or "MANQUANT" in text or "IGNORE" in text else (
            "warning" if "warning:" in text or "ATTENTION" in text else "stage" if text.startswith("===") else "")
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", (tag,) if tag else ())
        if self.follow_log.get():
            self.log.see("end")
        self.log.configure(state="disabled")

    def save_log(self):
        filename = filedialog.asksaveasfilename(parent=self, title="Enregistrer le journal",
                                               initialfile="compilation.log", defaultextension=".log",
                                               filetypes=[("Journal", "*.log"), ("Texte", "*.txt")])
        if filename:
            try:
                Path(filename).write_text(self.log.get("1.0", "end-1c"), encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("Enregistrement impossible", str(exc), parent=self)

    def start(self):
        if self.busy:
            return
        try:
            paths = validate_selection(self.platform.get(), self.paths[self.platform.get()])
            destination = Path(self.destination.get()).expanduser().resolve()
            if not destination.is_dir():
                raise ValueError("Choisissez un dossier de sortie existant.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Impossible de démarrer", str(exc), parent=self)
            return
        request = {"platform": self.platform.get(), "paths": [str(p) for p in paths],
                   "destination": str(destination), "compile_app": self.compile_app.get()}
        self.busy = True
        self.started_at = time.monotonic()
        self.elapsed.set("00:00")
        self.save_preferences()
        self.result = None
        self.open_button.configure(state="disabled")
        for widget in self.controls:
            widget.configure(state="disabled")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.status.set("Préparation en cours… La première compilation peut télécharger nwlink.")
        self.progress.start(12)
        self.tabs.select(self.journal_tab)
        threading.Thread(target=self.worker, args=(request,), daemon=True).start()

    def worker(self, request):
        """Aucun appel Tk dans ce thread : toutes les nouvelles passent par la queue."""
        result, error = None, None
        env = os.environ.copy()
        env.update(PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
        options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        try:
            with subprocess.Popen([python_executable(), "-B", "-u", str(Path(__file__).with_name("builder.py")), "--worker"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, encoding="utf-8", errors="replace", env=env, **options) as process:
                process.stdin.write(json.dumps(request))
                process.stdin.close()
                for line in process.stdout:
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        self.events.put(("log", line.rstrip()))
                        continue
                    if "log" in event:
                        self.events.put(("log", event["log"]))
                    if "result" in event:
                        result = event["result"]
                    if "error" in event:
                        error = event["error"]
                code = process.wait()
                if code or not result:
                    raise RuntimeError(error or "Le processus de compilation a échoué (code %d)." % code)
            self.events.put(("success", result))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll_events(self):
        if self.busy and self.started_at is not None:
            seconds = int(time.monotonic() - self.started_at)
            self.elapsed.set("%02d:%02d" % divmod(seconds, 60))
        for _ in range(200):
            try:
                kind, text = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self.append_log(text)
                if text.startswith("==="):
                    self.status.set(text.strip("= "))
                continue
            self.busy = False
            self.progress.stop()
            for widget in self.controls:
                widget.configure(state="normal")
            if kind == "success":
                self.result = Path(text)
                self.open_button.configure(state="normal")
                self.status.set("Terminé — " + text)
                self.append_log("\nRésultat prêt : " + text)
                self.save_preferences()
            else:
                self.status.set("Échec — consultez le journal et corrigez les fichiers ou les outils.")
                self.append_log("\nERREUR : " + text)
                messagebox.showerror("Préparation interrompue", text, parent=self)
        self.after_id = self.after(100, self.poll_events)

    def open_result(self):
        if self.result and self.result.is_dir():
            try:
                if os.name == "nt":
                    os.startfile(str(self.result))
                else:
                    webbrowser.open(self.result.as_uri())
            except OSError as exc:
                messagebox.showerror("Ouverture impossible", str(exc), parent=self)

    def close(self):
        if self.busy:
            messagebox.showinfo("Compilation en cours", "Attendez la fin de la compilation avant de fermer.", parent=self)
            return
        self.after_cancel(self.after_id)
        self.save_preferences()
        self.master.destroy()


def main():
    root = tk.Tk()
    RomBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
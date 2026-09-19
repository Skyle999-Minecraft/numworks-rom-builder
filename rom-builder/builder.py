"""Preparation des ROMs et compilation, sans dependance graphique.

Le processus --worker lit une requete JSON sur stdin. Les sources des
emulateurs restent la reference pour le format et la validation des ROMs.
"""
import argparse
from dataclasses import dataclass
from datetime import datetime
import glob
import json
import os
import runpy
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Platform:
    label: str
    project: str
    extensions: tuple
    blob: str


PLATFORMS = {
    "nes": Platform("NES", "nofrendo", (".nes",), "roms.nes"),
    "gbc": Platform("Game Boy / Game Boy Color", "peanutgb", (".gb", ".gbc"), "roms.gb"),
}


def python_executable():
    """pythonw ne fournit pas de stdout exploitable pour les sous-processus."""
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        executable = executable.with_name("python.exe")
    return str(executable)


def validate_selection(platform, paths):
    if platform not in PLATFORMS:
        raise ValueError("Choisissez NES ou Game Boy Color.")
    if not 1 <= len(paths) <= 64:
        raise ValueError("Choisissez entre 1 et 64 ROMs.")
    selected = []
    for name in paths:
        path = Path(name).expanduser().resolve(strict=True)
        if not path.is_file() or path.suffix.lower() not in PLATFORMS[platform].extensions:
            raise ValueError("Extension incompatible ou fichier invalide : " + str(path))
        if path in selected:
            raise ValueError("ROM selectionnee plusieurs fois : " + str(path))
        selected.append(path)
    return selected


def run_command(command, cwd, emit):
    env = os.environ.copy()
    env.update(PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    with subprocess.Popen(command, cwd=str(cwd), env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                          text=True, encoding="utf-8", errors="replace", **options) as process:
        for line in process.stdout:
            emit(line.rstrip("\r\n"))
        code = process.wait()
    if code:
        raise RuntimeError("Etape en echec (code %d). Consultez le journal ci-dessus." % code)


def check_tools(platform):
    """Detection locale seulement : aucun telechargement ni installation."""
    config = PLATFORMS[platform]
    rows = []
    script = ROOT / config.project / "tools/build.py"
    try:
        tools = runpy.run_path(str(script))
        compiler = tools["find_gcc"]()
        rows.append(("Compilateur ARM", True, compiler))
    except (OSError, KeyError, SystemExit) as exc:
        rows.append(("Compilateur ARM", False, str(exc)))
    for executable, label in (("node", "Node.js"), ("npx", "npx")):
        found = shutil.which(executable)
        rows.append((label, bool(found), found or "Absent du PATH : installez Node.js avec npm, puis relancez l'application."))
    return rows


def require_tools(platform, emit):
    rows = check_tools(platform)
    for label, available, detail in rows:
        emit(("OK : " if available else "MANQUANT : ") + label + " — " + detail)
    if any(not available for _, available, _ in rows):
        raise RuntimeError("Outils de compilation manquants. Installez les outils indiqués ou "
                           "décochez « Compiler aussi l’application .nwa » pour préparer seulement les ROMs.")


def build(platform, paths, destination, compile_app=True, emit=print):
    """Publie un nouveau dossier seulement apres validation de toutes les etapes."""
    selected = validate_selection(platform, paths)
    config = PLATFORMS[platform]
    parent = Path(destination).expanduser().resolve()
    if not parent.is_dir():
        raise ValueError("Le dossier de sortie doit exister : " + str(parent))
    project = ROOT / config.project
    for name in ("pack_roms.py", "check_pack.py", "build.py"):
        if not (project / "tools" / name).is_file():
            raise FileNotFoundError("Script du projet manquant : " + str(project / "tools" / name))
    log = []

    def report(line):
        log.append(line)
        emit(line)

    if compile_app:
        report("=== Vérification des outils ===")
        require_tools(platform, report)

    # Les outils de lien emploient un shell : ils ne recoivent que des chemins
    # de travail temporaires, jamais le dossier de publication choisi dans l'UI.
    with tempfile.TemporaryDirectory(prefix="nw-rom-builder-") as folder:
        stage = Path(folder)
        blob = stage / config.blob
        report("=== 1/3 : preparation des %d ROM(s) — %s ===" % (len(selected), config.label))
        # Le packeur attend des motifs glob : echapper les crochets des noms.
        run_command([python_executable(), "-B", "-u", str(project / "tools/pack_roms.py"),
                     "-o", str(blob), *[glob.escape(str(p)) for p in selected]], project, report)
        with blob.open("rb") as stream:
            header = stream.read(12)
        if len(header) != 12 or header[:8] != b"NWROMS\0\1":
            raise RuntimeError("Le packeur n'a pas produit un conteneur valide.")
        if struct.unpack_from("<I", header, 8)[0] != len(selected):
            raise ValueError("Une ou plusieurs ROMs ont ete refusees. Aucun resultat publie. "
                             "Retirez ou remplacez les ROMs indiquees IGNORE dans le journal.")
        report("=== 2/3 : verification du conteneur ===")
        run_command([python_executable(), "-B", "-u", str(project / "tools/check_pack.py"),
                     str(blob)], project, report)
        outputs = [blob]
        if compile_app:
            report("=== 3/3 : compilation ARM et verification du lien final ===")
            compiled = stage / "build"
            run_command([python_executable(), "-B", "-u", str(project / "tools/build.py"),
                         "-d", str(blob), "--output", str(compiled)], project, report)
            nwa = compiled / (config.project + ".nwa")
            binary = compiled / (config.project + ".bin")
            for path in (nwa, binary):
                if not path.is_file() or not path.stat().st_size:
                    raise RuntimeError("Fichier compile manquant ou vide : " + str(path))
            outputs.append(nwa)
            report("Taille du lien final, ROMs incluses : %d octets." % binary.stat().st_size)
        else:
            report("=== 3/3 : compilation non demandee (conteneur uniquement) ===")
        # mkdtemp reserve un nom unique, meme pour deux compilations simultanees.
        result = Path(tempfile.mkdtemp(prefix=platform + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-",
                                       dir=str(parent)))
        try:
            for path in outputs:
                shutil.copy2(path, result / path.name)
            instructions = (
                "NumWorks — " + config.label + "\n\n"
                + ("Application : " + config.project + ".nwa\n" if compile_app else
                   "Conteneur uniquement : utiliser une application multi-ROMs compatible.\n")
                + "Donnees externes : " + config.blob + "\n\n"
                "Installation : https://my.numworks.com/apps\n"
                "Deposer tous les .nwa a conserver en une seule operation, puis associer\n"
                "le fichier de donnees externes a son emulateur. Installer efface les\n"
                "autres applications externes. Aucune installation USB n'a ete effectuee.\n"
                "Une seule ROM demarre directement ; plusieurs ROMs affichent un menu.\n"
                "Game Boy : pas de son ni de sauvegarde persistante ; vitesse Color a tester.\n"
            )
            (result / "LISEZMOI.txt").write_text(instructions, encoding="utf-8")
            (result / "compilation.log").write_text("\n".join(log) + "\n", encoding="utf-8")
        except Exception:
            shutil.rmtree(result)
            raise
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", required=True)
    parser.parse_args()
    try:
        request = json.load(sys.stdin)
        result = build(request["platform"], request["paths"], request["destination"],
                       request.get("compile_app", True),
                       emit=lambda text: print(json.dumps({"log": text}, ensure_ascii=True), flush=True))
        print(json.dumps({"result": str(result)}), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
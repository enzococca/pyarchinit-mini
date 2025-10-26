#!/usr/bin/env python3
"""
Script per aggiornare automaticamente URLs e versioni in tutto il progetto
==========================================================================

Questo script:
1. Corregge gli URL del repository da pyarchinit/pyarchinit-mini a enzococca/pyarchinit-mini
2. Verifica che le versioni siano consistenti in tutti i file
3. Crea un report di tutti i punti dove appare la versione

Uso:
    python scripts/update_urls_and_versions.py --fix-urls
    python scripts/update_urls_and_versions.py --check-versions
    python scripts/update_urls_and_versions.py --update-version 1.5.4
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Repository URLs
OLD_REPO_URL = "https://github.com/enzococca/pyarchinit-mini"
NEW_REPO_URL = "https://github.com/enzococca/pyarchinit-mini"

# Files da controllare per la versione
VERSION_FILES = {
    "pyproject.toml": r'version\s*=\s*"([^"]+)"',
    "pyarchinit_mini/__init__.py": r'__version__\s*=\s*["\']([^"\']+)["\']',
    "setup.py": r'version\s*=\s*["\']([^"\']+)["\']',
    "docs/index.rst": r'Version\s+(\d+\.\d+\.\d+)',
    "web_interface/templates/dashboard.html": r'v(\d+\.\d+\.\d+)',
    "pyarchinit_mini/web_interface/templates/dashboard.html": r'v(\d+\.\d+\.\d+)',
}

# File da escludere dalla ricerca URL
EXCLUDE_PATTERNS = [
    "*.egg-info/*",
    "build/*",
    "dist/*",
    ".venv/*",
    "__pycache__/*",
    "*.pyc",
    ".git/*",
]


class URLVersionUpdater:
    """Aggiorna URLs e versioni nel progetto"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.changes = []
        self.version_locations = []

    def should_exclude(self, path: Path) -> bool:
        """Verifica se il file deve essere escluso"""
        path_str = str(path.relative_to(self.root_dir))
        for pattern in EXCLUDE_PATTERNS:
            if Path(path_str).match(pattern):
                return True
        return False

    def find_old_urls(self) -> List[Tuple[Path, int, str]]:
        """Trova tutti i file con il vecchio URL"""
        results = []

        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file() or self.should_exclude(file_path):
                continue

            # Skip binary files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue

            # Find old URLs
            for line_num, line in enumerate(content.splitlines(), 1):
                if OLD_REPO_URL in line:
                    results.append((file_path, line_num, line.strip()))

        return results

    def fix_urls(self, dry_run: bool = False) -> int:
        """Sostituisce tutti i vecchi URL con quelli nuovi"""
        fixed_count = 0

        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file() or self.should_exclude(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue

            if OLD_REPO_URL not in content:
                continue

            new_content = content.replace(OLD_REPO_URL, NEW_REPO_URL)

            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

            count = content.count(OLD_REPO_URL)
            fixed_count += count
            self.changes.append(f"✓ {file_path.relative_to(self.root_dir)}: {count} URL(s) aggiornato/i")

        return fixed_count

    def find_versions(self) -> Dict[str, List[str]]:
        """Trova tutte le versioni nei file specificati"""
        versions = {}

        for file_pattern, regex_pattern in VERSION_FILES.items():
            file_paths = list(self.root_dir.glob(file_pattern))

            for file_path in file_paths:
                if not file_path.exists():
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    matches = re.findall(regex_pattern, content)
                    if matches:
                        rel_path = str(file_path.relative_to(self.root_dir))
                        if rel_path not in versions:
                            versions[rel_path] = []
                        versions[rel_path].extend(matches)
                except (UnicodeDecodeError, PermissionError):
                    continue

        return versions

    def check_version_consistency(self) -> bool:
        """Verifica che tutte le versioni siano consistenti"""
        versions = self.find_versions()

        if not versions:
            print("⚠️  Nessuna versione trovata!")
            return False

        # Get all unique versions
        all_versions = set()
        for version_list in versions.values():
            all_versions.update(version_list)

        print(f"\n📋 Versioni trovate nel progetto:")
        print(f"   Versioni uniche: {', '.join(sorted(all_versions))}")
        print(f"\n📍 Posizioni delle versioni:")

        for file_path, version_list in sorted(versions.items()):
            for version in version_list:
                print(f"   - {file_path}: {version}")

        if len(all_versions) > 1:
            print(f"\n⚠️  ATTENZIONE: Trovate {len(all_versions)} versioni diverse!")
            print(f"   Versioni: {', '.join(sorted(all_versions))}")
            return False
        else:
            print(f"\n✅ Tutte le versioni sono consistenti: {list(all_versions)[0]}")
            return True

    def update_version(self, new_version: str, dry_run: bool = False) -> int:
        """Aggiorna la versione in tutti i file"""
        updated_count = 0

        for file_pattern, regex_pattern in VERSION_FILES.items():
            file_paths = list(self.root_dir.glob(file_pattern))

            for file_path in file_paths:
                if not file_path.exists():
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Find and replace version
                    new_content, count = re.subn(
                        regex_pattern,
                        lambda m: m.group(0).replace(m.group(1), new_version),
                        content
                    )

                    if count > 0:
                        if not dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)

                        updated_count += count
                        rel_path = str(file_path.relative_to(self.root_dir))
                        print(f"   ✓ {rel_path}: {count} versione/i aggiornata/e")

                except (UnicodeDecodeError, PermissionError):
                    continue

        return updated_count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggiorna URLs e versioni nel progetto PyArchInit-Mini"
    )
    parser.add_argument(
        "--fix-urls",
        action="store_true",
        help="Corregge tutti gli URL del repository"
    )
    parser.add_argument(
        "--check-versions",
        action="store_true",
        help="Verifica la consistenza delle versioni"
    )
    parser.add_argument(
        "--update-version",
        metavar="VERSION",
        help="Aggiorna la versione in tutti i file (es: 1.5.4)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra cosa verrebbe fatto senza modificare i file"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Genera un report completo di URLs e versioni"
    )

    args = parser.parse_args()

    if not any([args.fix_urls, args.check_versions, args.update_version, args.report]):
        parser.print_help()
        sys.exit(1)

    updater = URLVersionUpdater()

    print("=" * 70)
    print("PyArchInit-Mini - URL and Version Updater")
    print("=" * 70)

    # Fix URLs
    if args.fix_urls or args.report:
        print(f"\n🔍 Cercando vecchi URL del repository...")
        old_urls = updater.find_old_urls()

        if old_urls:
            print(f"   Trovati {len(old_urls)} file con vecchi URL:")
            for file_path, line_num, line in old_urls[:10]:  # Show first 10
                print(f"   - {file_path.relative_to(updater.root_dir)}:{line_num}")

            if len(old_urls) > 10:
                print(f"   ... e altri {len(old_urls) - 10} file")

            if args.fix_urls:
                if args.dry_run:
                    print(f"\n🔧 [DRY RUN] Verrebbero aggiornati:")
                else:
                    print(f"\n🔧 Aggiornando URL...")

                count = updater.fix_urls(dry_run=args.dry_run)

                for change in updater.changes:
                    print(f"   {change}")

                if args.dry_run:
                    print(f"\n✓ [DRY RUN] {count} URL verrebbero aggiornati")
                else:
                    print(f"\n✅ {count} URL aggiornati con successo!")
        else:
            print("   ✅ Nessun vecchio URL trovato!")

    # Check versions
    if args.check_versions or args.report:
        print(f"\n🔍 Verificando consistenza versioni...")
        consistent = updater.check_version_consistency()

    # Update version
    if args.update_version:
        if args.dry_run:
            print(f"\n🔧 [DRY RUN] Aggiornamento versione a {args.update_version}...")
        else:
            print(f"\n🔧 Aggiornando versione a {args.update_version}...")

        count = updater.update_version(args.update_version, dry_run=args.dry_run)

        if args.dry_run:
            print(f"\n✓ [DRY RUN] {count} versioni verrebbero aggiornate")
        else:
            print(f"\n✅ {count} versioni aggiornate con successo!")

    print("\n" + "=" * 70)

    if args.dry_run:
        print("ℹ️  Eseguito in modalità dry-run. Nessun file è stato modificato.")
        print("   Rimuovi --dry-run per applicare le modifiche.")

    print("=" * 70)


if __name__ == "__main__":
    main()
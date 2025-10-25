#!/usr/bin/env python3
"""
Documentation Verification Script for PyArchInit-Mini

This script verifies that:
1. Version numbers are aligned across all files (pyproject.toml, docs/conf.py, CHANGELOG.md)
2. Documentation is in English (not Italian)
3. ReadTheDocs configuration is valid

Usage:
    python scripts/verify_docs.py [--fix]

Options:
    --fix    Automatically fix version misalignments
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Use tomllib (Python 3.11+) or tomli (Python 3.8-3.10)
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: Please install tomli: pip install tomli")
        sys.exit(1)

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


class DocsVerifier:
    def __init__(self, project_root: Path, fix: bool = False):
        self.project_root = project_root
        self.fix = fix
        self.errors = []
        self.warnings = []
        self.success_messages = []

    def check_version_alignment(self) -> bool:
        """Check that version numbers are aligned across all files."""
        print(f"{BLUE}📋 Checking version alignment...{RESET}")

        versions = {}

        # 1. Get version from pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                versions["pyproject.toml"] = pyproject_data["project"]["version"]
        else:
            self.errors.append("pyproject.toml not found")
            return False

        # 2. Get version from docs/conf.py
        conf_path = self.project_root / "docs" / "conf.py"
        if conf_path.exists():
            with open(conf_path, "r") as f:
                conf_content = f.read()
                match = re.search(r"release\s*=\s*['\"]([^'\"]+)['\"]", conf_content)
                if match:
                    versions["docs/conf.py"] = match.group(1)
                else:
                    self.errors.append("Could not find 'release' in docs/conf.py")
                    return False
        else:
            self.errors.append("docs/conf.py not found")
            return False

        # 3. Get version from CHANGELOG.md (first version entry)
        changelog_path = self.project_root / "CHANGELOG.md"
        if changelog_path.exists():
            with open(changelog_path, "r") as f:
                changelog_content = f.read()
                match = re.search(r"##\s*\[([0-9.]+)\]", changelog_content)
                if match:
                    versions["CHANGELOG.md"] = match.group(1)
                else:
                    self.warnings.append("Could not find version in CHANGELOG.md")
        else:
            self.warnings.append("CHANGELOG.md not found")

        # Check if all versions match
        unique_versions = set(versions.values())

        if len(unique_versions) == 1:
            version = list(unique_versions)[0]
            self.success_messages.append(f"✅ All versions aligned: {version}")
            for file, ver in versions.items():
                print(f"  {GREEN}✓{RESET} {file}: {ver}")
            return True
        else:
            self.errors.append("Version mismatch detected:")
            for file, version in versions.items():
                print(f"  {RED}✗{RESET} {file}: {version}")

            if self.fix:
                return self._fix_version_alignment(versions)
            else:
                self.errors.append("Run with --fix to automatically align versions")
            return False

    def _fix_version_alignment(self, versions: Dict[str, str]) -> bool:
        """Automatically fix version misalignments using pyproject.toml as source of truth."""
        print(f"{YELLOW}🔧 Attempting to fix version misalignment...{RESET}")

        master_version = versions["pyproject.toml"]
        print(f"  Using {master_version} from pyproject.toml as master version")

        # Fix docs/conf.py
        if versions.get("docs/conf.py") != master_version:
            conf_path = self.project_root / "docs" / "conf.py"
            with open(conf_path, "r") as f:
                content = f.read()

            new_content = re.sub(
                r"(release\s*=\s*['\"])[^'\"]+(['\"])",
                f"\\1{master_version}\\2",
                content
            )

            with open(conf_path, "w") as f:
                f.write(new_content)

            print(f"  {GREEN}✓{RESET} Updated docs/conf.py to {master_version}")

        self.success_messages.append(f"✅ Versions aligned to {master_version}")
        return True

    def check_documentation_language(self) -> bool:
        """Check that documentation is in English, not Italian."""
        print(f"{BLUE}🌍 Checking documentation language...{RESET}")

        # Common Italian words that shouldn't appear in English docs
        italian_words = [
            r'\bciao\b',
            r'\bgrazie\b',
            r'\bprego\b',
            r'\bbenvenuto\b',
            r'\bprova\b',
            r'\bdocumentazione\b',
            r'\binstallazione\b',
            r'\butilizzo\b',
            r'\besempio\b',
            r'\bconfigurazione\b',
            r'\bimpostazioni\b',
            r'\boperazioni\b',
            r'\bfunzionalità\b',
            r'\bcaratteristiche\b',
        ]

        italian_pattern = re.compile('|'.join(italian_words), re.IGNORECASE)

        docs_dir = self.project_root / "docs"
        issues = []

        # Check .rst and .md files
        for ext in ['*.rst', '*.md']:
            for doc_file in docs_dir.rglob(ext):
                # Skip certain files
                if any(skip in str(doc_file) for skip in ['_build', 'SESSIONE', 'SESSION', 'DIAGNOSI', 'FIX_', 'RAPPORTI']):
                    continue

                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = italian_pattern.findall(content)
                        if matches:
                            issues.append({
                                'file': doc_file.relative_to(self.project_root),
                                'words': set(matches)
                            })
                except UnicodeDecodeError:
                    self.warnings.append(f"Could not read {doc_file} (encoding issue)")

        if issues:
            self.warnings.append(f"Found {len(issues)} files with potential Italian content:")
            for issue in issues:
                print(f"  {YELLOW}⚠{RESET} {issue['file']}: {', '.join(issue['words'])}")
            return False
        else:
            self.success_messages.append("✅ No Italian words detected in documentation")
            print(f"  {GREEN}✓{RESET} All documentation appears to be in English")
            return True

    def check_readthedocs_config(self) -> bool:
        """Verify ReadTheDocs configuration is valid."""
        print(f"{BLUE}📚 Checking ReadTheDocs configuration...{RESET}")

        rtd_config = self.project_root / ".readthedocs.yaml"

        if not rtd_config.exists():
            self.errors.append(".readthedocs.yaml not found")
            return False

        # Check required files exist
        required_files = [
            self.project_root / "docs" / "conf.py",
            self.project_root / "docs" / "index.rst",
            self.project_root / "docs" / "requirements.txt",
        ]

        missing = []
        for req_file in required_files:
            if not req_file.exists():
                missing.append(str(req_file.relative_to(self.project_root)))

        if missing:
            self.errors.append(f"Missing required ReadTheDocs files: {', '.join(missing)}")
            return False

        self.success_messages.append("✅ ReadTheDocs configuration is valid")
        print(f"  {GREEN}✓{RESET} .readthedocs.yaml exists")
        print(f"  {GREEN}✓{RESET} docs/conf.py exists")
        print(f"  {GREEN}✓{RESET} docs/index.rst exists")
        print(f"  {GREEN}✓{RESET} docs/requirements.txt exists")
        return True

    def check_changelog_updated(self) -> bool:
        """Check that CHANGELOG.md has an entry for the current version."""
        print(f"{BLUE}📝 Checking CHANGELOG.md...{RESET}")

        # Get current version from pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            current_version = pyproject_data["project"]["version"]

        # Check if CHANGELOG has entry for this version
        changelog_path = self.project_root / "CHANGELOG.md"
        with open(changelog_path, "r") as f:
            changelog_content = f.read()

        version_pattern = re.escape(f"## [{current_version}]")
        if re.search(version_pattern, changelog_content):
            self.success_messages.append(f"✅ CHANGELOG.md has entry for version {current_version}")
            print(f"  {GREEN}✓{RESET} Found entry for version {current_version}")
            return True
        else:
            self.errors.append(f"CHANGELOG.md missing entry for version {current_version}")
            print(f"  {RED}✗{RESET} No entry found for version {current_version}")
            return False

    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}PyArchInit-Mini Documentation Verification{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

        checks = [
            self.check_version_alignment(),
            self.check_documentation_language(),
            self.check_readthedocs_config(),
            self.check_changelog_updated(),
        ]

        all_passed = all(checks)

        # Print summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Summary{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

        if self.success_messages:
            for msg in self.success_messages:
                print(f"{GREEN}{msg}{RESET}")

        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"{YELLOW}⚠ {warning}{RESET}")

        if self.errors:
            print(f"\n{RED}Errors:{RESET}")
            for error in self.errors:
                print(f"{RED}✗ {error}{RESET}")

        print(f"\n{BLUE}{'='*60}{RESET}")

        if all_passed and not self.errors:
            print(f"{GREEN}✅ All checks passed! Documentation is ready.{RESET}\n")
            return True
        else:
            print(f"{RED}❌ Some checks failed. Please fix the issues above.{RESET}\n")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Verify PyArchInit-Mini documentation")
    parser.add_argument("--fix", action="store_true", help="Automatically fix version misalignments")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    verifier = DocsVerifier(project_root, fix=args.fix)

    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# PyArchInit-Mini Scripts

## Automated Maintenance Scripts

### `update_urls_and_versions.py`

Automated system for maintaining consistency across the project.

**Quick Reference:**

```bash
# Check version consistency before release
python scripts/update_urls_and_versions.py --check-versions

# Update version for new release
python scripts/update_urls_and_versions.py --update-version 1.6.0

# Fix repository URLs
python scripts/update_urls_and_versions.py --fix-urls

# Dry run (see changes without applying)
python scripts/update_urls_and_versions.py --update-version 1.6.0 --dry-run

# Complete report
python scripts/update_urls_and_versions.py --report
```

**Pre-Release Checklist:**

1. Check versions: `python scripts/update_urls_and_versions.py --check-versions`
2. Update if needed: `python scripts/update_urls_and_versions.py --update-version X.Y.Z`
3. Check URLs: `python scripts/update_urls_and_versions.py --fix-urls --dry-run`
4. Commit changes
5. Build: `python -m build`
6. Publish: `twine upload dist/pyarchinit_mini-X.Y.Z*`

**Tracked Locations:**

- `pyproject.toml` - Package version
- `pyarchinit_mini/__init__.py` - Python API version
- `setup.py` - Setup version
- `docs/index.rst` - Documentation version
- Web GUI dashboards (both locations) - UI version display

**See Also:**

- [Complete Guide](../docs/AUTOMATED_UPDATES_GUIDE.md)
- [Release Process](../docs/RELEASE_PROCESS.md)

---

**Purpose**: Prevents version number and URL inconsistencies across interfaces (API, CLI, Web GUI, Desktop GUI)

**Created**: 2025-10-26
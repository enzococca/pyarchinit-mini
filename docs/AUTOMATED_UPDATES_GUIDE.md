# Automated URL and Version Update Guide

## Overview

PyArchInit-Mini includes an automated system for maintaining consistency across the project:
- Repository URLs
- Version numbers across all interfaces (API, CLI, Web GUI, Desktop GUI)
- Documentation references

This prevents the common problem of version numbers and URLs becoming inconsistent across different parts of the codebase.

## The Update Script

Location: `scripts/update_urls_and_versions.py`

This script automatically:
1. Finds and fixes incorrect repository URLs
2. Checks version consistency across all interfaces
3. Updates version numbers everywhere with a single command

## Usage

### Check Version Consistency

Before any release, check that all version numbers are consistent:

```bash
python scripts/update_urls_and_versions.py --check-versions
```

This will show you all version numbers found in the project and warn if they're inconsistent.

### Update Version for New Release

When preparing a new release, update the version everywhere with one command:

```bash
python scripts/update_urls_and_versions.py --update-version 1.6.0
```

This automatically updates:
- `pyproject.toml` - Package version
- `pyarchinit_mini/__init__.py` - Python module version
- `setup.py` - Setup script version
- `docs/index.rst` - Documentation version
- `web_interface/templates/dashboard.html` - Web GUI version display
- `pyarchinit_mini/web_interface/templates/dashboard.html` - Web GUI version display

### Fix Repository URLs

If repository URLs need to be corrected:

```bash
python scripts/update_urls_and_versions.py --fix-urls
```

### Dry Run Mode

To see what would be changed without actually modifying files:

```bash
python scripts/update_urls_and_versions.py --update-version 1.6.0 --dry-run
python scripts/update_urls_and_versions.py --fix-urls --dry-run
```

### Complete Report

Generate a full report of URLs and versions:

```bash
python scripts/update_urls_and_versions.py --report
```

## Pre-Release Checklist

**IMPORTANT**: Run these commands before every release:

### 1. Check Version Consistency

```bash
python scripts/update_urls_and_versions.py --check-versions
```

If inconsistent, update to the correct version:

```bash
python scripts/update_urls_and_versions.py --update-version X.Y.Z
```

### 2. Verify URLs

```bash
python scripts/update_urls_and_versions.py --fix-urls --dry-run
```

If any old URLs are found, fix them:

```bash
python scripts/update_urls_and_versions.py --fix-urls
```

### 3. Commit Changes

```bash
git add -A
git commit -m "chore: update version to X.Y.Z and fix URLs"
git push
```

### 4. Build and Publish

```bash
# Build distribution
python -m build

# Upload to PyPI
twine upload dist/pyarchinit_mini-X.Y.Z*
```

## Where Versions Are Tracked

The script monitors these locations:

| File | Pattern | Interface |
|------|---------|-----------|
| `pyproject.toml` | `version = "X.Y.Z"` | Package metadata |
| `pyarchinit_mini/__init__.py` | `__version__ = "X.Y.Z"` | Python API |
| `setup.py` | `version="X.Y.Z"` | Setup script |
| `docs/index.rst` | `Version X.Y.Z` | Documentation |
| `web_interface/templates/dashboard.html` | `vX.Y.Z` | Web GUI |
| `pyarchinit_mini/web_interface/templates/dashboard.html` | `vX.Y.Z` | Web GUI (package) |

## Integration with CI/CD

You can integrate this into your release workflow:

```bash
# In your release script or CI/CD pipeline
VERSION=$1  # e.g., 1.6.0

# Update all versions
python scripts/update_urls_and_versions.py --update-version $VERSION

# Verify consistency
python scripts/update_urls_and_versions.py --check-versions

# If successful, proceed with build and release
if [ $? -eq 0 ]; then
    python -m build
    twine upload dist/pyarchinit_mini-${VERSION}*
fi
```

## Troubleshooting

### Version Update Didn't Update All Files

**Problem**: Some files still show old version

**Solution**: Check that the regex patterns in `VERSION_FILES` match your file format. The script looks for specific patterns.

### Script Reports False Positives

**Problem**: Script finds "versions" that aren't actually version numbers (like Python version `3.8`)

**Solution**: This is expected behavior. The Python version requirement in `pyproject.toml` is currently detected by the script but won't affect functionality. We filter by checking if the version matches semantic versioning pattern (X.Y.Z).

### Need to Track Additional Files

**Problem**: You've added version numbers in new files

**Solution**: Edit `scripts/update_urls_and_versions.py` and add the file path and regex pattern to the `VERSION_FILES` dictionary:

```python
VERSION_FILES = {
    # ... existing entries ...
    "your/new/file.py": r'VERSION\s*=\s*"([^"]+)"',
}
```

## Example Workflow: Preparing Version 1.6.0

```bash
# 1. Check current state
python scripts/update_urls_and_versions.py --check-versions

# Output shows:
# ⚠️  ATTENZIONE: Trovate 3 versioni diverse!
#    Versioni: 1.5.0, 1.5.2, 1.5.3

# 2. Update to new version
python scripts/update_urls_and_versions.py --update-version 1.6.0

# Output:
# ✅ 7 versioni aggiornate con successo!

# 3. Verify consistency
python scripts/update_urls_and_versions.py --check-versions

# Output:
# ✅ Tutte le versioni sono consistenti: 1.6.0

# 4. Check URLs
python scripts/update_urls_and_versions.py --fix-urls --dry-run

# 5. Commit
git add -A
git commit -m "chore: bump version to 1.6.0"
git push

# 6. Build and publish
python -m build
twine upload dist/pyarchinit_mini-1.6.0*
```

## Benefits

### Before This System

- Version numbers scattered across 6+ files
- Easy to forget updating web GUI version display
- Manual search-and-replace required
- Repository URLs could become inconsistent
- Documentation could reference wrong version

### With This System

- ✅ Single command updates all versions
- ✅ Automatic consistency checking
- ✅ Prevents accidental version mismatches
- ✅ Pre-release verification
- ✅ Dry-run mode for safety
- ✅ Complete audit trail of version locations

## Maintenance

The script requires minimal maintenance. Only update it when:

1. **Adding new version locations**: Edit `VERSION_FILES` dictionary
2. **Changing repository URL**: Edit `OLD_REPO_URL` and `NEW_REPO_URL` constants
3. **Adding new file types**: Add to `EXCLUDE_PATTERNS` if needed

## See Also

- [Release Process](RELEASE_PROCESS.md) - Complete release workflow
- [PyPI Publication](docs/PYPI_PUBLICATION.md) - Publishing to PyPI
- [Documentation Updates](docs/DOCUMENTATION_VERIFICATION.md) - Documentation workflow

---

**Created**: 2025-10-26
**Last Updated**: 2025-10-26
**Script Version**: 1.0.0
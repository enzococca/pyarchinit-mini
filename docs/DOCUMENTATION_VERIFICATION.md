# Documentation Verification System

**Status**: Active since v1.3.2
**Purpose**: Ensure documentation quality and version consistency

## Overview

PyArchInit-Mini includes an automated documentation verification system that ensures:

1. **Version Alignment**: All version numbers match across files
2. **Language Consistency**: Documentation is in English
3. **ReadTheDocs Readiness**: Configuration is valid and buildable
4. **Changelog Updates**: Each version has proper changelog entry

## Components

### 1. Verification Script (`scripts/verify_docs.py`)

A Python script that performs comprehensive documentation checks.

**Usage:**

```bash
# Run verification
python scripts/verify_docs.py

# Auto-fix version misalignments
python scripts/verify_docs.py --fix
```

**Checks Performed:**

- ✅ Version alignment (pyproject.toml, docs/conf.py, CHANGELOG.md)
- ✅ Documentation language (English vs Italian)
- ✅ ReadTheDocs configuration validity
- ✅ Changelog entry for current version

**Example Output:**

```
============================================================
PyArchInit-Mini Documentation Verification
============================================================

📋 Checking version alignment...
  ✓ pyproject.toml: 1.3.2
  ✓ docs/conf.py: 1.3.2
  ✓ CHANGELOG.md: 1.3.2

🌍 Checking documentation language...
  ✓ All documentation appears to be in English

📚 Checking ReadTheDocs configuration...
  ✓ .readthedocs.yaml exists
  ✓ docs/conf.py exists
  ✓ docs/index.rst exists
  ✓ docs/requirements.txt exists

📝 Checking CHANGELOG.md...
  ✓ Found entry for version 1.3.2

============================================================
Summary
============================================================

✅ All versions aligned: 1.3.2
✅ No Italian words detected in documentation
✅ ReadTheDocs configuration is valid
✅ CHANGELOG.md has entry for version 1.3.2

============================================================
✅ All checks passed! Documentation is ready.
```

### 2. Pre-commit Hook

Automatically runs verification before each git commit.

**Setup:**

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Or use our setup script
bash scripts/setup_pre_commit.sh
```

**Bypass (when needed):**

```bash
git commit --no-verify
```

**Manual run:**

```bash
pre-commit run --all-files
```

### 3. GitHub Actions Workflow

Runs verification on every push and pull request.

**File**: `.github/workflows/verify-docs.yml`

**Jobs:**

1. **verify-documentation**: Runs verification script on multiple Python versions
2. **readthedocs-build-test**: Tests Sphinx documentation build
3. **version-alignment-check**: Shell-based version alignment verification

**View Results**: Check the "Actions" tab on GitHub

## Version Update Workflow

When updating the version, follow this workflow:

### Step 1: Update Version Number

Update version in `pyproject.toml`:

```toml
[project]
version = "1.3.3"  # New version
```

### Step 2: Run Auto-fix

```bash
python scripts/verify_docs.py --fix
```

This automatically updates:
- `docs/conf.py` to match pyproject.toml version

### Step 3: Update CHANGELOG.md

Add new version entry at the top:

```markdown
## [1.3.3] - 2025-10-26

### Added
- New feature description

### Fixed
- Bug fix description
```

### Step 4: Verify Everything

```bash
python scripts/verify_docs.py
```

Should show:
```
✅ All checks passed! Documentation is ready.
```

### Step 5: Commit and Push

```bash
git add pyproject.toml docs/conf.py CHANGELOG.md
git commit -m "chore: Bump version to 1.3.3"
git push
```

The pre-commit hook will run automatically.

### Step 6: Publish to PyPI

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

### Step 7: Verify ReadTheDocs

- Visit https://readthedocs.org/projects/pyarchinit-mini/
- Check that the build triggered automatically
- Verify the new version appears in documentation

## Troubleshooting

### Version Mismatch

**Problem**: Different versions in different files

**Solution**:
```bash
python scripts/verify_docs.py --fix
```

### Italian Words Detected

**Problem**: Documentation contains Italian words

**Solution**:
1. Check the reported files
2. Translate Italian content to English
3. Re-run verification

**Note**: Some files are session summaries and can be ignored.

### ReadTheDocs Build Failed

**Problem**: Documentation doesn't build on ReadTheDocs

**Solution**:
```bash
# Test build locally
cd docs
pip install -r requirements.txt
sphinx-build -W -b html . _build/html
```

Fix any errors reported.

### Pre-commit Hook Blocked Commit

**Problem**: Pre-commit hook prevents commit

**Solutions**:

1. **Fix the issues** (recommended):
   ```bash
   python scripts/verify_docs.py --fix
   ```

2. **Skip the hook** (use sparingly):
   ```bash
   git commit --no-verify
   ```

## Files Checked

### Version Files
- `pyproject.toml` - Master version source
- `docs/conf.py` - Sphinx documentation version
- `CHANGELOG.md` - Version history

### Documentation Files
- `docs/**/*.rst` - reStructuredText files
- `docs/**/*.md` - Markdown files
- Excludes: `_build/`, session summaries

### Configuration Files
- `.readthedocs.yaml` - ReadTheDocs configuration
- `docs/requirements.txt` - Documentation dependencies

## Integration with CI/CD

### GitHub Actions

The workflow runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via GitHub Actions UI

**Badge** (add to README):

```markdown
[![Documentation Status](https://github.com/enzococca/pyarchinit-mini/actions/workflows/verify-docs.yml/badge.svg)](https://github.com/enzococca/pyarchinit-mini/actions/workflows/verify-docs.yml)
```

### Pre-commit CI

For additional coverage, consider enabling [pre-commit.ci](https://pre-commit.ci):

```yaml
# .pre-commit-config.yaml
ci:
  autofix_commit_msg: |
    [pre-commit.ci] auto fixes from pre-commit hooks
  autofix_prs: true
  autoupdate_commit_msg: '[pre-commit.ci] pre-commit autoupdate'
  autoupdate_schedule: weekly
```

## Best Practices

1. **Always run verification before publishing**:
   ```bash
   python scripts/verify_docs.py
   ```

2. **Use auto-fix for version updates**:
   ```bash
   python scripts/verify_docs.py --fix
   ```

3. **Keep CHANGELOG.md updated** with each version

4. **Write documentation in English** to maintain consistency

5. **Test locally before pushing**:
   ```bash
   pre-commit run --all-files
   ```

6. **Check GitHub Actions** after pushing to verify builds

7. **Monitor ReadTheDocs** for successful builds

## Maintenance

### Update Pre-commit Hooks

```bash
pre-commit autoupdate
```

### Add New Checks

Edit `scripts/verify_docs.py` to add new verification logic.

### Modify GitHub Actions

Edit `.github/workflows/verify-docs.yml` to adjust CI behavior.

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

## Support

If you encounter issues with the verification system:

1. Check this documentation first
2. Run `python scripts/verify_docs.py` for detailed error messages
3. Open an issue on GitHub: https://github.com/enzococca/pyarchinit-mini/issues

---

**Last Updated**: 2025-10-25
**Version**: 1.3.2

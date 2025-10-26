# File Browser 400 Error - Fixed

## Issue Summary

The PyArchInit Import/Export file browser was returning HTTP 400 errors when attempting to open the file selection dialog.

## Root Cause

**Critical routing bug found and fixed:**

The blueprint was registered with URL prefix `/pyarchinit-import-export`, but the index route was incorrectly defined as:

```python
@pyarchinit_import_export_bp.route('/pyarchinit-import-export')  # WRONG!
```

This caused the route to become `/pyarchinit-import-export/pyarchinit-import-export` (double path).

## Fix Applied

Changed the index route to:

```python
@pyarchinit_import_export_bp.route('/')  # CORRECT!
```

Now the route correctly resolves to `/pyarchinit-import-export/`.

## Files Modified

1. **web_interface/pyarchinit_import_export_routes.py** (line 16)
   - Fixed route definition for index page

2. **Previous fixes already in place:**
   - JSON validation in browse_files endpoint
   - Empty path handling (defaults to home directory)
   - Path normalization and security checks
   - Comprehensive logging

## Testing Steps

### 1. Restart the Flask Web Server

**IMPORTANT:** You must restart the server for changes to take effect.

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python web_interface/app.py
```

### 2. Test the File Browser in Web Browser

1. Open http://localhost:5000
2. Navigate to **Tools → Import/Export PyArchInit**
3. In the Import tab, click the **Browse** button next to "Database File Path"
4. The file browser modal should open showing your home directory

### 3. Check Browser Console (F12)

If the modal doesn't open, check the browser console for JavaScript errors:

1. Press F12 to open Developer Tools
2. Go to Console tab
3. Look for messages starting with "Opening file browser" and "Loading directory"
4. Check for any error messages in red

### 4. Check Server Logs

Watch the server terminal for log messages:

```
INFO:web_interface.pyarchinit_import_export_routes:File browser requested path:  -> normalized: /Users/yourname
```

### 5. Run Automated Test (Optional)

```bash
# Make sure server is running first, then:
python test_file_browser_api.py
```

This will test all API endpoints and verify correct behavior.

## Expected Behavior

When working correctly:

1. Click **Browse** button → Modal opens showing home directory
2. Click on a directory → Navigate into that directory
3. Click on a .sqlite/.db file → File path appears in "Selected File" field
4. Click **Select** button → Modal closes and path fills the input field
5. Breadcrumb navigation shows current path
6. Only directories and SQLite files are shown

## What Was Fixed

### Issue 1: SQLite Path Validation Error ✓ FIXED
**Error:** "The string did not match the expected pattern"

**Fix:** Added path normalization:
```python
db_path = os.path.abspath(os.path.expanduser(db_path))
```

Applied to all three endpoints:
- `/api/pyarchinit/test-connection`
- `/api/pyarchinit/import`
- `/api/pyarchinit/export`

### Issue 2: File Browser 400 Error ✓ FIXED
**Error:** HTTP 400 when opening file browser modal

**Fix:**
1. Corrected route definition (route path bug)
2. Added JSON validation
3. Improved empty path handling
4. Added comprehensive error logging

### Issue 3: Manual Path Entry ✓ FIXED
**Issue:** Users had to manually type file paths

**Fix:** Implemented full file browser with:
- Bootstrap modal interface
- Server-side filesystem navigation API
- Breadcrumb navigation
- File type filtering (SQLite only)
- Security restrictions (forbidden directories)
- File size display

## Security Features

The file browser includes security protections:

1. **Forbidden directories blocked:**
   - `/etc`, `/var`, `/sys`, `/proc`, `/root`

2. **File type filtering:**
   - Only shows directories and SQLite database files (.db, .sqlite, .sqlite3, .db3)

3. **Path normalization:**
   - Prevents directory traversal attacks
   - Expands `~` and relative paths safely

4. **Permission handling:**
   - Skips files/directories without read access
   - Returns proper 403 errors for permission denied

## Troubleshooting

### Modal doesn't open
- Check browser console (F12) for JavaScript errors
- Verify server is running and restarted after fix
- Check server logs for route registration

### Still getting 400 error
- Verify the route fix is applied (check line 16 of pyarchinit_import_export_routes.py)
- Ensure server was fully restarted (not just reload)
- Run test_file_browser_api.py to test endpoint directly

### Empty directory list
- This is normal for directories with no SQLite files or subdirectories
- Navigate to a different directory using breadcrumb

### Permission denied errors
- Normal for system directories and protected folders
- Navigate to user-accessible directories (home, Documents, etc.)

## Next Steps

After verifying the file browser works:

1. Test the complete import workflow:
   - Browse and select a PyArchInit SQLite database
   - Test connection
   - Import data

2. Test the export workflow:
   - Browse and select target database path
   - Export data

3. Report any remaining issues with:
   - Browser console logs
   - Server terminal logs
   - Specific steps to reproduce

## Documentation Updated

The following documentation has been created:

1. **docs/features/pyarchinit_import_export.rst** - Complete import/export feature documentation
2. **docs/features/stratigraphic_relationships.rst** - Corrected relationship labeling for v1.2.16
3. **docs/features/harris_matrix.rst** - Harris Matrix visualization documentation

These will be available on ReadTheDocs after the next documentation build.

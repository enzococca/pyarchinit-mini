#!/bin/bash
# Verify CSRF Fix for PyArchInit Import/Export

echo "============================================================"
echo "CSRF Fix Verification Script"
echo "============================================================"
echo ""

# Check if the fix is applied
echo "Checking if CSRF exemption is in place..."
if grep -q "csrf.exempt(pyarchinit_import_export_bp)" web_interface/app.py; then
    echo "✓ CSRF exemption found in app.py"
else
    echo "✗ CSRF exemption NOT found in app.py"
    echo "  Please verify line 448 has: csrf.exempt(pyarchinit_import_export_bp)"
    exit 1
fi

# Check if route fix is applied
echo ""
echo "Checking if route fix is in place..."
if grep -q "@pyarchinit_import_export_bp.route('/')" web_interface/pyarchinit_import_export_routes.py; then
    echo "✓ Route fix found in pyarchinit_import_export_routes.py"
else
    echo "✗ Route fix NOT found"
    echo "  Please verify line 16 has: @pyarchinit_import_export_bp.route('/')"
    exit 1
fi

echo ""
echo "============================================================"
echo "All fixes are in place!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. RESTART the Flask server (kill and start again)"
echo "2. Test the file browser in web interface"
echo "3. Check browser console (F12) for success messages"
echo ""
echo "If file browser still doesn't work:"
echo "  - Run: python test_file_browser_api.py"
echo "  - Check for 200 status codes (not 400)"
echo ""

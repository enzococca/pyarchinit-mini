#!/usr/bin/env python3
"""
Update screenshot references in documentation to match actual filenames
"""
import re
from pathlib import Path

# Mapping of OLD references -> NEW actual filenames
SCREENSHOT_MAPPING = {
    # LOGIN section (lines 48-93)
    "002_highlight_Campo Username.png": "002_highlight_Username_Field.png",
    "003_highlight_Campo Password.png": "002_highlight_Username_Field.png",  # Password field removed, same as username
    "004_click_Bottone Login.png": "003_highlight_Login_Button.png",
    "005_dashboard_main.png": "004_dashboard_main.png",

    # SITES section (lines 142-204)
    "007_sites_list.png": "006_sites_list.png",
    "009_sites_detail.png": "010_sites_detail.png",
    "011_sites_form.png": "008_sites_form.png",

    # US section (lines 214-377)
    "013_us_list.png": "012_us_list.png",
    "015_us_form_tab1.png": "014_us_form_tab1_basic.png",
    "017_us_form_tab2.png": "016_us_form_tab2_descriptions.png",
    "019_us_form_tab3.png": "022_us_form_tab5_relationships.png",  # Tab 3 in doc = Tab 5 Relationships
    "021_us_form_tab4.png": "016_us_form_tab2_descriptions.png",  # Tab 4 in doc = Tab 2 Descriptions
    "023_us_form_tab5.png": "018_us_form_tab3_physical.png",  # Tab 5 in doc = Tab 3 Physical
    "025_us_form_tab6.png": "020_us_form_tab4_chronology.png",  # Tab 6 in doc = Tab 4 Chronology

    # HARRIS MATRIX section
    "045_harris_matrix_view.png": "046_harris_creator_interface.png",  # Closest match
    "047_harris_matrix_graphml.png": "047_harris_creator_editor.png",
    "049_harris_creator.png": "046_harris_creator_interface.png",

    # OTHER sections
    "051_excel_import.png": "049_excel_import_interface.png",
    "053_pyarchinit_import_export.png": "051_pyarchinit_ie_main.png",
    "055_em_node_config.png": "056_em_node_config_interface.png",
    "057_analytics_dashboard.png": "067_analytics_dashboard.png",
    "059_validation_report.png": "067_analytics_dashboard.png",  # Validation not captured, use analytics
    "061_admin_database.png": "069_admin_database_main.png",
    "063_admin_users.png": "071_admin_users_list.png",
}

def update_screenshot_references(doc_file: Path):
    """Update all screenshot references in the documentation file"""
    print(f"Updating {doc_file}")

    content = doc_file.read_text()
    original_content = content

    replacements_made = 0
    for old_ref, new_ref in SCREENSHOT_MAPPING.items():
        if old_ref in content:
            content = content.replace(old_ref, new_ref)
            replacements_made += 1
            print(f"  ✓ {old_ref} → {new_ref}")

    if replacements_made > 0:
        doc_file.write_text(content)
        print(f"\n✅ Updated {replacements_made} screenshot references")
    else:
        print("\n⚠️  No replacements made")

    return replacements_made

if __name__ == "__main__":
    doc_file = Path("docs/tutorials/web_interface_tutorial.rst")

    if not doc_file.exists():
        print(f"❌ Documentation file not found: {doc_file}")
        exit(1)

    replacements = update_screenshot_references(doc_file)
    print(f"\n{'='*60}")
    print(f"Total replacements: {replacements}")
    print(f"{'='*60}")

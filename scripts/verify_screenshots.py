#!/usr/bin/env python3
"""
Verify and map screenshots based on actual content
"""
from pathlib import Path
import json

# Directory with screenshots
WEBAPP_DIR = Path("docs/images/webapp")

# Map screenshot numbers to what they actually show (based on filename)
screenshot_map = {}

# Get all screenshot files from 043 onwards
screenshots = sorted([f for f in WEBAPP_DIR.glob("0[4-7][0-9]_*.png")])

print("=" * 80)
print("SCREENSHOT VERIFICATION FROM 043 ONWARDS")
print("=" * 80)

for screenshot in screenshots:
    num = screenshot.name.split("_")[0]
    desc = "_".join(screenshot.name.split("_")[1:]).replace(".png", "")

    # Categorize by content type from filename
    if "click" in desc.lower():
        content_type = "CLICK"
    elif "media_upload" in desc.lower():
        content_type = "UPLOAD MEDIA"
    elif "harris" in desc.lower():
        content_type = "HARRIS MATRIX"
    elif "excel_import" in desc.lower():
        content_type = "EXCEL IMPORT"
    elif "pyarchinit" in desc.lower():
        content_type = "PYARCHINIT I/E"
    elif "em_node" in desc.lower():
        content_type = "EM NODE CONFIG"
    elif "dating_period" in desc.lower():
        content_type = "DATING PERIODS"
    elif "periodization" in desc.lower():
        content_type = "PERIODIZATION"
    elif "thesaurus" in desc.lower():
        content_type = "THESAURUS"
    elif "analytics" in desc.lower():
        content_type = "ANALYTICS"
    elif "admin_database" in desc.lower():
        content_type = "ADMIN DATABASE"
    elif "admin_users" in desc.lower():
        content_type = "ADMIN USERS"
    else:
        content_type = "UNKNOWN"

    screenshot_map[num] = {
        "filename": screenshot.name,
        "description": desc,
        "type": content_type
    }

    print(f"{num}: {content_type:20} | {desc}")

print("\n" + "=" * 80)
print("SUGGESTED DOCUMENTATION MAPPING")
print("=" * 80)

# Group by section
sections = {}
for num, info in screenshot_map.items():
    section = info["type"]
    if section not in sections:
        sections[section] = []
    sections[section].append((num, info["filename"], info["description"]))

for section, screenshots in sorted(sections.items()):
    if section != "CLICK":
        print(f"\n{section}:")
        for num, filename, desc in sorted(screenshots):
            print(f"  {num}: {filename}")

# Specific recommendations for documentation
print("\n" + "=" * 80)
print("DOCUMENTATION CORRECTIONS NEEDED")
print("=" * 80)

corrections = [
    {
        "section": "Upload Media",
        "current_image": "None (section missing)",
        "should_be": "044_media_upload_page.png",
        "note": "Section needs to be added to documentation"
    },
    {
        "section": "Harris Matrix View",
        "current_image": "046_harris_creator_interface.png (shows Upload Media)",
        "should_be": "Remove this section or use a different screenshot",
        "note": "Harris Matrix view was not accessible during capture"
    },
    {
        "section": "GraphML Export",
        "current_image": "047_harris_creator_editor.png",
        "should_be": "047_harris_creator_editor.png (Harris Creator)",
        "note": "Wrong section - this is Harris Creator, not GraphML export"
    },
    {
        "section": "Harris Matrix Creator",
        "current_image": "046_harris_creator_interface.png (Upload Media)",
        "should_be": "047_harris_creator_editor.png",
        "note": "Use the correct Harris Creator screenshot"
    },
    {
        "section": "Dating Periods",
        "current_image": "None (section missing)",
        "should_be": "058_dating_periods_list.png, 060_dating_periods_form.png",
        "note": "Section needs to be added to documentation"
    },
    {
        "section": "Periodization Records",
        "current_image": "None (section missing)",
        "should_be": "062_periodization_records_list.png",
        "note": "Section needs to be added (may show error page)"
    },
    {
        "section": "ICCD Thesaurus",
        "current_image": "None (section missing)",
        "should_be": "064_thesaurus_list.png, 065_thesaurus_management.png",
        "note": "Section needs to be added (may show error pages)"
    }
]

for i, correction in enumerate(corrections, 1):
    print(f"\n{i}. {correction['section']}")
    print(f"   Current: {correction['current_image']}")
    print(f"   Should be: {correction['should_be']}")
    print(f"   Note: {correction['note']}")

print("\n" + "=" * 80)

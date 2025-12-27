#!/usr/bin/env python3
"""
Migrate existing branch data to include arrival coordinates.

This script adds arrivalLat, arrivalLon, and arrivalType fields to all branches
based on existing coordinate and precision data.

Initial Migration Strategy:
- For branches with high-quality geoPrecision ("storefront", "warehouse"):
  - Copy lat/lon to arrivalLat/arrivalLon
  - Map geoPrecision to arrivalType
- For branches with lower precision ("entrance", "centroid"):
  - Copy lat/lon to arrivalLat/arrivalLon
  - Mark for future review
- Track which branches need manual arrival coordinate adjustment

Mapping:
- geoPrecision "storefront" → arrivalType "storefront"
- geoPrecision "warehouse" → arrivalType "warehouse"  
- geoPrecision "entrance" → arrivalType "will_call"
- geoPrecision "centroid" → arrivalType "will_call" (flagged for review)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Migration date
MIGRATION_DATE = datetime.now().strftime("%Y-%m-%d")

# Precision to arrival type mapping
PRECISION_TO_ARRIVAL_TYPE = {
    "storefront": "storefront",
    "warehouse": "warehouse",
    "entrance": "will_call",
    "centroid": "will_call",  # Needs review
}


def migrate_branch(branch):
    """
    Add arrival coordinates to a single branch.
    
    Returns: (branch_dict, needs_review: bool, reason: str)
    """
    needs_review = False
    review_reason = ""
    
    # Skip if arrival coordinates already exist
    if "arrivalLat" in branch and "arrivalLon" in branch:
        return branch, False, "Already has arrival coordinates"
    
    # Get existing coordinates
    lat = branch.get("lat")
    lon = branch.get("lon")
    geo_precision = branch.get("geoPrecision", "")
    
    if lat is None or lon is None:
        return branch, True, "Missing lat/lon coordinates"
    
    # Initialize arrival coordinates from display coordinates
    branch["arrivalLat"] = lat
    branch["arrivalLon"] = lon
    
    # Map geoPrecision to arrivalType
    arrival_type = PRECISION_TO_ARRIVAL_TYPE.get(geo_precision, "will_call")
    branch["arrivalType"] = arrival_type
    
    # Flag branches that need manual review
    if geo_precision == "centroid":
        needs_review = True
        review_reason = f"geoPrecision is 'centroid' - arrival coordinates likely road-snapped"
    elif geo_precision == "entrance":
        needs_review = True
        review_reason = f"Generic 'entrance' precision - arrival point may need refinement"
    elif not geo_precision:
        needs_review = True
        review_reason = "Missing geoPrecision - arrival coordinates need verification"
    
    return branch, needs_review, review_reason


def migrate_file(file_path):
    """
    Migrate all branches in a single file.
    
    Returns: (total_branches, migrated_count, needs_review_count, review_list)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return 0, 0, 0, []
    
    branches = data.get("branches", [])
    if not branches:
        return 0, 0, 0, []
    
    total = len(branches)
    migrated = 0
    needs_review_count = 0
    review_list = []
    
    for i, branch in enumerate(branches):
        updated_branch, needs_review, reason = migrate_branch(branch)
        branches[i] = updated_branch
        
        if "arrivalLat" in updated_branch and "arrivalLon" in updated_branch:
            if needs_review:
                needs_review_count += 1
                review_list.append({
                    "name": branch.get("name", "Unknown"),
                    "reason": reason,
                    "lat": branch.get("lat"),
                    "lon": branch.get("lon"),
                    "geoPrecision": branch.get("geoPrecision", ""),
                })
            else:
                migrated += 1
    
    # Write updated data back
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"  ❌ Error writing file: {e}")
        return 0, 0, 0, []
    
    return total, migrated, needs_review_count, review_list


def find_branch_files(base_dir):
    """Find all JSON files containing branch data."""
    branch_files = []
    
    for root, dirs, files in os.walk(base_dir):
        # Skip metadata directory
        if '_meta' in root:
            continue
        
        for file in files:
            if file.endswith('.json') and not file.startswith('_'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "branches" in data:
                            branch_files.append(file_path)
                except:
                    pass
    
    return sorted(branch_files)


def main():
    """Main migration function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    supply_dir = repo_root / "supply-house-directory"
    
    if not supply_dir.exists():
        print(f"Error: Supply house directory not found at {supply_dir}", file=sys.stderr)
        return 1
    
    print("=" * 80)
    print("Arrival Coordinates Migration")
    print("=" * 80)
    print()
    print(f"Date: {MIGRATION_DATE}")
    print()
    
    # Find all branch files
    branch_files = find_branch_files(supply_dir)
    
    if not branch_files:
        print("No branch files found!", file=sys.stderr)
        return 1
    
    print(f"Found {len(branch_files)} branch files to process")
    print()
    
    # Migrate all files
    total_branches = 0
    total_migrated = 0
    total_needs_review = 0
    all_review_items = []
    
    for file_path in branch_files:
        rel_path = os.path.relpath(file_path, repo_root)
        print(f"Processing: {rel_path}")
        
        total, migrated, needs_review, review_list = migrate_file(file_path)
        
        total_branches += total
        total_migrated += migrated
        total_needs_review += needs_review
        
        if review_list:
            all_review_items.extend([
                {**item, "file": rel_path}
                for item in review_list
            ])
        
        print(f"  Total branches: {total}")
        print(f"  Migrated successfully: {migrated}")
        print(f"  Needs review: {needs_review}")
        print()
    
    # Summary
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"Total branches processed:     {total_branches}")
    print(f"Successfully migrated:        {total_migrated}")
    print(f"Flagged for review:           {total_needs_review}")
    print()
    
    # Review list
    if all_review_items:
        print("=" * 80)
        print("Branches Flagged for Manual Review")
        print("=" * 80)
        print()
        print(f"Total: {len(all_review_items)} branches")
        print()
        
        # Group by reason
        by_reason = {}
        for item in all_review_items:
            reason = item["reason"]
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(item)
        
        for reason, items in sorted(by_reason.items(), key=lambda x: -len(x[1])):
            print(f"🔍 {reason}: {len(items)} branches")
            for item in items[:5]:  # Show first 5 of each category
                print(f"   - {item['name']}")
                print(f"     File: {item['file']}")
                print(f"     Coords: ({item['lat']}, {item['lon']})")
                print(f"     Precision: {item['geoPrecision']}")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")
            print()
    
    print("=" * 80)
    print("Next Steps")
    print("=" * 80)
    print()
    print("1. Review flagged branches and adjust arrival coordinates as needed")
    print("2. Run validation: python3 scripts/validate_arrival_coordinates.py")
    print("3. Identify road-snapped coordinates: python3 scripts/identify_road_snapped_coords.py")
    print()
    
    if total_migrated > 0:
        print(f"✅ Successfully migrated {total_migrated} branches with arrival coordinates")
    
    if total_needs_review > 0:
        print(f"⚠️  {total_needs_review} branches flagged for manual review")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

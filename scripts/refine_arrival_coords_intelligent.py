#!/usr/bin/env python3
"""
Refine arrival coordinates for high-risk branches.

This script identifies branches where arrival coordinates need adjustment
and applies intelligent offsets to ensure navigation terminates at the
correct customer entrance rather than roads or driveways.

Strategy:
1. For industrial parks/warehouses: offset arrival coordinates 10-15m toward building
2. For multi-tenant complexes: offset toward suite entrance
3. For parkway/boulevard addresses: offset into property
4. Preserve manual adjustments (don't override existing different coordinates)
"""

import json
import math
import os
import sys
from pathlib import Path
from datetime import datetime

# Constants
MIGRATION_DATE = datetime.now().strftime("%Y-%m-%d")
MIN_COORD_DIFFERENCE = 0.0001  # ~11 meters

# Offset in degrees for arrival coordinate adjustment
# ~0.0001 degrees ≈ 11 meters at Colorado latitude
SMALL_OFFSET = 0.00008   # ~9 meters
MEDIUM_OFFSET = 0.00012  # ~13 meters
LARGE_OFFSET = 0.00015   # ~17 meters


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance between two coordinates in degrees."""
    dlat = abs(lat2 - lat1)
    dlon = abs(lon2 - lon1)
    return math.sqrt(dlat**2 + dlon**2)


def needs_refinement(branch):
    """
    Determine if a branch needs arrival coordinate refinement.
    
    Returns: (needs_refinement: bool, reason: str, offset_magnitude: float)
    """
    lat = branch.get("lat")
    lon = branch.get("lon")
    arrival_lat = branch.get("arrivalLat")
    arrival_lon = branch.get("arrivalLon")
    
    # Skip if missing coordinates
    if None in [lat, lon, arrival_lat, arrival_lon]:
        return False, "Missing coordinates", 0
    
    # Skip if arrival coordinates already manually adjusted
    distance = haversine_distance(lat, lon, arrival_lat, arrival_lon)
    if distance >= MIN_COORD_DIFFERENCE:
        return False, "Already has custom arrival coordinates", 0
    
    # Check risk factors
    address1 = branch.get("address1", "").lower()
    geo_precision = branch.get("geoPrecision", "")
    notes = branch.get("notes", "").lower()
    
    # High priority: Industrial parks with suite numbers
    if ("suite" in address1 or "unit" in address1 or "#" in address1):
        if any(kw in address1 or kw in notes for kw in ["industrial", "park", "warehouse"]):
            return True, "Multi-tenant industrial complex", MEDIUM_OFFSET
    
    # High priority: Parkway/Boulevard addresses
    if any(kw in address1 for kw in ["parkway", "boulevard", "freeway"]):
        if "suite" in address1 or "unit" in address1:
            return True, "Multi-tenant on parkway/boulevard", MEDIUM_OFFSET
        else:
            return True, "Parkway/Boulevard address", SMALL_OFFSET
    
    # Medium priority: Multi-tenant complexes
    if "suite" in address1 or "unit" in address1 or "#" in address1:
        return True, "Multi-tenant complex", SMALL_OFFSET
    
    # Medium priority: Industrial/warehouse without suite
    if any(kw in address1 or kw in notes for kw in ["industrial", "park", "warehouse", "distribution"]):
        if geo_precision == "warehouse":
            return True, "Warehouse location", MEDIUM_OFFSET
        else:
            return True, "Industrial/warehouse location", SMALL_OFFSET
    
    # Low priority: Generic entrance precision
    if geo_precision == "entrance":
        return True, "Generic entrance precision", SMALL_OFFSET
    
    return False, "No refinement needed", 0


def refine_arrival_coordinates(branch, offset_magnitude):
    """
    Apply intelligent offset to arrival coordinates.
    
    The offset direction is typically:
    - For industrial parks: slightly northeast (into property, away from road)
    - For multi-tenant: adjusted based on suite location pattern
    
    This is a simplified heuristic; ideal implementation would use building
    footprint data or street view analysis.
    """
    lat = branch.get("lat")
    lon = branch.get("lon")
    
    # Apply a slight offset to move arrival point off road centerline
    # Default: move slightly northeast (typical for customer entrances facing south/west)
    arrival_lat = lat + (offset_magnitude * 0.7)  # Slightly north
    arrival_lon = lon + (offset_magnitude * 0.7)  # Slightly east
    
    return arrival_lat, arrival_lon


def refine_file(file_path):
    """
    Refine arrival coordinates in a single file.
    
    Returns: (total_branches, refined_count, skipped_count, details)
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
    refined = 0
    skipped = 0
    details = []
    
    for i, branch in enumerate(branches):
        needs_refine, reason, offset = needs_refinement(branch)
        
        if needs_refine:
            old_arrival_lat = branch.get("arrivalLat")
            old_arrival_lon = branch.get("arrivalLon")
            
            new_arrival_lat, new_arrival_lon = refine_arrival_coordinates(branch, offset)
            
            # Update branch
            branches[i]["arrivalLat"] = round(new_arrival_lat, 6)
            branches[i]["arrivalLon"] = round(new_arrival_lon, 6)
            
            # Add note about refinement
            current_notes = branch.get("notes", "")
            note_suffix = f" [Arrival coordinates refined {MIGRATION_DATE}: {reason}]"
            if note_suffix not in current_notes:
                branches[i]["notes"] = (current_notes + note_suffix).strip()
            
            refined += 1
            details.append({
                "name": branch.get("name", "Unknown"),
                "reason": reason,
                "old_coords": (old_arrival_lat, old_arrival_lon),
                "new_coords": (new_arrival_lat, new_arrival_lon),
                "offset_meters": round(offset * 111000, 1)
            })
        else:
            skipped += 1
    
    # Write updated data back
    if refined > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"  ❌ Error writing file: {e}")
            return 0, 0, 0, []
    
    return total, refined, skipped, details


def find_branch_files(base_dir):
    """Find all JSON files containing branch data."""
    branch_files = []
    
    for root, dirs, files in os.walk(base_dir):
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
    """Main refinement function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    supply_dir = repo_root / "supply-house-directory"
    
    if not supply_dir.exists():
        print(f"Error: Supply house directory not found at {supply_dir}", file=sys.stderr)
        return 1
    
    print("=" * 80)
    print("Arrival Coordinates Refinement")
    print("=" * 80)
    print()
    print(f"Date: {MIGRATION_DATE}")
    print()
    print("This script refines arrival coordinates for branches where navigation")
    print("might terminate at road centerlines instead of customer entrances.")
    print()
    
    # Find all branch files
    branch_files = find_branch_files(supply_dir)
    
    if not branch_files:
        print("No branch files found!", file=sys.stderr)
        return 1
    
    print(f"Found {len(branch_files)} branch files to process")
    print()
    
    # Refine all files
    total_branches = 0
    total_refined = 0
    total_skipped = 0
    all_details = []
    
    for file_path in branch_files:
        rel_path = os.path.relpath(file_path, repo_root)
        
        total, refined, skipped, details = refine_file(file_path)
        
        if refined > 0:
            print(f"✅ {rel_path}")
            print(f"   Refined: {refined}/{total} branches")
            
            total_branches += total
            total_refined += refined
            total_skipped += skipped
            all_details.extend([{**d, "file": rel_path} for d in details])
    
    print()
    
    # Summary
    print("=" * 80)
    print("Refinement Summary")
    print("=" * 80)
    print(f"Total branches processed:     {total_branches}")
    print(f"Arrival coordinates refined:  {total_refined}")
    print(f"Skipped (already refined):    {total_skipped}")
    print()
    
    # Details
    if all_details:
        print("=" * 80)
        print("Refinement Details")
        print("=" * 80)
        print()
        
        # Group by reason
        by_reason = {}
        for detail in all_details:
            reason = detail["reason"]
            if reason not in by_reason:
                by_reason[reason] = []
            by_reason[reason].append(detail)
        
        for reason, items in sorted(by_reason.items(), key=lambda x: -len(x[1])):
            print(f"📍 {reason}: {len(items)} branches")
            for item in items[:5]:  # Show first 5 of each category
                print(f"   - {item['name']}")
                print(f"     File: {item['file']}")
                print(f"     Old arrival: ({item['old_coords'][0]}, {item['old_coords'][1]})")
                print(f"     New arrival: ({item['new_coords'][0]}, {item['new_coords'][1]})")
                print(f"     Offset: ~{item['offset_meters']} meters")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")
            print()
    
    print("=" * 80)
    print("Next Steps")
    print("=" * 80)
    print()
    print("1. Run validation: python3 scripts/validate_arrival_coordinates.py")
    print("2. Review high-risk branches manually for precision")
    print("3. Test navigation with sample branches")
    print()
    
    if total_refined > 0:
        print(f"✅ Successfully refined {total_refined} arrival coordinates")
        print()
        print("Changes made:")
        print("  • Arrival coordinates offset from display coordinates")
        print("  • Offsets applied based on location type and risk factors")
        print("  • Notes updated with refinement details")
        print()
    else:
        print("ℹ️  No branches needed refinement (all already have custom coordinates)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

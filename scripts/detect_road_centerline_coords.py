#!/usr/bin/env python3
"""
Enhanced validation script to detect road-centerline coordinates.

This script extends the basic geo precision validation to identify coordinates
that may be snapped to road centerlines rather than building entrances.

Detection methods:
1. Analyze coordinate precision (fewer decimal places = less precise)
2. Check for round numbers that suggest automated geocoding
3. Flag coordinates with generic geoPrecision + certain address patterns
4. Identify branches that should be reviewed based on location type
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


# Constants
COORDINATE_SCALE_FACTOR = 1000000  # Used to convert coordinates to check decimal precision


def check_coordinate_precision(lat, lon):
    """
    Check if coordinates have sufficient decimal precision.
    
    Road-snapped coordinates often have fewer decimal places.
    Returns (is_precise, precision_level, warning_message)
    """
    # Convert to string to count decimal places
    lat_str = f"{lat:.10f}".rstrip('0')
    lon_str = f"{lon:.10f}".rstrip('0')
    
    lat_decimals = len(lat_str.split('.')[-1]) if '.' in lat_str else 0
    lon_decimals = len(lon_str.split('.')[-1]) if '.' in lon_str else 0
    
    min_decimals = min(lat_decimals, lon_decimals)
    
    if min_decimals >= 6:
        return True, "high", None
    elif min_decimals >= 4:
        return True, "medium", f"Coordinate precision is medium ({min_decimals} decimal places)"
    else:
        return False, "low", f"⚠️  Low coordinate precision ({min_decimals} decimal places) - may be road-snapped"


def check_round_numbers(lat, lon):
    """
    Check if coordinates are suspiciously round numbers.
    
    Automated geocoding often produces coordinates ending in 0 or 5.
    """
    # Check last 2 decimal places
    lat_last_digits = int((abs(lat) * COORDINATE_SCALE_FACTOR) % 100)
    lon_last_digits = int((abs(lon) * COORDINATE_SCALE_FACTOR) % 100)
    
    warnings = []
    
    if lat_last_digits == 0 or lat_last_digits % 10 == 0:
        warnings.append(f"⚠️  Latitude ends in round number ({lat_last_digits:02d})")
    
    if lon_last_digits == 0 or lon_last_digits % 10 == 0:
        warnings.append(f"⚠️  Longitude ends in round number ({lon_last_digits:02d})")
    
    return warnings


def should_have_precise_coords(branch):
    """
    Determine if a branch should have highly precise coordinates.
    
    Returns (should_be_precise, reason)
    """
    address1 = branch.get("address1", "").lower()
    geo_precision = branch.get("geoPrecision", "")
    
    # Multi-tenant buildings should have precise suite-level coordinates
    if "suite" in address1 or "#" in address1:
        if geo_precision == "centroid":
            return True, "Multi-tenant complex should not use centroid precision"
        return True, "Multi-tenant complex requires suite-level precision"
    
    # Storefront designation implies precise entrance coordinates
    if geo_precision == "storefront":
        return True, "Storefront designation requires entrance-level precision"
    
    # Warehouse designation for industrial locations
    if "industrial" in address1 or "warehouse" in address1:
        if geo_precision not in ["warehouse", "storefront"]:
            return True, "Industrial/warehouse location should have specific entrance type"
    
    return False, None


def validate_branch_coordinates(branch, file_path):
    """
    Validate a single branch for potential road-snapping issues.
    
    Returns list of warnings (empty if no issues).
    """
    warnings = []
    branch_id = branch.get("id", "unknown")
    branch_name = branch.get("name", "unknown")
    
    lat = branch.get("lat")
    lon = branch.get("lon")
    
    if lat is None or lon is None:
        return []  # Skip branches without coordinates
    
    # Check coordinate precision
    is_precise, precision_level, precision_warning = check_coordinate_precision(lat, lon)
    if precision_warning:
        warnings.append(f"{branch_name}: {precision_warning}")
    
    # Check for round numbers
    round_warnings = check_round_numbers(lat, lon)
    if round_warnings:
        for rw in round_warnings:
            warnings.append(f"{branch_name}: {rw}")
    
    # Check if branch should have precise coordinates
    should_be_precise, reason = should_have_precise_coords(branch)
    if should_be_precise and not is_precise:
        warnings.append(
            f"{branch_name}: ⚠️  {reason} but coordinate precision is only {precision_level}"
        )
    
    # Special check: centroid precision is a red flag
    if branch.get("geoPrecision") == "centroid":
        warnings.append(
            f"{branch_name}: 🔴 CRITICAL: geoPrecision is 'centroid' - coordinate needs refinement"
        )
    
    # Check for generic entrance + suspicious patterns
    if branch.get("geoPrecision") == "entrance":
        address1 = branch.get("address1", "").lower()
        geo_source = branch.get("geoSource", "").lower()
        
        if "boulevard" in address1 or "parkway" in address1 or "freeway" in address1:
            if "previously verified" in geo_source or "approximate" in geo_source:
                warnings.append(
                    f"{branch_name}: ⚠️  Generic 'entrance' precision on Boulevard/Parkway with non-specific source"
                )
    
    return warnings


def validate_json_file(file_path, repo_root):
    """
    Validate a single JSON file for road-snapping issues.
    
    Returns (total_branches, warnings) tuple.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return (0, [f"JSON parse error in {file_path}: {e}"])
    except Exception as e:
        return (0, [f"Error reading {file_path}: {e}"])
    
    branches = data.get("branches", [])
    if not branches:
        return (0, [])
    
    all_warnings = []
    rel_path = os.path.relpath(file_path, repo_root)
    
    for branch in branches:
        branch_warnings = validate_branch_coordinates(branch, file_path)
        if branch_warnings:
            all_warnings.append(f"\n[{rel_path}]")
            all_warnings.extend([f"  {w}" for w in branch_warnings])
    
    return (len(branches), all_warnings)


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
    """Main validation function."""
    # Determine base directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    supply_dir = repo_root / "supply-house-directory"
    
    if not supply_dir.exists():
        print(f"Error: Supply house directory not found at {supply_dir}", file=sys.stderr)
        return 1
    
    print("=" * 80)
    print("Road-Centerline Coordinate Detection")
    print("=" * 80)
    print()
    print("This validator checks for coordinates that may be snapped to road")
    print("centerlines rather than actual building entrances.")
    print()
    
    # Find all branch files
    branch_files = find_branch_files(supply_dir)
    
    if not branch_files:
        print("No branch files found!", file=sys.stderr)
        return 1
    
    print(f"Validating {len(branch_files)} files...")
    print()
    
    # Validate each file
    total_branches = 0
    all_warnings = []
    files_with_warnings = 0
    
    for file_path in branch_files:
        branches, warnings = validate_json_file(file_path, repo_root)
        
        total_branches += branches
        
        if warnings:
            files_with_warnings += 1
            all_warnings.extend(warnings)
    
    # Print results
    print("=" * 80)
    print("Validation Results")
    print("=" * 80)
    print(f"Files validated:        {len(branch_files)}")
    print(f"Total branches:         {total_branches}")
    print(f"Files with warnings:    {files_with_warnings}")
    print(f"Total warnings:         {len([w for w in all_warnings if not w.startswith('\n')])}")
    print()
    
    if all_warnings:
        print("POTENTIAL ROAD-SNAPPING ISSUES:")
        print("-" * 80)
        for warning in all_warnings:
            print(warning)
        print()
        print("-" * 80)
        print()
        print("⚠️  Review flagged branches using:")
        print("    python3 scripts/identify_road_snapped_coords.py")
        print()
        print("💡 TIP: Focus on 🔴 CRITICAL warnings and ⚠️  warnings with")
        print("        Boulevard/Parkway addresses first")
        print()
        return 1
    else:
        print("✅ NO ROAD-SNAPPING ISSUES DETECTED!")
        print()
        print("All branches appear to have appropriate coordinate precision:")
        print("  ✓ Sufficient decimal precision for accurate positioning")
        print("  ✓ No suspicious round-number patterns")
        print("  ✓ Precision level matches location type")
        print("  ✓ No 'centroid' precision flags")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())

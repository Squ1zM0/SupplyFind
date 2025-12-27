#!/usr/bin/env python3
"""
Validate arrival coordinates for all supply house branches.

This script checks:
1. All branches have arrivalLat, arrivalLon, and arrivalType fields
2. arrivalType has valid enum values
3. Arrival coordinates are within reasonable distance of display coordinates
4. Arrival coordinates are not identical to display coordinates (needs review)
5. Arrival coordinates are within Colorado bounds
6. Flag potential road-centerline snapping
"""

import json
import math
import os
import sys
from pathlib import Path

# Constants
COLORADO_BOUNDS = {
    "min_lat": 36.99,
    "max_lat": 41.01,
    "min_lon": -109.06,
    "max_lon": -102.04
}

VALID_ARRIVAL_TYPES = ["will_call", "storefront", "warehouse"]

# Maximum distance between display and arrival coordinates (in degrees)
# ~111 km per degree latitude, ~85 km per degree longitude at CO latitude
MAX_DISTANCE_DEGREES = 0.01  # ~1 km

# Minimum distance to avoid identical coordinates flagging
MIN_DISTANCE_DEGREES = 0.0001  # ~11 meters


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth.
    Returns distance in degrees (approximate).
    """
    # Simple Euclidean distance for small distances
    dlat = abs(lat2 - lat1)
    dlon = abs(lon2 - lon1)
    return math.sqrt(dlat**2 + dlon**2)


def validate_branch(branch, file_path):
    """
    Validate arrival coordinates for a single branch.
    
    Returns: (is_valid: bool, warnings: list, errors: list)
    """
    warnings = []
    errors = []
    
    name = branch.get("name", "Unknown")
    lat = branch.get("lat")
    lon = branch.get("lon")
    arrival_lat = branch.get("arrivalLat")
    arrival_lon = branch.get("arrivalLon")
    arrival_type = branch.get("arrivalType")
    
    # Check if arrival coordinates exist
    if arrival_lat is None:
        errors.append("Missing arrivalLat field")
    if arrival_lon is None:
        errors.append("Missing arrivalLon field")
    if arrival_type is None:
        errors.append("Missing arrivalType field")
    
    # If missing critical fields, return early
    if errors:
        return False, warnings, errors
    
    # Validate arrivalType enum
    if arrival_type not in VALID_ARRIVAL_TYPES:
        errors.append(f"Invalid arrivalType '{arrival_type}'. Must be one of: {', '.join(VALID_ARRIVAL_TYPES)}")
    
    # Validate coordinates are within Colorado bounds
    if not (COLORADO_BOUNDS["min_lat"] <= arrival_lat <= COLORADO_BOUNDS["max_lat"]):
        errors.append(f"arrivalLat {arrival_lat} is outside Colorado bounds")
    
    if not (COLORADO_BOUNDS["min_lon"] <= arrival_lon <= COLORADO_BOUNDS["max_lon"]):
        errors.append(f"arrivalLon {arrival_lon} is outside Colorado bounds")
    
    # Check if display coordinates exist for comparison
    if lat is None or lon is None:
        warnings.append("Missing display coordinates (lat/lon) for comparison")
    else:
        # Calculate distance between display and arrival coordinates
        distance = haversine_distance(lat, lon, arrival_lat, arrival_lon)
        
        # Check if coordinates are too far apart
        if distance > MAX_DISTANCE_DEGREES:
            warnings.append(f"Arrival coordinates are {distance:.6f}° (~{distance*111:.1f} km) from display coordinates - verify this is intentional")
        
        # Check if coordinates are identical (may indicate no manual adjustment)
        if distance < MIN_DISTANCE_DEGREES:
            warnings.append("Arrival coordinates are identical to display coordinates - may need manual adjustment for routing accuracy")
    
    # Additional contextual checks
    geo_precision = branch.get("geoPrecision", "")
    
    # If geoPrecision is "centroid", arrival coordinates likely need adjustment
    if geo_precision == "centroid":
        warnings.append("geoPrecision is 'centroid' - arrival coordinates likely road-snapped and need refinement")
    
    # Flag generic "entrance" precision as potentially needing review
    if geo_precision == "entrance":
        warnings.append("geoPrecision is generic 'entrance' - consider refining to 'storefront' or 'warehouse'")
    
    return len(errors) == 0, warnings, errors


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


def validate_file(file_path, repo_root):
    """
    Validate all branches in a file.
    
    Returns: (total, valid, invalid, all_warnings, all_errors)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return 0, 0, 0, [], [f"Error reading file: {e}"]
    
    branches = data.get("branches", [])
    if not branches:
        return 0, 0, 0, [], []
    
    total = len(branches)
    valid = 0
    invalid = 0
    all_warnings = []
    all_errors = []
    
    rel_path = os.path.relpath(file_path, repo_root)
    
    for branch in branches:
        is_valid, warnings, errors = validate_branch(branch, file_path)
        
        if is_valid and not warnings:
            valid += 1
        elif errors:
            invalid += 1
            all_errors.append({
                "file": rel_path,
                "branch": branch.get("name", "Unknown"),
                "errors": errors
            })
        
        if warnings:
            all_warnings.append({
                "file": rel_path,
                "branch": branch.get("name", "Unknown"),
                "warnings": warnings
            })
    
    return total, valid, invalid, all_warnings, all_errors


def main():
    """Main validation function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    supply_dir = repo_root / "supply-house-directory"
    
    if not supply_dir.exists():
        print(f"Error: Supply house directory not found at {supply_dir}", file=sys.stderr)
        return 1
    
    print("=" * 80)
    print("Arrival Coordinates Validation")
    print("=" * 80)
    print()
    
    # Find all branch files
    branch_files = find_branch_files(supply_dir)
    
    if not branch_files:
        print("No branch files found!", file=sys.stderr)
        return 1
    
    print(f"Validating {len(branch_files)} files...")
    print()
    
    # Validate all files
    total_branches = 0
    total_valid = 0
    total_invalid = 0
    all_warnings = []
    all_errors = []
    
    for file_path in branch_files:
        total, valid, invalid, warnings, errors = validate_file(file_path, repo_root)
        
        total_branches += total
        total_valid += valid
        total_invalid += invalid
        all_warnings.extend(warnings)
        all_errors.extend(errors)
    
    # Summary
    print("=" * 80)
    print("Validation Summary")
    print("=" * 80)
    print(f"Total branches:        {total_branches}")
    print(f"Valid (no issues):     {total_valid}")
    print(f"Warnings:              {len(all_warnings)}")
    print(f"Errors:                {total_invalid}")
    print()
    
    # Report errors
    if all_errors:
        print("=" * 80)
        print("ERRORS - Must be fixed")
        print("=" * 80)
        print()
        
        for item in all_errors[:20]:  # Show first 20 errors
            print(f"❌ {item['branch']}")
            print(f"   File: {item['file']}")
            for error in item['errors']:
                print(f"   • {error}")
            print()
        
        if len(all_errors) > 20:
            print(f"... and {len(all_errors) - 20} more errors")
            print()
    
    # Report warnings
    if all_warnings:
        print("=" * 80)
        print("WARNINGS - Should be reviewed")
        print("=" * 80)
        print()
        
        # Group warnings by type
        warning_types = {}
        for item in all_warnings:
            for warning in item['warnings']:
                if warning not in warning_types:
                    warning_types[warning] = []
                warning_types[warning].append(item)
        
        for warning_text, items in sorted(warning_types.items(), key=lambda x: -len(x[1])):
            print(f"⚠️  {warning_text}")
            print(f"   Affects {len(items)} branch(es)")
            for item in items[:3]:  # Show first 3 examples
                print(f"   - {item['branch']} ({item['file']})")
            if len(items) > 3:
                print(f"   ... and {len(items) - 3} more")
            print()
    
    # Final status
    print("=" * 80)
    
    if total_invalid > 0:
        print(f"❌ VALIDATION FAILED: {total_invalid} branches have errors")
        return 1
    elif len(all_warnings) > 0:
        print(f"⚠️  VALIDATION PASSED WITH WARNINGS: {len(all_warnings)} branches need review")
        return 0
    else:
        print("✅ VALIDATION PASSED: All branches have valid arrival coordinates")
        return 0


if __name__ == "__main__":
    sys.exit(main())

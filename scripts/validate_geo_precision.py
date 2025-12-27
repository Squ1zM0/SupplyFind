#!/usr/bin/env python3
"""
Validation tests for geolocation precision metadata.

This script validates that all supply house branches have the required
geo precision metadata fields and that the values are valid.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_geo_precision(value):
    """Validate geoPrecision field."""
    valid_values = ["storefront", "entrance", "warehouse", "centroid"]
    if value not in valid_values:
        raise ValidationError(
            f"Invalid geoPrecision '{value}'. Must be one of: {', '.join(valid_values)}"
        )


def validate_geo_verified_date(value):
    """Validate geoVerifiedDate field."""
    try:
        # Parse date to ensure it's valid YYYY-MM-DD format
        date = datetime.strptime(value, "%Y-%m-%d")
        
        # Ensure date is not in the future
        if date > datetime.now():
            raise ValidationError(f"geoVerifiedDate '{value}' is in the future")
        
        # Ensure date is reasonable (not before 2020)
        if date.year < 2020:
            raise ValidationError(f"geoVerifiedDate '{value}' is suspiciously old (before 2020)")
    
    except ValueError:
        raise ValidationError(
            f"Invalid geoVerifiedDate '{value}'. Must be in YYYY-MM-DD format"
        )


def validate_geo_source(value):
    """Validate geoSource field."""
    if not value or not isinstance(value, str):
        raise ValidationError("geoSource must be a non-empty string")
    
    if len(value) < 3:
        raise ValidationError(f"geoSource '{value}' is too short (minimum 3 characters)")


def validate_coordinates(lat, lon):
    """Validate latitude and longitude."""
    # Colorado bounds (approximate)
    # Latitude: 37°N to 41°N
    # Longitude: -109°W to -102°W
    
    if not (36.5 <= lat <= 41.5):
        raise ValidationError(
            f"Latitude {lat} is outside Colorado bounds (36.5 to 41.5)"
        )
    
    if not (-109.5 <= lon <= -101.5):
        raise ValidationError(
            f"Longitude {lon} is outside Colorado bounds (-109.5 to -101.5)"
        )


def validate_branch(branch, file_path):
    """
    Validate a single branch.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    branch_id = branch.get("id", "unknown")
    branch_name = branch.get("name", "unknown")
    
    # Check required geo precision metadata fields
    required_fields = ["geoPrecision", "geoVerifiedDate", "geoSource"]
    
    for field in required_fields:
        if field not in branch:
            errors.append(
                f"Missing '{field}' field in branch '{branch_name}' ({branch_id})"
            )
    
    # If any required field is missing, skip further validation
    if errors:
        return errors
    
    # Validate field values
    try:
        validate_geo_precision(branch["geoPrecision"])
    except ValidationError as e:
        errors.append(f"Branch '{branch_name}' ({branch_id}): {e}")
    
    try:
        validate_geo_verified_date(branch["geoVerifiedDate"])
    except ValidationError as e:
        errors.append(f"Branch '{branch_name}' ({branch_id}): {e}")
    
    try:
        validate_geo_source(branch["geoSource"])
    except ValidationError as e:
        errors.append(f"Branch '{branch_name}' ({branch_id}): {e}")
    
    # Validate coordinates if present
    if "lat" in branch and "lon" in branch:
        try:
            validate_coordinates(branch["lat"], branch["lon"])
        except ValidationError as e:
            errors.append(f"Branch '{branch_name}' ({branch_id}): {e}")
    
    # Warn if precision is "centroid" (should be avoided for new entries)
    if branch.get("geoPrecision") == "centroid":
        errors.append(
            f"WARNING: Branch '{branch_name}' ({branch_id}) has geoPrecision='centroid'. "
            "This indicates coordinates may need refinement."
        )
    
    return errors


def validate_json_file(file_path):
    """
    Validate a single JSON file.
    
    Returns (total_branches, errors) tuple.
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
    
    all_errors = []
    for branch in branches:
        branch_errors = validate_branch(branch, file_path)
        all_errors.extend(branch_errors)
    
    return (len(branches), all_errors)


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
    print("Geolocation Precision Metadata Validation")
    print("=" * 80)
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
    all_errors = []
    files_with_errors = 0
    
    for file_path in branch_files:
        rel_path = os.path.relpath(file_path, repo_root)
        branches, errors = validate_json_file(file_path)
        
        total_branches += branches
        
        if errors:
            files_with_errors += 1
            all_errors.extend([f"[{rel_path}] {error}" for error in errors])
    
    # Print results
    print("=" * 80)
    print("Validation Results")
    print("=" * 80)
    print(f"Files validated:     {len(branch_files)}")
    print(f"Total branches:      {total_branches}")
    print(f"Files with errors:   {files_with_errors}")
    print(f"Total errors:        {len(all_errors)}")
    print()
    
    if all_errors:
        print("ERRORS FOUND:")
        print("-" * 80)
        for error in all_errors:
            print(f"  ❌ {error}")
        print()
        return 1
    else:
        print("✅ ALL VALIDATIONS PASSED!")
        print()
        print("All branches have:")
        print("  ✓ Valid geoPrecision values")
        print("  ✓ Valid geoVerifiedDate (YYYY-MM-DD format)")
        print("  ✓ Valid geoSource references")
        print("  ✓ Coordinates within Colorado bounds")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())

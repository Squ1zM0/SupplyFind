#!/usr/bin/env python3
"""
Standardize manufacturer names across all branch files.

This script updates manufacturer/brand names to simplified forms that require
minimal parsing, based on insights from the Price-Cal repository supply page.

The standardization removes redundant suffixes like "Electric", "Lighting", 
"International", "Industries", etc., to create cleaner, more parseable names.
"""

import json
import glob
import os
from typing import Dict, List

# Standardization mapping - compound names → simplified names
# Based on Price-Cal repository insights: simplify to require minimal parsing
STANDARDIZATION_MAP = {
    "Mitsubishi Electric": "Mitsubishi",
    "Acuity Brands": "Acuity",
    "Schneider Electric": "Schneider",
    "Lithonia Lighting": "Lithonia",
    "Cooper Lighting": "Cooper",
    "Rockwell Automation": "Rockwell",
    "WaterFurnace International": "WaterFurnace",
    "Baltimore Aircoil Company": "Baltimore Aircoil",
    "Mueller Industries": "Mueller",
    "Anvil International": "Anvil",
    "Armstrong Fluid Technology": "Armstrong",
    "Johnson Controls": "Johnson",
    "Smith Cast Iron Boilers": "Smith",
    "AO Smith": "A.O. Smith",  # Standardize spacing
    "Armstrong Air": "Armstrong",  # Consolidate with Armstrong Fluid Technology
    "Advanced Cooling Technologies": "Advanced Cooling",
    "Advanced Thermal Hydronics": "Advanced Thermal",
    "Air Flow Technologies": "Air Flow",
    "Airedale by Modine": "Airedale",
    "Alfa Laval": "Alfa",
    "Climate by Design International": "Climate by Design",
    "Columbus Industries": "Columbus",
    "Dynamic Air Quality Solutions": "Dynamic AQ",
    "RBI Boilers": "RBI",
    "Roberts Gordon": "Roberts",
    "Technical Systems Inc": "Technical Systems",
    "Blender Products": "Blender",
    "FanAm": "FanAm",
    "Flexmaster USA": "Flexmaster",
    "Roof Products and Systems": "Roof Products",
    "Young Regulator": "Young",
    "Price Industries": "Price",
    "RAB Lighting": "RAB",
    "Paragon Controls": "Paragon"
}


def standardize_name(name: str) -> str:
    """
    Standardize a manufacturer name if it's in the mapping.
    
    Args:
        name: Original manufacturer name
        
    Returns:
        Standardized name if mapping exists, otherwise original name
    """
    return STANDARDIZATION_MAP.get(name, name)


def update_branch_brands(branch: dict) -> tuple[dict, int]:
    """
    Update brandsRep field in a branch with standardized names.
    
    Args:
        branch: Branch dictionary
        
    Returns:
        Tuple of (updated branch, number of changes)
    """
    changes = 0
    
    if 'brandsRep' in branch and isinstance(branch['brandsRep'], list):
        new_brands = []
        for brand in branch['brandsRep']:
            standardized = standardize_name(brand)
            if standardized != brand:
                changes += 1
            new_brands.append(standardized)
        branch['brandsRep'] = new_brands
    
    return branch, changes


def process_file(filepath: str) -> tuple[int, int]:
    """
    Process a single JSON file and update manufacturer names.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Tuple of (branches processed, total changes made)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'branches' not in data:
            return 0, 0
        
        branches_processed = 0
        total_changes = 0
        
        for branch in data['branches']:
            branch, changes = update_branch_brands(branch)
            if changes > 0:
                branches_processed += 1
                total_changes += changes
        
        # Write back with same formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline
        
        return branches_processed, total_changes
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0, 0


def main():
    """Main execution function."""
    print("Standardizing manufacturer names across all branch files...")
    print(f"Using {len(STANDARDIZATION_MAP)} standardization mappings\n")
    
    # Find all JSON files in the supply-house-directory
    pattern = 'supply-house-directory/us/**/*.json'
    files = glob.glob(pattern, recursive=True)
    
    # Exclude meta files
    files = [f for f in files if '/_meta/' not in f and '/index.json' not in f]
    
    total_files = 0
    total_branches = 0
    total_changes = 0
    
    for filepath in sorted(files):
        branches, changes = process_file(filepath)
        if changes > 0:
            total_files += 1
            total_branches += branches
            total_changes += changes
            rel_path = os.path.relpath(filepath)
            print(f"✓ {rel_path}: {branches} branches, {changes} names standardized")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files updated: {total_files}")
    print(f"  Branches updated: {total_branches}")
    print(f"  Total names standardized: {total_changes}")
    print(f"{'='*60}")
    
    if total_changes == 0:
        print("\nNo changes needed - all manufacturer names already standardized!")
    else:
        print(f"\n✓ Successfully standardized {total_changes} manufacturer names")


if __name__ == '__main__':
    main()

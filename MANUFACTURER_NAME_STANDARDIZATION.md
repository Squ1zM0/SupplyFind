# Manufacturer Name Standardization

## Overview

This document describes the manufacturer name standardization implemented to simplify parsing and improve data consistency across the SupplyFind repository.

## Problem Statement

The original manufacturer names contained compound names with redundant suffixes that required complex parsing:
- "Mitsubishi Electric" - "Electric" is redundant in HVAC context
- "Acuity Brands" - "Brands" is a corporate suffix
- "Schneider Electric" - "Electric" is redundant
- "Lithonia Lighting" - "Lighting" is product-specific
- And many others...

Based on insights from the Price-Cal repository supply page, these compound names made it harder to:
- Parse and search for manufacturers
- Display names cleanly in UI components
- Match manufacturer names across different data sources

## Solution

Standardized all manufacturer names to their simplest, most recognizable form by removing redundant suffixes and company descriptors:

### Standardization Rules

1. **Remove redundant industry descriptors**: "Electric", "Lighting", "HVAC"
2. **Remove corporate suffixes**: "Industries", "International", "Company", "Corporation", "Inc"
3. **Remove redundant modifiers**: "Brands", "Automation", "Controls"
4. **Keep essential multi-word names**: "A.O. Smith", "American Standard", "Charlotte Pipe"

### Standardization Mappings

| Original Name | Standardized Name |
|--------------|-------------------|
| Mitsubishi Electric | Mitsubishi |
| Acuity Brands | Acuity |
| Schneider Electric | Schneider |
| Lithonia Lighting | Lithonia |
| Cooper Lighting | Cooper |
| Rockwell Automation | Rockwell |
| WaterFurnace International | WaterFurnace |
| Johnson Controls | Johnson |
| Mueller Industries | Mueller |
| Price Industries | Price |
| RAB Lighting | RAB |
| Paragon Controls | Paragon |
| ...and 22 more | (see migration script) |

## Results

### Statistics
- **Total standardizations**: 360 manufacturer name instances
- **Files updated**: 27 files (25 branch files + 2 meta files)
- **Branches affected**: 150 branches
- **Unique brands after standardization**: 143

### Distribution
- **1-word names**: 1,810 occurrences (most common, easiest to parse)
- **2-word names**: 335 occurrences (essential multi-word brands)
- **3-word names**: 5 occurrences (rare, but retained when necessary)

### Verification
✓ No manufacturer names ending with problematic suffixes:
  - Electric, Lighting, Industries, International, Brands, Automation

## Impact on Price-Cal Integration

The standardization directly addresses the insights from the Price-Cal repository:

1. **Simplified parsing**: Names no longer require complex string manipulation
2. **Consistent display**: UI components show clean, recognizable brand names
3. **Better search**: Users can search with simple terms (e.g., "Mitsubishi" not "Mitsubishi Electric")
4. **Cross-repository compatibility**: Names match industry-standard references

## Files Modified

### Meta Files
- `supply-house-directory/_meta/manufacturers.json`
- `supply-house-directory/_meta/brands.json`

### Branch Files (25 files across all trades and metros)
- All electrical, HVAC, plumbing, and filter supply house data files
- Updated `brandsRep` fields throughout

## Migration Script

The standardization was performed using:
- `scripts/standardize_manufacturer_names.py`

This script:
1. Loads all branch JSON files
2. Applies standardization mapping to `brandsRep` arrays
3. Preserves all other data and formatting
4. Writes updated files with trailing newlines

## Maintenance

To maintain standardization:

1. **When adding new branches**: Use standardized names from the start
2. **When adding new manufacturers**: Check against existing names, avoid compound forms
3. **Reference list**: See `supply-house-directory/_meta/manufacturers.json` for current standards

## Related Files

- Migration script: `scripts/standardize_manufacturer_names.py`
- Meta files: `supply-house-directory/_meta/manufacturers.json`, `supply-house-directory/_meta/brands.json`
- All branch data files in `supply-house-directory/us/co/`

---

**Date**: 2025-12-31  
**Version**: 1.3  
**Author**: Automated standardization based on Price-Cal repository insights

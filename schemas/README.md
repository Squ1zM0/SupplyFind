# Supply House Data Schemas

This directory contains JSON Schema definitions for the canonical supply house dataset format.

## Overview

The supply house dataset has been standardized to use a single cohesive format across all branch-bearing JSON files. This ensures consistent parsing, validation, and tooling across the entire dataset.

## Schema Files

### branch-record.schema.json

Defines the structure for individual branch records. Every branch must have:

**Required Fields:**
- `id` - Stable unique identifier
- `name` - Branch name
- `address` - Structured address object (line1, city, state, postalCode)
- `contact` - Contact information (phone, website, hours)
- `geo` - Geographic coordinates and metadata
- `brands` - Brand representation info (brandsRep, manufacturersPartsFor)
- `trades` - Array of trade categories served

**Optional Fields:**
- `chain` - Parent company/chain name
- `primaryTrade` - Primary trade focus
- `tags` - Additional categorization tags
- `notes` - General notes about the branch
- `sources` - Source URLs for verification
- `verification` - Verification metadata

### branch-dataset.schema.json

Defines the structure for files containing branch records (the canonical wrapper format).

**Required Fields:**
- `version` - Dataset version identifier
- `updated` - Last update date (YYYY-MM-DD)
- `country` - Country code (e.g., "US")
- `state` - State/province code (e.g., "CO")
- `area` - Area description (kind, id, name)
  - `kind`: "metro" | "region" | "statewide" | "custom"
  - `id`: Stable slug identifier (e.g., "denver-metro")
  - `name`: Human-readable name (e.g., "Denver Metro")
- `scope` - Dataset scope
  - `trade`: "hvac" | "plumbing" | "electrical" | "filter" | "multi"
- `branches` - Array of branch records

**Optional Fields:**
- `audit` - Audit and verification metadata
  - `status`: Current audit status
  - `notes`: Array of audit notes
  - `verificationMode`: Verification methodology

### index-dataset.schema.json

Defines the structure for index/routing files that reference other datasets.

**Required Fields:**
- `type` - Must be "index"
- `state` - State/province code
- `updated` - Last update date (YYYY-MM-DD)
- `scope` - Index scope
  - `trade`: Trade category
- `entries` - Array of dataset references
  - `id`: Area identifier
  - `name`: Area name
  - `file`: Relative path to dataset file

## Migration

All existing supply house data files have been migrated to the canonical format using:

```bash
python3 scripts/normalize_supply_house_data.py
```

This migration:
- ✅ Converts bare arrays to canonical wrapper objects
- ✅ Normalizes all branch record field names
- ✅ Preserves all existing data (no data loss)
- ✅ Maintains audit notes and verification metadata

## Validation

Schema compliance is validated using:

```bash
python3 scripts/validate_supply_house_schema.py
```

This validation:
- ✅ Checks all required fields are present
- ✅ Validates field types and structures
- ✅ Ensures consistent data format across all files
- ✅ Runs automatically in CI on every PR

## CI Integration

A GitHub Actions workflow automatically validates schema compliance on:
- All pull requests that modify JSON files
- Pushes to main/master branch

The workflow is defined in `.github/workflows/validate-schemas.yml` and will block merges if validation fails.

## Key Benefits

1. **Single Parser** - All branch datasets use the same structure, enabling simple, consistent parsing
2. **Type Safety** - Clear schema definitions enable strong typing in consuming applications
3. **Validation** - Automated schema validation prevents regressions
4. **Documentation** - Schemas serve as living documentation of the data format
5. **Tooling** - Consistent format enables better tooling, IDE support, and code generation

## Field Migration Reference

### Address Fields
- `address1` → `address.line1`
- `address2` → `address.line2`
- `city` → `address.city`
- `state` → `address.state`
- `postalCode` → `address.postalCode`

### Geographic Fields
- `lat` → `geo.lat`
- `lon` → `geo.lon`
- `arrivalLat` → `geo.arrivalLat`
- `arrivalLon` → `geo.arrivalLon`
- `arrivalType` → `geo.arrivalType`
- `coordsStatus` → `geo.coordsStatus`
- `geoPrecision` → `geo.geoPrecision`
- `geoVerifiedDate` → `geo.geoVerifiedDate`
- `geoSource` → `geo.geoSource`

### Brand Fields
- `brandsRep` → `brands.brandsRep`
- `manufacturersPartsFor` → `brands.manufacturersPartsFor`
- `partsFor` → `brands.manufacturersPartsFor` (legacy mapping)

### Contact Fields
- `phone` → `contact.phone`
- `website` → `contact.website`
- `hours` → `contact.hours`

### Audit Fields
- `auditNotes` → `audit.notes`
- `auditStatus` → `audit.status`
- `verificationMode` → `audit.verificationMode`

### Area/Metro Fields
- `metro` → `area.name`
- `region` → `area.name`
- File-based inference → `area.id`, `area.kind`

## Examples

### Example Branch Dataset

```json
{
  "version": "1.0.0",
  "updated": "2025-12-30",
  "country": "US",
  "state": "CO",
  "area": {
    "kind": "metro",
    "id": "denver-metro",
    "name": "Denver Metro"
  },
  "scope": {
    "trade": "hvac"
  },
  "audit": {
    "status": "complete",
    "notes": ["Verified all locations 2025-12-30"],
    "verificationMode": "strict_storefront_only"
  },
  "branches": [...]
}
```

### Example Index File

```json
{
  "type": "index",
  "state": "CO",
  "updated": "2025-12-30",
  "scope": {
    "trade": "electrical"
  },
  "entries": [
    {
      "id": "denver-metro",
      "name": "Denver Metro",
      "file": "us/co/electrical/denver-metro.json"
    }
  ]
}
```

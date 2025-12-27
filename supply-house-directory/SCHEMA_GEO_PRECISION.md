# Geolocation Precision Metadata Schema

## Overview

This document describes the optional geolocation precision metadata fields added to the supply house branch schema to improve routing accuracy and prevent coordinate precision degradation over time.

## Problem Statement

While recent address audits ensured all supply houses have verified coordinates, there was no standardized way to:
1. Track the **type** of precision achieved (entrance vs. storefront vs. warehouse vs. centroid)
2. Record **when** coordinates were verified
3. Document the **source** used for coordinate verification

Without this metadata, future updates could inadvertently degrade precision by:
- Overwriting precise coordinates with auto-geocoded approximations
- Losing track of which locations have been manually verified
- Reverting to parcel centroids or business park centers

## Solution

We've added three optional fields to all supply house branches to track geolocation precision:

### Schema Definition

```json
{
  "geoPrecision": "storefront" | "entrance" | "warehouse" | "centroid",
  "geoVerifiedDate": "YYYY-MM-DD",
  "geoSource": "Google Maps pin" | "gps-coordinates.org" | "..."
}
```

### Field Descriptions

#### `geoPrecision`

Indicates the type of location precision achieved for the coordinates.

**Type:** String (enum)

**Valid Values:**
- `"storefront"` - Coordinates point to the main customer entrance or storefront
- `"entrance"` - Coordinates point to a building entrance (when specific type unclear)
- `"warehouse"` - Coordinates point to warehouse or loading dock entrance
- `"centroid"` - Coordinates represent a parcel or building centroid (avoid for new entries)

**Usage Guidelines:**
- Use `"storefront"` for retail-facing locations with will-call counters
- Use `"warehouse"` when the primary access is via loading dock
- Use `"entrance"` when the specific entrance type is unclear but precision is verified
- Avoid `"centroid"` for new entries; it indicates coordinates need refinement

**Example:**
```json
{
  "name": "Ferguson Plumbing Supply (Denver)",
  "lat": 39.7274,
  "lon": -105.0206,
  "geoPrecision": "storefront",
  "geoVerifiedDate": "2025-12-27",
  "geoSource": "Google Maps pin"
}
```

#### `geoVerifiedDate`

The date when the coordinates were last verified, in ISO 8601 format (YYYY-MM-DD).

**Type:** String (ISO date)

**Format:** `"YYYY-MM-DD"`

**Purpose:**
- Enables tracking of coordinate staleness
- Supports scheduled re-verification campaigns
- Helps prioritize locations for precision audits

**Example:**
```json
{
  "geoVerifiedDate": "2025-12-27"
}
```

#### `geoSource`

The primary source or method used to verify the coordinates.

**Type:** String

**Common Values:**
- `"Google Maps pin"` - Coordinates from Google Maps pin placement
- `"Google Maps"` - Verified using Google Maps (general)
- `"gps-coordinates.org"` - Verified using gps-coordinates.org tool
- `"latlong.net"` - Verified using latlong.net tool
- `"Apple Maps"` - Verified using Apple Maps
- `"Official company website"` - Coordinates from official location finder
- Custom source descriptions

**Usage Guidelines:**
- Always cite the primary verification source
- Prefer specific tool names over generic descriptions
- Include method when coordinates are manually derived

**Example:**
```json
{
  "geoSource": "Google Maps pin"
}
```

## Complete Example

```json
{
  "id": "co-denver-sidharvey-w6th-001",
  "name": "Sid Harvey - Denver",
  "chain": "Sid Harvey",
  "trade": "hvac",
  "address1": "2700 W. 6th Ave",
  "city": "Denver",
  "state": "CO",
  "postalCode": "80204",
  "phone": "(303) 623-1236",
  "lat": 39.72672,
  "lon": -105.01886,
  "coordsStatus": "verified",
  "geoPrecision": "storefront",
  "geoVerifiedDate": "2025-12-27",
  "geoSource": "Google Maps pin",
  "verification": {
    "addressVerified": true,
    "addressSource": "Google Business Profile & Multiple Verified Directories",
    "addressVerifiedDate": "2025-12-27",
    "storefront_confirmed": "2025-12-27",
    "coords_verified": "2025-12-27",
    "geocoding_method": "Google Maps verified coordinates"
  }
}
```

## Relationship to Existing Fields

The new geo precision fields complement but don't replace existing verification metadata:

| Field | Purpose | Location |
|-------|---------|----------|
| `coordsStatus` | Overall coordinate verification status | Root level |
| `verification.coords_verified` | Date of coordinate verification | Inside verification object |
| `verification.geocoding_method` | Detailed verification methodology | Inside verification object |
| **`geoPrecision`** | **Type of precision achieved** | **Root level (NEW)** |
| **`geoVerifiedDate`** | **Simplified verification date** | **Root level (NEW)** |
| **`geoSource`** | **Primary verification source** | **Root level (NEW)** |

The new fields provide quick, top-level access to critical precision information without requiring parsing of the nested `verification` object.

## Implementation Statistics

**Date Implemented:** 2025-12-27

### Coverage
- **Total Branches:** 225
- **With Geo Precision Metadata:** 225 (100%)
- **Files Modified:** 30

### Distribution by Precision Type
- **Storefront:** 158 branches (70.2%)
- **Entrance:** 67 branches (29.8%)
- **Warehouse:** 0 branches (0%)
- **Centroid:** 0 branches (0%)

### Distribution by Source
- **Google Maps pin:** 82 branches (36.4%)
- **gps-coordinates.org:** 82 branches (36.4%)
- **Previously verified during geocoding audit:** 41 branches (18.2%)
- **Other verified sources:** 20 branches (8.9%)

## Regression Guard Recommendations

To maintain coordinate precision over time:

### 1. Preservation During Updates
- **NEVER** overwrite fields with auto-geocoded values
- Always check `geoPrecision` before updating coordinates
- Prefer manually verified coordinates over automated results

### 2. Validation Rules
```javascript
// Example validation
if (branch.geoPrecision === "storefront" || branch.geoPrecision === "entrance") {
  // These are high-precision coordinates - don't overwrite
  console.warn("Skipping coordinate update - manually verified precision");
  return;
}
```

### 3. Audit Schedule
- Review `geoVerifiedDate` quarterly
- Flag branches with verification dates older than 2 years
- Prioritize high-traffic metro locations for re-verification

### 4. Future Ingestion
When adding new branches:
1. Always set `geoPrecision` during initial data entry
2. Document `geoSource` at time of verification
3. Set `geoVerifiedDate` to current date
4. Never use automated geocoding as final source for production data

## Benefits

### For Data Consumers
- **Quick precision assessment:** Check `geoPrecision` before using coordinates for routing
- **Confidence indicators:** Know which locations have verified storefront coordinates
- **Audit trail:** Track when coordinates were last verified

### For Data Maintainers
- **Regression prevention:** Avoid overwriting precise coordinates
- **Quality tracking:** Monitor distribution of precision types
- **Targeted updates:** Identify locations needing re-verification

### For End Users (Contractors)
- **Accurate routing:** Directions lead to correct entrance, not parking lot
- **Time savings:** No searching for correct building in complex
- **Better UX:** Reliable arrival points for truck-accessible locations

## Future Enhancements

Potential additions to the schema:

1. **Precision Confidence Score**
   ```json
   "geoConfidence": 0.95  // 0-1 scale
   ```

2. **Access Type Metadata**
   ```json
   "accessType": "truck-accessible" | "car-only" | "walk-up"
   ```

3. **Multi-entrance Support**
   ```json
   "entrances": {
     "will-call": { "lat": 39.7274, "lon": -105.0206 },
     "loading-dock": { "lat": 39.7275, "lon": -105.0207 }
   }
   ```

## Validation Script

A validation script is available at `scripts/add_geo_precision_metadata.py` to:
- Add metadata to branches missing these fields
- Derive values from existing verification data
- Validate JSON integrity after updates

**Usage:**
```bash
python3 scripts/add_geo_precision_metadata.py
```

## References

- **Original Issue:** GitHub Issue - "📍 Refine Latitude / Longitude Precision for Supply House Directions"
- **Address Audit Report:** `ADDRESS_GEOLOCATION_AUDIT_2025-12-27.md`
- **Implementation Script:** `scripts/add_geo_precision_metadata.py`

---

**Last Updated:** 2025-12-27  
**Status:** Implemented - 100% coverage achieved  
**Validation:** ✅ Passed (225/225 branches)

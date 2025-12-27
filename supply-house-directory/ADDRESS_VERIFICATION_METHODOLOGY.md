# Address Verification Methodology

## Overview

This document defines the authoritative process for verifying and maintaining accurate physical addresses and geolocation data for supply house branches in the SupplyFind repository.

**Date Established:** 2025-12-27  
**Status:** Required for all branch additions and updates

---

## Problem Statement

Supply houses frequently relocate, yet legacy addresses persist in:
- Manufacturer line cards
- Distributor directories
- Trade association listings
- Cached business data

**Impact:**
- ❌ Incorrect directions to former/wrong locations
- ❌ Broken "near me" proximity results
- ❌ Inaccurate distance calculations
- ❌ Reduced contractor trust in SupplyFind

**Root Cause:**
- Previous verification relied on non-authoritative sources
- Addresses verified from manufacturer line cards may lag 1-5+ years behind relocations
- No systematic re-verification process

---

## Authoritative Source Hierarchy

When verifying or updating branch addresses, sources **MUST** be consulted in this priority order:

### 1. **Google Business Profile** (Highest Priority)
- Most current, publicly verifiable address
- Updated by business owners
- Reflects actual operating location
- Directly impacts Google Maps routing

**How to verify:**
1. Search "Company Name + City + State" in Google
2. Check the Google Business listing (Knowledge Panel)
3. Note the complete address including suite/building numbers
4. Verify hours and phone number
5. Screenshot or save URL as proof

**Example:**
```
RSD Centennial
Google Search: "RSD Centennial Colorado"
Result: 7184 S Revere Pkwy, Building 2, Centennial, CO 80112
```

### 2. **Official Company Store Locator** (Secondary)
- Company's own location directory
- Usually current and authoritative
- May include store numbers and branch details

**How to verify:**
1. Visit company website
2. Navigate to "Locations" or "Store Locator"
3. Search for specific branch
4. Verify full address matches Google Business Profile
5. Save URL to specific branch page

**Examples:**
- Ferguson: https://www.ferguson.com/store/
- RSD: https://www.rsd.net/locations/
- Graybar: https://www.graybar.com/locations

### 3. **Direct Contact** (If Discrepancy Exists)
- Call the branch directly using published phone number
- Verify current physical address
- Ask for suite/building number if applicable
- Document date and person contacted

---

## Non-Authoritative Sources (DO NOT USE ALONE)

The following sources are **NOT sufficient** for address verification:

❌ **Manufacturer Line Cards**
- May be 1-5+ years outdated
- Not updated when distributors relocate
- Primary purpose is brand representation, not location accuracy

❌ **Trade Directories**
- Often scraped from outdated sources
- Not maintained by the businesses themselves
- May contain aggregated/stale data

❌ **Third-Party Business Listings** (Alone)
- Yelp, Yellow Pages, BBB, Chamber of Commerce
- May be user-submitted or auto-generated
- Acceptable only to corroborate Google/Official sources

❌ **Mailing Addresses**
- P.O. Boxes are never physical locations
- Corporate headquarters ≠ branch location
- Suite numbers may differ from will-call entrance

---

## Required Verification Metadata

Every branch **MUST** include the following verification fields:

```json
{
  "verification": {
    "addressVerified": true,
    "addressSource": "Google Business Profile & Official RSD Store Locator",
    "addressVerifiedDate": "2025-12-27",
    "storefront_confirmed": "2025-12-27",
    "sources": [
      "https://www.rsd.net/store/0074-centennial-co",
      "https://www.google.com/maps/place/RSD+Centennial"
    ],
    "coords_verified": "2025-12-27",
    "geocoding_method": "Google Maps pin + verified geocoding services"
  }
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `addressVerified` | boolean | ✅ Yes | Set to `true` when address verified via authoritative sources |
| `addressSource` | string | ✅ Yes | Primary source(s) used for verification (e.g., "Google Business Profile & Official Store Locator") |
| `addressVerifiedDate` | string | ✅ Yes | Date of verification in YYYY-MM-DD format |
| `storefront_confirmed` | string | ✅ Yes | Date when physical address was confirmed (YYYY-MM-DD) |
| `sources` | array | ✅ Yes | URLs to authoritative sources |
| `coords_verified` | string | ✅ Yes | Date when coordinates were verified (YYYY-MM-DD) |
| `geocoding_method` | string | ✅ Yes | Method used to obtain coordinates (e.g., "Google Maps pin + verified geocoding services") |

---

## Geolocation Precision Requirements

### Coordinate Accuracy Standards

Coordinates **MUST** meet these precision standards:

- **Decimal Places:** Minimum 4 decimal places (±11m accuracy)
- **Precision Level:** Storefront/building entrance level
- **Not Acceptable:** City centroids, ZIP code centroids, street centroids

### Coordinate Verification Process

1. **Use Google Maps:**
   - Search for verified address
   - Drop pin on exact building location
   - Right-click pin → "What's here?"
   - Copy latitude, longitude (shown at bottom)

2. **Cross-Verify with Geocoding Service:**
   - Use https://www.gps-coordinates.org/ or https://www.latlong.net/
   - Enter verified street address
   - Compare results to Google Maps pin
   - Use Google Maps coordinates if discrepancy exists

3. **Validate Routing:**
   - Click "Directions" from Google Maps
   - Verify route goes to correct building entrance
   - Check street view if available

### Example Coordinate Verification

```
Address: 7184 S Revere Pkwy, Building 2, Centennial, CO 80112
Google Maps Pin: 39.5869, -104.8276
GPS-Coordinates.org: 39.5869, -104.8276
✅ Match - coordinates verified
```

---

## Step-by-Step Verification Workflow

### For New Branches

1. **Find Google Business Profile**
   - Search "Company Name + Branch City + State"
   - Confirm business name matches
   - Copy full address including suite/building

2. **Verify with Official Store Locator**
   - Visit company's location page
   - Find specific branch
   - Confirm address matches Google
   - Save URL to branch page

3. **If Discrepancy Exists:**
   - Prefer Google Business Profile (more likely current)
   - Call branch to confirm
   - Document which source was incorrect

4. **Obtain Precise Coordinates**
   - Use Google Maps pin on verified address
   - Cross-check with geocoding service
   - Verify routing/directions

5. **Add Verification Metadata**
   - Include all required fields
   - List authoritative sources
   - Use current date for verification

### For Address Updates/Relocations

1. **Confirm Relocation**
   - Check if Google Business shows new address
   - Verify with store locator
   - Look for "permanently closed" / new location notices

2. **Document Old Address**
   - Add comment noting relocation
   - Include relocation date if known
   - Example: `"Relocated from 6825 S Galena St on 2025-XX-XX"`

3. **Update All Fields**
   - New address (address1, city, postalCode)
   - New coordinates (lat, lon)
   - New/verified phone number
   - Updated verification metadata

4. **Test Directions**
   - Verify Google Maps routes to new location
   - Check that old address no longer shows business

---

## Schema Requirements

### Complete Address Fields

Every branch must include:

```json
{
  "address1": "7184 S Revere Pkwy, Building 2",
  "address2": "",
  "city": "Centennial",
  "state": "CO",
  "postalCode": "80112",
  "phone": "(303) 792-2354",
  "lat": 39.5869,
  "lon": -104.8276
}
```

**Field Requirements:**
- `address1`: Street address with suite/building if applicable (required)
- `address2`: Additional address line if needed (optional, use empty string if not needed)
- `city`: City name (required)
- `state`: Two-letter state code (required)
- `postalCode`: 5-digit ZIP code (required) - **NOTE:** Use "postalCode" not "zip"
- `phone`: Phone number in (XXX) XXX-XXXX format (required)
- `lat`: Latitude with 4-6 decimal places (required)
- `lon`: Longitude with 4-6 decimal places (required)

---

## Maintenance & Re-Verification

### Quarterly Audit Schedule

- **Q1 (January-March):** Verify 25% of branches
- **Q2 (April-June):** Verify 25% of branches
- **Q3 (July-September):** Verify 25% of branches
- **Q4 (October-December):** Verify 25% of branches

### Triggers for Immediate Re-Verification

Re-verify a branch immediately if:
- User reports incorrect address/location
- Google Business shows "permanently closed"
- Store locator shows address change
- Branch appears in multiple files with different addresses
- Verification is >2 years old

### Verification Priority

High-priority branches for verification:
1. **Major chains** (Ferguson, Rexel, Graybar, etc.) - 100+ locations nationally
2. **High-traffic metros** (Denver, Colorado Springs, Fort Collins)
3. **Branches with >1 year old verification**
4. **Branches with non-authoritative sources**

---

## Examples

### ✅ Correct Verification

```json
{
  "id": "co-centennial-rsd-001",
  "name": "RSD – Centennial",
  "chain": "RSD",
  "address1": "7184 S Revere Pkwy, Building 2",
  "city": "Centennial",
  "state": "CO",
  "postalCode": "80112",
  "phone": "(303) 792-2354",
  "lat": 39.5869,
  "lon": -104.8276,
  "notes": "RSD Store #74. HVAC/R wholesaler. Address verified via Google Business Profile and official RSD store locator (Store #74), 2025-12-27.",
  "sources": [
    "https://www.rsd.net/store/0074-centennial-co",
    "https://www.google.com/maps/place/RSD+Centennial"
  ],
  "verification": {
    "addressVerified": true,
    "addressSource": "Google Business Profile & Official RSD Store Locator",
    "addressVerifiedDate": "2025-12-27",
    "storefront_confirmed": "2025-12-27",
    "sources": [
      "https://www.rsd.net/store/0074-centennial-co",
      "https://www.google.com/maps/place/RSD+Centennial"
    ],
    "coords_verified": "2025-12-27",
    "geocoding_method": "Google Maps pin + verified geocoding services"
  }
}
```

### ❌ Incorrect Verification (Non-Authoritative Source)

```json
{
  "id": "co-example-branch-001",
  "address1": "123 Main St",
  "city": "Denver",
  "notes": "Source: Manufacturer line card, verified 2020-01-15",
  "sources": [
    "https://manufacturer.com/line-card.pdf"
  ],
  "verification": {
    "coords_verified": "2020-01-15",
    "geocoding_method": "Approximate from ZIP code"
  }
}
```

**Problems:**
- No addressVerified field
- Uses manufacturer line card (non-authoritative)
- Verification date is 5 years old
- No Google Business Profile check
- Coordinates from ZIP code (too imprecise)
- Missing addressSource field

---

## Regression Prevention

### For Data Contributors

Before committing new branches or updates:

1. ✅ Verify address with Google Business Profile
2. ✅ Cross-check with official store locator
3. ✅ Include all required verification metadata
4. ✅ Use precise coordinates from Google Maps
5. ✅ Test directions in Google Maps
6. ✅ Document authoritative sources

### For Code Reviewers

Check that every branch:

1. ✅ Has `addressVerified: true` in verification object
2. ✅ Lists authoritative source (Google/Official Site)
3. ✅ Has verification date within 2 years
4. ✅ Has precise coordinates (4+ decimal places)
5. ✅ Has complete address (address1, city, state, postalCode)
6. ✅ Has working source URLs

---

## Tools & Resources

### Verification Tools
- **Google Business Search:** https://www.google.com/maps
- **GPS Coordinates:** https://www.gps-coordinates.org/
- **Lat/Long Finder:** https://www.latlong.net/

### Common Store Locators
- Ferguson: https://www.ferguson.com/store/
- RSD: https://www.rsd.net/locations/
- Rexel: https://www.rexelusa.com/locations
- Border States: https://www.borderstates.com/locations
- Graybar: https://www.graybar.com/locations
- WESCO: https://www.wesco.com/locations
- Johnstone Supply: https://www.johnstonesupply.com/locations

### Validation Script
Run the verification analysis script to identify branches needing review:
```bash
python3 scripts/analyze_address_verification.py
```

---

## Acceptance Criteria

An address is considered **verified and production-ready** when:

✅ Address obtained from Google Business Profile OR official store locator  
✅ Coordinates verified via Google Maps pin (4+ decimal places)  
✅ "Directions" routes to correct storefront  
✅ All verification metadata fields populated  
✅ Verification date is current (within 2 years)  
✅ Sources documented with URLs  
✅ Phone number verified  

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-27 | 1.0 | Initial methodology document created |

---

**Maintained by:** SupplyFind Data Team  
**Questions:** File issue with "address-verification" label

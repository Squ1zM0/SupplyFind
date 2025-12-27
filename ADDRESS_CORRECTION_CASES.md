# Address Correction Case Studies

This document tracks high-impact address corrections that were discovered after initial verification, serving as regression guards and audit trail for address quality issues.

---

## Case #1: Superior Filtration Products - Multi-Address Conflict

**Date Discovered**: 2025-12-27  
**Severity**: HIGH - Navigation Failure  
**Branch**: Superior Filtration Products, Denver, CO

### Problem Statement

The dataset entry for Superior Filtration Products was producing a directions/address mismatch when opened in Google Maps. The app entry showed one address, but Google Maps was surfacing a different business listing, causing navigation to the wrong destination.

**Dataset Entry (Incorrect)**:
- Address: 2650 W 3rd Ave, Unit 3, Denver, CO 80219
- Coordinates: 39.72073, -105.01978

**Google Maps Listing (Correct)**:
- Address: 209 Yuma St, Unit 3, Denver, CO 80219
- Coordinates: 39.7129, -105.0111

### Root Cause Analysis

**Suspected Causes**:
1. ✅ **Business Relocation** - Business moved and dataset reflected old/outdated address
2. ✅ **Multi-tenant Industrial Complex** - Unit-level accuracy matters; maps listing may reflect different unit or entrance
3. **Address String Resolution** - Dataset uses address-based directions, string resolving incorrectly in Google

**Confirmed Cause**: The business has multiple addresses in public records. 2650 W 3rd Ave Unit 3 appears in some older directories and MapQuest listings, but the official website and Google Business Profile both use 209 Yuma St, Unit 3 as the primary customer-accessible location.

### Verification Process

**Required Sources (Minimum 2)**:
1. ✅ Official Website: https://www.superiorfiltrationproducts.com/contact
   - Lists "209 Yuma Street, Denver, CO 80219"
   
2. ✅ Google Business Profile / Maps:
   - Confirms "209 Yuma St, Unit 3, Denver, CO 80219"
   
3. ✅ Business Directories:
   - Chamber of Commerce confirms 209 Yuma St
   - MapQuest also has entries for both addresses (older data)

**Validation Methods**:
- Cross-referenced official website contact page (blocked but verified via web search)
- Verified Google Business Profile listing
- Checked multiple business directories
- Confirmed via web search that official address is 209 Yuma St

### Resolution Applied

**Dataset Updates**:
```json
{
  "id": "superior-filtration-denver-yuma",  // Changed from superior-filtration-denver-3rd-ave
  "address1": "209 Yuma St, Unit 3",       // Changed from 2650 W 3rd Ave, Unit 3
  "lat": 39.7129,                           // Changed from 39.72073
  "lon": -105.0111,                         // Changed from -105.01978
  "arrivalLat": 39.7129,                    // Updated to match
  "arrivalLon": -105.0111,                  // Updated to match
  "geoPrecision": "entrance",               // Changed from "storefront" for multi-tenant clarity
  "geoVerifiedDate": "2025-12-27",         // Updated
  "verification": {
    "storefront_confirmed": "2025-12-27",
    "sources": [
      "https://www.superiorfiltrationproducts.com/contact",
      "https://maps.google.com/",
      "https://www.chamberofcommerce.com/..."
    ],
    "addressSource": "Official Website + Google Business Profile",
    "addressVerifiedDate": "2025-12-27",
    "previousAddress": "2650 W 3rd Ave, Unit 3 (incorrect - found during address audit)",
    "correctionReason": "Directions/address mismatch - Google Maps was showing different location..."
  }
}
```

**Metadata Additions**:
- `previousAddress` field added for audit trail
- `correctionReason` field documents why the change was needed
- Updated verification sources to include Google Maps and Chamber of Commerce
- Changed `geoPrecision` from "storefront" to "entrance" for multi-tenant building clarity

### Lessons Learned & Prevention

**Common Failure Pattern Identified**:
- ⚠️ Businesses with conflicting Google listing vs unit-level dataset address
- ⚠️ Multi-tenant industrial complexes where unit numbers matter
- ⚠️ Legacy addresses in some directories while official sources have updated location

**Regression Guard Rules**:
1. **Do NOT assume unit-level addresses are correct without proof**
   - Always verify unit numbers with official website or photos
   - Multi-tenant buildings require extra validation
   
2. **Prioritize Official Sources**
   - Company website contact page > MapQuest/directories
   - Google Business Profile > generic listings
   - Recent verification dates > older data
   
3. **Cross-Reference Multiple Sources**
   - Minimum 2 authoritative sources required
   - If sources conflict, prioritize official website + Google Business Profile
   - Document conflicting addresses for audit trail
   
4. **Test Navigation Behavior**
   - Verify Google Maps search resolves to correct location
   - Test both address string and coordinates
   - Ensure "Directions" opens to physical customer entrance

### Impact Assessment

**Trust Issue**: Even one wrong location undermines confidence in the entire directory.

**Before Fix**:
- ❌ Directions to incorrect location
- ❌ User drives to wrong address
- ❌ Trust in dataset compromised

**After Fix**:
- ✅ Directions to correct physical location
- ✅ Google Maps resolves to verified business listing
- ✅ Unit-level precision for multi-tenant building
- ✅ Complete audit trail with previous address documented

### File Modified
- `supply-house-directory/us/co/filter/denver-metro.json`

### Related Issues
- Original Issue: "🐛 Fix Incorrect Address / Directions Mismatch — Superior Filtration Products (Denver, CO)"
- Pattern Type: Multi-address conflict in industrial complex
- Priority: HIGH (navigation failure)

---

## Audit Process Improvements

Based on this case, the following improvements should be applied to future address audits:

1. **Multi-tenant Building Flag**
   - When `geoPrecision` is "entrance" and notes mention "multi-tenant" or "Unit X"
   - Require extra validation: signage photos, street view, or on-site confirmation
   
2. **Google Maps Verification**
   - Always include Google Business Profile in verification sources
   - Test that address string resolves correctly in Google Maps
   
3. **Previous Address Documentation**
   - When correcting addresses, always document `previousAddress`
   - Include `correctionReason` for audit transparency
   
4. **Conflicting Address Protocol**
   - If multiple addresses found for same business:
     1. Check official website (highest priority)
     2. Check Google Business Profile
     3. Call business to confirm if still unclear
     4. Document all addresses found with notes

---

**Next Case**: TBD

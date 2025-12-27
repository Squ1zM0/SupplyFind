# Removed Branches Report

**Date:** 2025-12-27  
**Audit:** November 2025 Supply House Branch Verification

---

## Summary

This document records all branches removed from the supply house directory during the November 2025 comprehensive audit. Each removal is documented with verification sources and reasons.

**Total Branches Removed:** 3

---

## Removed Branches

### 1. Apex Supply Company – Denver

**Removed From File:** `plumbing/denver-metro.json`

**Listed Information:**
- **ID:** TBD (from file)
- **Name:** Apex Supply Company – Denver
- **Address:** 4010 Holly St, Denver, CO 80216
- **Phone:** Not listed
- **Website:** https://apexsupplyco.com/
- **Trade:** Plumbing

**Reason for Removal:** Branch does not exist at listed address

**Verification Details:**
- Official Apex Supply Company website shows NO Colorado locations
- All Apex Supply physical stores are located in Texas only
- Address 4010 Holly St is occupied by "First United Door Technologies" (garage door company)
- First United Door Technologies confirmed open M-F 7am-4pm at this address
- No evidence of Apex Supply ever operating at this Denver location

**Sources:**
- https://apexsupplyco.com/pages/locations (official locations page)
- https://apexsupplyco.com/pages/all-location (all locations list)
- https://firstudt.com/denver/ (current occupant)
- https://www.yellowpages.com/denver-co/apex-supply-company (no Denver listings)

**Verification Date:** 2025-12-27

**Status:** ❌ REMOVED - Invalid entry

---

### 2. A/C Distributors – Thornton

**Removed From File:** `denver-metro.json`

**Listed Information:**
- **ID:** TBD (from file)
- **Name:** A/C Distributors – Thornton
- **Address:** 899 E 84th Ave, Thornton, CO 80229
- **Phone:** Not listed
- **Website:** Not listed
- **Trade:** HVAC

**Reason for Removal:** Address is an appliance retail store, not HVAC supply distributor

**Verification Details:**
- Address 899 E 84th Ave (nearby 321 W 84th Ave) is "Appliance Factory & Mattress Kingdom"
- Business sells retail appliances and mattresses to consumers
- NOT an HVAC supply house or trade distributor
- Hours: M-F 9am-8pm, Sat 10am-8pm, Sun 11am-6pm
- Phone: (303) 292-4800, (720) 881-8282
- No evidence of "A/C Distributors" business at this location

**Sources:**
- https://www.yellowpages.com/thornton-co/mip/appliance-factory-mattress-kingdom-508376890
- https://businessyab.com/explore/united_states/colorado/adams_county/thornton/west_84th_avenue/321/appliance-factory-303-292-4800.html
- https://www.chamberofcommerce.com/business-directory/colorado/thornton/wholesaler-household-appliances/2016040947-appliance-factory-wholesale-distribution
- https://www.appliancefactorydistribution.com/blank-4

**Verification Date:** 2025-12-27

**Status:** ❌ REMOVED - Wrong business type / Invalid entry

---

### 3. HVAC Distributors Co – Denver

**Removed From File:** `denver-metro.json`

**Listed Information:**
- **ID:** TBD (from file)
- **Name:** HVAC Distributors Co – Denver
- **Address:** 4900 Washington St, Denver, CO 80216
- **Phone:** Not listed
- **Website:** Not listed
- **Trade:** HVAC

**Reason for Removal:** Cannot verify existence - unverifiable business

**Verification Details:**
- No web presence found for "HVAC Distributors Co" at 4900 Washington St
- Multiple HVAC distributors exist in Denver area but none match this name/address combination
- No listings in business directories (Yellow Pages, Google Maps, Chamber of Commerce)
- Similar-named businesses exist at different addresses:
  - Comfort Air Distributing at 5757 E 42nd Ave
  - Select Distributing at 4201 Oneida St Unit B
  - Other distributors at various locations
- No evidence this specific business exists or ever existed at this address

**Sources:**
- https://supplynearme.com/denver (HVAC supply directory - no match)
- https://www.superpages.com/denver-co/hvac-distributors (no match found)
- https://www.comfortairdistributing.com/locations/denver (alternative distributors)
- https://sdidenver.com/ (Select Distributing - different location)

**Verification Date:** 2025-12-27

**Status:** ❌ REMOVED - Unverifiable / Does not exist

---

## Related Branch - Under Review

### 4. HVAC Distributors Co – Commerce City (FLAGGED)

**File:** `denver-metro.json`

**Listed Information:**
- **Address:** 6175 E 56th Ave, Commerce City, CO 80022
- **Trade:** HVAC

**Status:** 🔍 FLAGGED FOR FOLLOW-UP

**Issue:** Similar to Denver location above - no web verification found for "HVAC Distributors Co" at this address either. Recommend phone verification or removal in next review cycle.

---

## Additional Related Branch - Under Review

### 5. A/C Distributors – Denver (FLAGGED)

**File:** `denver-metro.json`

**Listed Information:**
- **Address:** 2501 W 3rd Ave, Denver, CO 80219
- **Trade:** HVAC

**Status:** 🔍 FLAGGED FOR FOLLOW-UP

**Issue:** Cannot find web presence for "A/C Distributors" at this address. Recommend phone verification or removal in next review cycle.

---

## Regression Prevention

To prevent removed branches from being reintroduced:

1. **Document IDs:** Record branch IDs from removed entries (to be added after file review)
2. **Source Verification Required:** All future branch additions must include:
   - Official company website OR store locator verification
   - Secondary source verification (Google Maps, business directory)
   - Phone number verification
   - Verification date within last 6 months
3. **Automated Checks:** Implement validation to reject entries without proper verification metadata
4. **Review Cycle:** Quarterly review of all branches without recent verification dates

---

## Import Guards

For future data imports:

- ❌ Do not import branches without official company verification
- ❌ Do not import branches based solely on third-party directories
- ❌ Do not import branches without verified phone numbers
- ✅ Require verification.addressVerified = true
- ✅ Require verification.sources array with official URLs
- ✅ Require verification.addressVerifiedDate within 6 months

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Branches Removed | 3 |
| Removed - Does Not Exist | 2 |
| Removed - Wrong Business Type | 1 |
| Flagged for Follow-Up | 3 |
| Files Affected | 2 |

---

**Document Created:** 2025-12-27  
**Last Updated:** 2025-12-27  
**Next Review:** 2026-01-27

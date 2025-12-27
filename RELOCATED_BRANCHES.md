# Relocated Branches Report

**Date:** 2025-12-27  
**Audit:** November 2025 Supply House Branch Verification

---

## Summary

This document records all branches that have relocated to new addresses, discovered during the November 2025 comprehensive audit. Each relocation is documented with old address, new address, and verification sources.

**Total Branches Relocated:** 1

**Total Address Corrections (Wrong Address in Dataset):** 5

---

## Confirmed Relocations

### 1. Flink Supply Company – Denver

**File:** `plumbing/denver-metro.json`

**Branch ID:** TBD (from file)

**Old Address:**
- 5150 Race Ct, Denver, CO 80216

**New Address:**
- 58 S. Galapago St, Denver, CO 80223

**Relocation Details:**
- Flink Supply Company is a family-run plumbing supply business serving Denver since 1958
- Company has relocated from industrial area (Race Ct) to new location on Galapago St
- Business remains fully operational at new location
- Known for hard-to-find plumbing repair parts, copper tubing, PEX, PVC, water heaters, faucets
- Excellent customer service reputation maintained

**Contact Information:**
- **Phone:** (303) 744-7123
- **Website:** https://www.flinksupply.com/
- **Email:** info@flinksupply.com

**Hours at New Location:**
- Open to public
- Standard business hours (weekdays)

**Verification Sources:**
- https://www.flinksupply.com/ (official website showing new address)
- https://local.yahoo.com/info-19619767-flink-supply-denver/ (Yahoo Local listing)
- https://co-denver.cataloxy.us/firms/flinksupply.com.htm (business directory)
- https://www.flinksupply.com/linecard (product line card)

**Verification Date:** 2025-12-27

**Action Required:**
- ✅ Update address1 to "58 S. Galapago St"
- ✅ Update postalCode to "80223"
- ✅ Update lat/lon coordinates to new location
- ✅ Update verification.addressVerifiedDate to "2025-12-27"
- ✅ Add relocation note to branch notes field

**Status:** 🔄 RELOCATION CONFIRMED - Update required

---

## Address Corrections (Wrong Address in Dataset)

These branches exist and are operating, but the dataset contains incorrect addresses. The correct addresses are listed below.

### 2. WinSupply HVAC – Colorado Springs

**File:** `colorado-springs-metro.json`

**Branch ID:** TBD (from file)

**Incorrect Address in Dataset:**
- 2555 S Circle Dr, Colorado Springs, CO 80906

**Correct Address:**
- 3110 N Stone Ave, Suite 180, Colorado Springs, CO 80907

**Issue:** Completely wrong address in dataset. Verified location is on N Stone Ave, not S Circle Dr.

**Verification Sources:**
- https://www.winsupplyinc.com/Location/Colorado-Springs-CO/80907/HVAC-Supplies (official Winsupply locator)
- https://www.manta.com/c/mhqpctk/winsupply-inc (business directory)
- https://supplynearme.com/hvac-supplier-search/winsupply-colorado-springs-co

**Phone:** (719) 578-0722  
**Hours:** M-F 7:30am-5:00pm, Closed weekends

**Verification Date:** 2025-12-27

**Action Required:** CORRECT ADDRESS

---

### 3. Sid Harvey – Fort Collins

**File:** `front-range-north.json`

**Branch ID:** TBD (from file)

**Incorrect Address in Dataset:**
- 4000 S College Ave, Fort Collins, CO 80525

**Correct Address:**
- 300 Lincoln Ct, Fort Collins, CO 80524

**Issue:** Wrong address in dataset. Verified location is on Lincoln Ct, not College Ave.

**Verification Sources:**
- https://www.chamberofcommerce.com/business-directory/colorado/fort-collins/wholesaler/2006110704-sid-harvey-s (Chamber of Commerce)
- https://www.achrnews.com/directories/2937-hvacr-directory/listing/12151-sid-harvey-s-fort-collins-co (ACHR News directory)
- https://supplynearme.com/hvac-supply/sidharveys (Sid Harvey's locator)

**Phone:** (970) 221-1929  
**Hours:** M-F business hours, closed weekends

**Verification Date:** 2025-12-27

**Action Required:** CORRECT ADDRESS

---

### 4. WinSupply HVAC – Greeley

**File:** `front-range-north.json`

**Branch ID:** TBD (from file)

**Incorrect Address in Dataset:**
- 2315 6th Ave, Greeley, CO 80631

**Correct Address:**
- 1979 2nd Ave, Greeley, CO 80631

**Issue:** Wrong street address. Verified Winsupply Greeley is on 2nd Ave, not 6th Ave.

**Verification Sources:**
- https://www.winsupplyinc.com/Location/Greeley-CO/80631/Plumbing-Supplies (official Winsupply)
- https://www.mapquest.com/us/colorado/greeley-winsupply-429191270 (MapQuest)
- https://www.chamberofcommerce.com/business-directory/colorado/greeley/plumbing-supply-store/31292303-greeley-winsupply (Chamber of Commerce)

**Phone:** (970) 356-0404  
**Hours:** M-F 8:00am-4:30pm, Closed weekends

**Verification Date:** 2025-12-27

**Action Required:** CORRECT ADDRESS

---

### 5. HD Supply Facilities Maintenance – Denver

**File:** `plumbing/denver-metro.json`

**Branch ID:** TBD (from file)

**Incorrect Address in Dataset:**
- 5080 Florence St, Denver, CO 80216

**Correct Address:**
- 10000 E 56th Ave, Denver, CO 80238

**Issue:** Completely wrong address. HD Supply Denver facility is on E 56th Ave, not Florence St.

**Verification Sources:**
- https://hdsupplysolutions.com/ (official HD Supply website)
- https://www.mapquest.com/us/colorado/hd-supply-facillities-maintenance-375448621 (MapQuest)
- https://www.manta.com/c/mkl5zv7/hd-supply-facilities-maintenance (Manta directory)
- https://www.dnb.com/business-directory/company-profiles.hd_supply_facilities_maintenance_ltd.010753fc89335ead771b4827d3f6e5b6.html (D&B)

**Phone:** (800) 431-3000  
**Hours:** M-F 8am-5pm, Closed weekends

**Verification Date:** 2025-12-27

**Action Required:** CORRECT ADDRESS

---

### 6. Filter Supply – Grand Junction (SPECIAL CASE)

**File:** `filter/western-slope.json`

**Branch ID:** TBD (from file)

**Address in Dataset:**
- 308 Pitkin Ave, Grand Junction, CO 81501

**Verification Result:**
- Address is CORRECT
- Business EXISTS and is OPEN
- **HOWEVER:** This is an **AUTO PARTS store** selling automotive filters, NOT HVAC/building air filters

**Business Type:** Automotive parts supplier (Baldwin filters for cars/trucks)

**Verification Sources:**
- http://filtersupply.us (official website - auto parts)
- https://www.yellowpages.com/grand-junction-co/mip/filter-supply-466048815
- https://www.schaefferoil.com/filter-supply-grand-junction-grand-junction-co-81501.html (Schaeffer Oil automotive distributor)

**Phone:** (970) 254-9043  
**Hours:** M-F 7:00am-5:00pm, Closed weekends

**Verification Date:** 2025-12-27

**Action Required:**
- ⚠️ **CATEGORY ERROR** - This branch is miscategorized
- **Option A:** REMOVE from filter/HVAC dataset (recommended - not HVAC/building trade)
- **Option B:** Recategorize as automotive supplier (if automotive trade is in scope)

---

## Minor Address Detail Additions

These branches are at the correct location but are missing suite/unit details in the dataset:

### Denver Winair – Denver

**File:** `denver-metro.json`

**Current Address in Dataset:**
- 1550 W Evans Ave, Denver, CO 80223

**Complete Address:**
- 1550 W Evans Ave, **Unit M**, Denver, CO 80223

**Action Required:** Add "Unit M" to address field

**Source:** https://www.winsupplyinc.com/Location/Denver-CO/80223/HVAC-Supplies/contact-us

---

### North Denver Winair – Denver

**File:** `denver-metro.json`

**Current Address in Dataset:**
- 490 E 76th Ave, Denver, CO 80229

**Complete Address:**
- 490 E 76th Ave, **Bldg 6B**, Denver, CO 80229

**Action Required:** Add "Bldg 6B" to address field

**Source:** https://www.winsupplyinc.com/Location/Denver-CO/80229/HVAC-Supplies/contact-us

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Confirmed Relocations** | 1 |
| **Wrong Addresses Requiring Correction** | 4 |
| **Category Errors (Miscategorized)** | 1 |
| **Minor Detail Additions (Unit Numbers)** | 2 |
| **Total Address Updates Required** | 8 |

---

## Update Checklist

- [ ] Update Flink Supply Company to new address (58 S. Galapago St)
- [ ] Correct WinSupply HVAC Colorado Springs address (3110 N Stone Ave Suite 180)
- [ ] Correct Sid Harvey Fort Collins address (300 Lincoln Ct)
- [ ] Correct WinSupply HVAC Greeley address (1979 2nd Ave)
- [ ] Correct HD Supply Denver address (10000 E 56th Ave)
- [ ] Decide on Filter Supply Grand Junction (remove or recategorize)
- [ ] Add "Unit M" to Denver Winair address
- [ ] Add "Bldg 6B" to North Denver Winair address
- [ ] Update all verification dates to 2025-12-27
- [ ] Update coordinates for relocated/corrected addresses

---

**Document Created:** 2025-12-27  
**Last Updated:** 2025-12-27  
**Next Review:** 2026-06-01

# Primary Trade Schema Extension

## Overview

This document describes the `primaryTrade` field extension to the supply house branch schema, implemented to improve trade filtering clarity for multi-division distributors.

## Problem Statement

Multi-division distributors like Ferguson, Rampart Supply, and Winsupply serve multiple trades (e.g., HVAC and Plumbing). When these branches appear in trade-filtered results, users may be confused about whether the branch is primarily focused on HVAC or Plumbing.

For example:
- **Ferguson** operates 23 branches in Colorado, most of which are "Plumbing Supply" locations that also carry some HVAC products
- Users filtering for "HVAC suppliers" would see these primarily-plumbing branches in results
- This creates ambiguity and potential frustration

## Solution

We've added a `primaryTrade` field to multi-trade branches to clearly indicate the primary business focus of each location.

### Schema Definition

```json
{
  "primaryTrade": "HVAC" | "Plumbing" | "Electrical"
}
```

**When to use:**
- **REQUIRED** for branches with multiple trades (`trades` array length > 1)
- **NOT ALLOWED** for single-trade branches
- Value MUST be one of the trades listed in the `trades` array

**Placement:**
- Add immediately after the `trades` array in the branch object

### Example

```json
{
  "id": "co-denver-ferguson-denver-0383",
  "name": "Ferguson - Denver (Plumbing/PVF & HVAC)",
  "chain": "Ferguson",
  "address1": "550 Raritan Way",
  "city": "Denver",
  "state": "CO",
  "trades": [
    "HVAC",
    "Plumbing"
  ],
  "primaryTrade": "Plumbing"
}
```

## Evidence-Based Classification

All `primaryTrade` assignments are based on verifiable evidence:

### Ferguson Branches (23 locations)

**Primary Trade: Plumbing (22 branches)**
- Branch names contain "Plumbing Supply" or "Plumbing/PVF"
- Official Ferguson URLs include `/plumbingpvf-XXXX`
- Showroom locations (Ferguson Home, Aurora Showroom) are plumbing-focused
- Examples:
  - Ferguson Plumbing Supply (Fort Collins) - URL: `/plumbingpvf-0112`
  - Ferguson - Denver - URL: `/plumbingpvf-0383`
  - Ferguson Home (Durango) - Showroom format

**Primary Trade: HVAC (1 branch)**
- Ferguson Plumbing & HVAC Supply - Arvada
- Official URL: `/hvac-1805` (HVAC department code)

### Rampart Supply (4 branches)

**Primary Trade: HVAC**
- Specializes in boilers and hydronic heating systems
- Core business is heating equipment (HVAC category)
- Plumbing supplies are secondary/complementary products

### Gateway Supply (2 branches)

**Primary Trade: Plumbing**
- Identified as "independent plumbing wholesaler" in notes
- Business descriptions emphasize plumbing supply focus
- HVAC offerings are secondary

### Winsupply Network (2 branches)

**Winsupply of Salida**
- Primary Trade: Plumbing
- Part of Winnelson (plumbing) division

**Longmont Winair**
- Primary Trade: HVAC
- Part of Winair (HVAC) division
- Name explicitly includes "Winair"

## Colorado Dataset Summary

| Chain | Total Branches | Primary HVAC | Primary Plumbing |
|-------|----------------|--------------|------------------|
| Ferguson | 23 | 1 | 22 |
| Rampart Supply | 4 | 4 | 0 |
| Gateway Supply | 2 | 0 | 2 |
| Winsupply / Winair | 1 | 1 | 0 |
| Winsupply | 1 | 0 | 1 |
| **TOTAL** | **31** | **6** | **25** |

## Validation

All 31 multi-trade branches in the Colorado dataset now have the `primaryTrade` field:
- ✅ 100% coverage of multi-trade branches
- ✅ All `primaryTrade` values are valid (in the `trades` array)
- ✅ No single-trade branches incorrectly have `primaryTrade`
- ✅ All classifications backed by verifiable evidence

## Usage Guidelines

### For Data Consumers

When implementing trade filters:

1. **Primary Trade Filter:** Use `primaryTrade` for "primary focus" filtering
   ```javascript
   // Show branches primarily focused on HVAC
   branches.filter(b => b.primaryTrade === 'HVAC')
   ```

2. **Any Trade Filter:** Use `trades` array for "serves this trade" filtering
   ```javascript
   // Show all branches that serve HVAC (primary or secondary)
   branches.filter(b => b.trades.includes('HVAC'))
   ```

3. **Combined Filtering:** Offer users both options
   - "HVAC Specialists" (primaryTrade === 'HVAC')
   - "All HVAC Suppliers" (trades includes 'HVAC')

### For Data Maintainers

When adding new multi-trade branches:

1. **Research the primary focus:**
   - Check official branch name (e.g., "Plumbing Supply" vs "HVAC Supply")
   - Review official website URL structure
   - Examine branch type (showroom = typically plumbing)
   - Analyze business description and specialization

2. **Document your evidence:**
   - Add notes explaining the primaryTrade decision
   - Include sources (URLs, official descriptions)
   - Use verification dates

3. **Validate consistency:**
   - Ensure `primaryTrade` is in the `trades` array
   - Verify it matches the branch's core business model

## Migration Notes

- **Version:** Introduced 2025-12-26
- **Backward Compatibility:** Fully backward compatible
  - Consumers not using `primaryTrade` are unaffected
  - Field is optional for single-trade branches (recommended: omit)
- **Files Modified:** 11 files across Colorado dataset
- **Branches Updated:** 31 multi-trade branches

## Future Considerations

- Consider extending to other states as they're audited
- May inform UI/UX design for multi-trade filtering
- Could enable more sophisticated search/recommendation algorithms
- Provides foundation for "primary vs. secondary inventory" metadata

## References

- Problem Statement: GitHub Issue (trade filtering confusion)
- Audit Report: `COLORADO_TRADE_AUDIT_FINAL.md`
- Implementation: PR #[number] - "Improve trade filter clarity with primaryTrade field"

---

**Last Updated:** 2025-12-26  
**Status:** Implemented for Colorado dataset  
**Validation:** ✅ Passed (31/31 multi-trade branches)

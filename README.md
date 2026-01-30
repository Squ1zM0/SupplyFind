# SupplyFind

A comprehensive, verified directory of supply house branches across Colorado, providing contractors and professionals with accurate location data, contact information, and brand availability.

## 🎯 Project Overview

SupplyFind maintains a production-grade dataset of HVAC, Plumbing, and Electrical supply houses with:
- ✅ **100% verified coordinates** for accurate directions
- ✅ **97.7% verified addresses** from authoritative sources
- ✅ **Comprehensive brand information** for major distributors
- ✅ **Separate arrival coordinates** for precise navigation

## 📊 Current Coverage

### Colorado Dataset
- **Total Branches**: 227
- **Trades Covered**: HVAC, Plumbing, Electrical, Filters
- **Major Chains**: Ferguson, CED, Graybar, Rexel, Johnstone Supply, Baker Distributing, and 60+ more
- **Data Quality**: Production-ready with full verification metadata

### Geographic Coverage
- Denver Metro Area
- Colorado Springs
- Fort Collins / Greeley (Front Range North)
- Boulder / Longmont
- Pueblo / South Colorado
- Western Slope (Grand Junction, Durango, Montrose)
- Eastern Plains (Sterling, Fort Morgan)

## 🚀 Quick Start

### Data Structure

Branch data is organized by region and trade:

```
supply-house-directory/
└── us/
    └── co/
        ├── denver-metro.json
        ├── colorado-springs-metro.json
        ├── electrical/
        │   └── denver-metro.json
        ├── plumbing/
        │   └── denver-metro.json
        └── hvac/
            └── denver-metro.json
```

### Branch Schema

Each branch includes:

```json
{
  "id": "unique-branch-id",
  "name": "Ferguson Plumbing Supply - Denver",
  "chain": "Ferguson",
  "trade": "Plumbing",
  "trades": ["Plumbing", "HVAC"],
  "address1": "550 Raritan Way",
  "city": "Denver",
  "state": "CO",
  "postalCode": "80223",
  "lat": 39.7274,
  "lon": -105.0206,
  "arrivalLat": 39.7274,
  "arrivalLon": -105.0206,
  "geoPrecision": "storefront",
  "coordsStatus": "verified",
  "phone": "(303) 744-7374",
  "website": "https://www.ferguson.com",
  "verification": {
    "addressVerified": true,
    "addressSource": "Google Business Profile & Official Store Locator",
    "addressVerifiedDate": "2025-12-27",
    "storefront_confirmed": "2025-12-27",
    "coords_verified": "2025-12-27"
  }
}
```

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

### Quick Links
- **[Documentation Index](./docs/README.md)** - Complete documentation overview
- **[Comprehensive Audit](./docs/audits/2025-12-comprehensive-audit.md)** - Full audit reports
- **[Geocoding & Coordinates](./docs/audits/geocoding-and-coordinates.md)** - Coordinate verification
- **[Directions API Guide](./docs/implementation/directions-api-guide.md)** - How to use coordinates
- **[Security Reviews](./docs/security/security-reviews.md)** - Security analyses

### Documentation Categories
- **Audits** - Data quality verification and audit reports
- **Expansion** - Dataset growth and branch additions
- **Implementation** - Technical guides and feature implementations
- **Security** - Security reviews and CodeQL scans

## 🛠️ Scripts & Tools

### Validation Scripts
- `scripts/validate_geo_precision.py` - Validate coordinate precision metadata
- `scripts/analyze_address_verification.py` - Analyze address verification status

### Data Processing
- `scripts/standardize_manufacturer_names.py` - Standardize manufacturer names
- `scripts/migrate_verification_metadata.py` - Add verification metadata

## 📈 Data Quality Standards

### Verification Requirements
✅ **Authoritative Sources Only**
- Google Business Profile (primary)
- Official company store locators
- Direct company websites

❌ **Not Acceptable**
- Manufacturer line cards
- Third-party directories alone
- Corporate HQ addresses
- Outdated datasets

### Coordinate Standards
- **Precision**: 4-6 decimal places (±0.11m to ±11m accuracy)
- **Source**: Google Maps pin placement or verified geocoding tools
- **Validation**: All coordinates within Colorado bounds (36.5°N to 41.5°N, -109.5°W to -101.5°W)
- **Arrival Points**: Separate coordinates for navigation accuracy

### Schema Compliance
- Consistent field naming (`postalCode`, not `zip`)
- Required verification metadata for all branches
- Canonical trade values: ["HVAC", "Plumbing", "Electrical"]
- ISO 8601 date format (YYYY-MM-DD)

## 🔄 Recent Updates

### December 2025 Audits
- ✅ Comprehensive branch verification (224 branches audited)
- ✅ Geocoding audit (100% coordinate coverage achieved)
- ✅ Address precision audit (all addresses re-verified)
- ✅ Trade classification audit (100% accuracy)
- ✅ Electrical dataset expansion (34% growth)
- ✅ HVAC dataset expansion (12.3% growth)

### Key Improvements
- Removed 3 invalid branches
- Relocated 1 branch to new address
- Corrected 5 wrong addresses
- Added arrival coordinates for navigation accuracy
- Standardized manufacturer names across dataset

## 🤝 Contributing

### Data Quality Guidelines
1. **Always verify from authoritative sources** (Google Business Profile, official store locators)
2. **Include verification metadata** (source, date, method)
3. **Test coordinates** in Google Maps before submission
4. **Document all changes** with clear commit messages
5. **Run validation scripts** before submitting

### Adding New Branches
1. Verify physical existence via two independent sources
2. Obtain precise coordinates using Google Maps pin placement
3. Include all required schema fields
4. Add comprehensive verification metadata
5. Document sources and verification date

### Reporting Issues
- Use GitHub issues for address corrections
- Include verification sources (links to Google Maps, official websites)
- Provide before/after comparison
- Tag with appropriate labels (address-verification, coordinate-accuracy, etc.)

## 📋 Project Status

| Category | Status |
|----------|--------|
| **Data Coverage** | ✅ Complete for Colorado |
| **Address Verification** | ✅ 97.7% verified |
| **Coordinate Accuracy** | ✅ 100% verified |
| **Data Quality** | ✅ Production-grade |
| **Documentation** | ✅ Comprehensive |
| **Security** | ✅ All scans passing |

## 🔐 Security

All data changes undergo security review:
- CodeQL static analysis on all scripts
- Manual review of coordinate changes
- Verification metadata for audit trail
- Git history for complete change tracking

See [Security Reviews](./docs/security/security-reviews.md) for detailed analyses.

## 📞 Support

### Resources
- [Documentation](./docs/README.md) - Complete documentation index
- [GitHub Issues](../../issues) - Report problems or request features
- [Supply House Directory Schema](./supply-house-directory/README.md) - Detailed schema documentation

### Methodology References
- [Address Verification Methodology](./supply-house-directory/ADDRESS_VERIFICATION_METHODOLOGY.md)
- [Schema Documentation (Geo Precision)](./supply-house-directory/SCHEMA_GEO_PRECISION.md)
- [Schema Documentation (Primary Trade)](./supply-house-directory/SCHEMA_PRIMARYTRADE.md)

## 📝 License

This project maintains a public dataset of supply house locations. All data is verified from publicly available sources and documented with authoritative references.

---

**Last Updated**: December 27, 2025  
**Total Branches**: 227  
**Data Quality**: Production-Grade ✅  
**Documentation**: Comprehensive ✅

# SupplyFind

A comprehensive, verified directory of supply house locations for contractors and tradespeople, starting with Colorado. This repository provides high-precision geolocation data and verified addresses for HVAC, plumbing, electrical, and filter supply houses.

## 🎯 Purpose

SupplyFind helps contractors quickly locate nearby supply houses with accurate addresses and navigation coordinates. Unlike traditional directories, we focus on:

- **Precision geolocation**: Coordinates verified to route to actual customer entrances, not road centerlines
- **Verified addresses**: Every address sourced from official company websites or Google Business profiles
- **Trade-specific data**: Organized by trade (HVAC, electrical, plumbing, filter) for quick filtering
- **Rich metadata**: Brands carried, services offered, coverage areas, and contact information

## 📁 Repository Structure

```
supply-house-directory/
├── us/
│   ├── index.json
│   └── co/                          # Colorado (current coverage)
│       ├── index.json
│       ├── STATEWIDE_SUMMARY.json
│       ├── denver-metro.json        # Regional cross-trade files
│       ├── colorado-springs-metro.json
│       ├── boulder-metro.json
│       ├── front-range-north.json
│       ├── pueblo-south.json
│       ├── western-slope.json
│       ├── eastern-plains.json
│       ├── central-mountains.json
│       ├── hvac/                    # Trade-specific directories
│       │   ├── index.json
│       │   ├── denver-metro.json
│       │   └── ...
│       ├── electrical/
│       ├── plumbing/
│       └── filter/
├── _meta/                           # Metadata files
│   ├── brands.json
│   ├── chains.json
│   └── manufacturers.json
└── README.md                        # Project documentation

scripts/                             # Data processing utilities (root level)
audit/                               # Audit reports and changelogs (root level)
```

## 🗺️ Current Coverage

**Colorado**: 227 verified supply house branches across:
- **Electrical**: Major metros and regional areas
- **Plumbing**: Denver, Colorado Springs, and surrounding regions
- **HVAC**: Denver metro and Colorado Springs
- **Filters**: Specialized filter distributors

## 📊 Data Schema

Each branch includes:

### Location Information
- `id`: Unique branch identifier
- `name`: Branch display name
- `chain`: Parent company/chain name
- `trade`: Primary trade category (hvac, electrical, plumbing, filter)
- `address1`, `address2`, `city`, `state`, `postalCode`: Physical address
- `phone`: Contact phone number
- `website`: Branch or chain website

### Geographic Coordinates

Branches use **separate coordinates** for visual display and navigation routing:

#### Display Coordinates (Map Pin)
- `lat`, `lon`: Latitude/longitude for map pin placement
- `geoPrecision`: Precision level ("storefront", "warehouse", "entrance", "centroid")
- `geoSource`: Source of coordinate verification
- `geoVerifiedDate`: Date coordinates were verified (YYYY-MM-DD)

#### Arrival Coordinates (Navigation Destination)
- `arrivalLat`, `arrivalLon`: Optimal navigation routing destination
- `arrivalType`: Type of arrival point ("will_call", "storefront", "warehouse")

**Why separate coordinates?** Map providers may snap navigation destinations to road segments, causing contractors to arrive at wrong locations. Arrival coordinates are placed 5-15 meters inside the property at actual customer entrances.

### Verification Metadata
- `coordsStatus`: "verified" or "needs_verification"
- `verification`: Detailed verification data including address source, verification date, and geocoding method
- `verified`: Overall verification status
- `verifiedDate`: Date of verification

### Product & Service Information
- `partsFor`: Types of parts carried (e.g., HVAC, Refrigeration)
- `brandsRep`: Brands represented
- `services`: Services offered
- `trades`: All trades served
- `tags`: Categorical tags

### Additional Fields
- `coverage`: Geographic coverage area (metro, regional, statewide)
- `notes`: Additional notes and metadata
- `sources`: Data sources and references

## 🔧 Data Quality Standards

1. **Address Verification**: All addresses sourced from:
   - Official company location pages
   - Google Business profiles
   - Branch-specific store locators
   - Never from P.O. boxes, corporate HQ, or legacy datasets

2. **Coordinate Precision**: 
   - 4-6 decimal places (±0.11m to ±11m accuracy)
   - No city/ZIP centroids
   - No reused coordinates from nearby locations
   - All coordinates verified to route to correct physical locations

3. **Verification Status**: Every branch marked with `coordsStatus` and detailed verification metadata

## 🛠️ Scripts

The `scripts/` directory contains Python utilities for data processing and validation:

- `validate_geo_precision.py`: Validate geographic coordinate precision
- `validate_arrival_coordinates.py`: Check arrival coordinate accuracy
- `comprehensive_branch_audit.py`: Full branch data audit
- `add_geo_precision_metadata.py`: Add geolocation metadata
- And more...

## 📝 Documentation

Additional documentation available in root directory:
- `FINAL_SUMMARY.md`: Complete audit summary
- `DIRECTIONS_URL_GUIDE.md`: Guide for directions URLs
- `GEOCODING_AUDIT_REPORT.md`: Geocoding methodology and results
- Various audit and implementation reports

## 🤝 Contributing

Contributions are welcome! When adding or updating supply house data:

1. Follow the detailed schema documented in `supply-house-directory/README.md`
2. Verify all addresses using authoritative sources
3. Test coordinates for accurate navigation
4. Include verification metadata
5. Use consistent formatting (4-6 decimal places for coordinates)

## 📄 License

This project aims to provide freely accessible, accurate supply house location data for the trades industry.

## 🎯 Future Plans

- Expand to additional states
- Add more trades (industrial, safety equipment, specialty supplies)
- Develop API for programmatic access
- Build web interface for easy searching
- Add operating hours and inventory information

---

**Last Updated**: December 2025  
**Current Version**: 1.0.0

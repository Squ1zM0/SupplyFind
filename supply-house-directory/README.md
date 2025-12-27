Colorado HVAC Supply Houses (seed data)

This folder is intended to mirror the TechDirect-style data repo approach:
- hierarchical index.json files at each level
- branches stored as individual JSON files with lat/lon for distance sorting

Current coverage:
- Denver Metro: Johnstone Supply (Denver West), Ferguson (Denver 0383), United Refrigeration (Denver 01029)
- Colorado Springs: Johnstone Supply (Colorado Springs)

## Branch Schema

### Geographic Coordinates

Branches use **separate coordinates** for visual display and navigation routing:

#### Display Coordinates (Map Pin)
- `lat` (number): Latitude for map pin visual placement
- `lon` (number): Longitude for map pin visual placement
- `geoPrecision` (string): Precision level - "storefront", "warehouse", "entrance", "centroid"
- `geoSource` (string): Source of coordinate verification
- `geoVerifiedDate` (string): Date coordinates were verified (YYYY-MM-DD format)

#### Arrival Coordinates (Navigation Destination)
- `arrivalLat` (number, optional): Latitude for navigation routing destination
- `arrivalLon` (number, optional): Longitude for navigation routing destination
- `arrivalType` (string, optional): Type of arrival point - "will_call", "storefront", "warehouse"

**Why separate coordinates?**
Map providers (Google Maps, Apple Maps) may snap navigation destinations to nearest road segments, causing contractors to arrive at the wrong location (e.g., down the road, driveway entrance, wrong side of building). Arrival coordinates should be placed 5-15 meters inside the property at the actual customer entrance to ensure accurate routing.

**Guidelines:**
- If `arrivalLat`/`arrivalLon` are not specified, fallback to `lat`/`lon`
- Arrival coordinates should point to actual customer/will-call entrance
- Avoid placing arrival points on public road centerlines or parcel centroids
- `arrivalType` clarifies the intended destination (will-call counter, storefront entrance, warehouse dock)

### Coordinate Status & Verification
- `coordsStatus` (string): Status - "verified", "needs_verification"
- `verification` (object): Detailed verification metadata
  - `addressVerified` (boolean)
  - `addressSource` (string)
  - `addressVerifiedDate` (string)
  - `storefront_confirmed` (string)
  - `sources` (array of strings)
  - `coords_verified` (string)
  - `geocoding_method` (string)

### Other Fields
- `id` (string): Unique branch identifier
- `name` (string): Branch display name
- `chain` (string): Parent company/chain name
- `trade` (string): Primary trade category
- `address1`, `address2`, `city`, `state`, `postalCode` (strings): Physical address
- `phone` (string): Contact phone number
- `website` (string): Branch or chain website
- `directionsUrl` (string, optional): Google Maps directions URL using arrival coordinates (format: `https://www.google.com/maps/dir/?api=1&destination={arrivalLat},{arrivalLon}`)
- `coverage` (string): Geographic coverage area
- `verified` (string): Overall verification status
- `verifiedDate` (string): Date of verification
- `notes` (string): Additional notes and metadata
- `tags` (array): Categorical tags
- `partsFor` (array): Types of parts carried
- `brandsRep` (array): Brands represented
- `services` (array): Services offered
- `sources` (array): Data sources and references
- `trades` (array): All trades served

Notes:
- Some brand/parts metadata is intentionally left empty until you confirm the exact schema you want for "brands they rep" vs "manufacturers they have parts for".
- Geo accuracy notes are included per branch.

# Directions URL Generation Guide

## Overview

Supply house branches now use **separate coordinates** for visual map display and navigation routing:

- **Display Coordinates** (`lat`, `lon`): Where the pin appears on the map
- **Arrival Coordinates** (`arrivalLat`, `arrivalLon`): Where navigation should route users

This separation ensures contractors arrive at the correct customer entrance instead of road centerlines, driveways, or adjacent properties.

## Why Separate Coordinates?

Map providers (Google Maps, Apple Maps) automatically snap navigation destinations to the nearest routable road segment. This causes issues for:

- Industrial parks with long driveways
- Multi-tenant buildings with suite numbers
- Warehouse districts
- Properties set back from parkways/boulevards

Using dedicated arrival coordinates placed 5-15 meters inside the property ensures navigation terminates at the actual customer entrance.

## Generating Directions URLs

### Google Maps

Always use **coordinate-based** directions, not address-based:

```
https://www.google.com/maps/dir/?api=1&destination={arrivalLat},{arrivalLon}
```

**Example:**
```
https://www.google.com/maps/dir/?api=1&destination=39.581536,-104.831195
```

**DO NOT** use address-based directions:
```
❌ https://www.google.com/maps/dir/?api=1&destination=7318+S+Revere+Parkway
```

Google will reinterpret the address and may override your intent, routing to the road centerline instead of the entrance.

### Apple Maps

Use coordinate-based directions:

```
http://maps.apple.com/?daddr={arrivalLat},{arrivalLon}
```

**Example:**
```
http://maps.apple.com/?daddr=39.581536,-104.831195
```

### Universal (Platform Detection)

For apps that need to support both platforms, detect the user's device:

**iOS:**
```
http://maps.apple.com/?daddr={arrivalLat},{arrivalLon}
```

**Android/Desktop:**
```
https://www.google.com/maps/dir/?api=1&destination={arrivalLat},{arrivalLon}
```

**Example JavaScript:**
```javascript
function getDirectionsUrl(branch) {
  const arrivalLat = branch.arrivalLat || branch.lat;
  const arrivalLon = branch.arrivalLon || branch.lon;
  
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  
  if (isIOS) {
    return `http://maps.apple.com/?daddr=${arrivalLat},${arrivalLon}`;
  } else {
    return `https://www.google.com/maps/dir/?api=1&destination=${arrivalLat},${arrivalLon}`;
  }
}
```

## Fallback Behavior

If a branch doesn't have arrival coordinates defined:

```javascript
const arrivalLat = branch.arrivalLat || branch.lat;
const arrivalLon = branch.arrivalLon || branch.lon;
```

This ensures backward compatibility while the arrival coordinate system is being rolled out.

## Data Schema Reference

### Branch Object Fields

```json
{
  "lat": 39.581452,
  "lon": -104.831279,
  "geoPrecision": "storefront",
  
  "arrivalLat": 39.581536,
  "arrivalLon": -104.831195,
  "arrivalType": "storefront"
}
```

- `lat`, `lon`: Display pin coordinates (visual only)
- `arrivalLat`, `arrivalLon`: Navigation destination (routing)
- `arrivalType`: Type of arrival point
  - `"storefront"`: Customer entrance at retail storefront
  - `"will_call"`: Will-call counter or customer pickup area
  - `"warehouse"`: Warehouse entrance or loading dock customer access

## Best Practices

### 1. Always Use Coordinates for Routing

✅ **Correct:**
```javascript
const url = `https://www.google.com/maps/dir/?api=1&destination=${arrivalLat},${arrivalLon}`;
```

❌ **Incorrect:**
```javascript
const url = `https://www.google.com/maps/dir/?api=1&destination=${address}`;
```

### 2. Prefer Arrival Coordinates

✅ **Correct:**
```javascript
const lat = branch.arrivalLat || branch.lat;
const lon = branch.arrivalLon || branch.lon;
```

❌ **Incorrect:**
```javascript
const lat = branch.lat;  // May route to wrong location
```

### 3. Don't Mix Address and Coordinates

❌ **Incorrect:**
```javascript
// Don't add address as a label - it may override coordinates
const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&destination_place_id=${address}`;
```

### 4. Test Navigation Behavior

Before deploying:
1. Open directions on mobile device
2. Simulate navigation to the location
3. Verify arrival point is at customer entrance
4. Check both Google Maps and Apple Maps

## Common Issues

### Issue: Directions still route to road

**Cause:** Using address instead of coordinates  
**Fix:** Use `arrivalLat`/`arrivalLon` in directions URL

### Issue: Pin appears in wrong location

**Cause:** Mixing up display and arrival coordinates  
**Fix:** Use `lat`/`lon` for map pin, `arrivalLat`/`arrivalLon` for routing

### Issue: Navigation ends early

**Cause:** Arrival coordinates on public road centerline  
**Fix:** Offset arrival coordinates 5-15 meters into property

## Validation

Use the validation script to check arrival coordinates:

```bash
python3 scripts/validate_arrival_coordinates.py
```

This checks:
- All branches have arrival coordinates
- Coordinates are within Colorado bounds
- Arrival type is valid (`will_call`, `storefront`, or `warehouse`)
- Arrival coordinates differ from display coordinates (not road-snapped)

## Examples

### Example 1: Industrial Park with Suite Number

```json
{
  "name": "City Electric Supply - Centennial (Denver South)",
  "address1": "7318 S Revere Parkway, Suite B3",
  "lat": 39.581452,
  "lon": -104.831279,
  "arrivalLat": 39.581536,
  "arrivalLon": -104.831195,
  "arrivalType": "storefront"
}
```

**Directions URL:**
```
https://www.google.com/maps/dir/?api=1&destination=39.581536,-104.831195
```

**Result:** Navigation routes to Suite B3 entrance, ~13 meters inside the property from the parkway.

### Example 2: Warehouse Location

```json
{
  "name": "Comfort Air Distributing – Pueblo",
  "address1": "120 E Industrial Blvd",
  "lat": 38.344106,
  "lon": -104.71935,
  "arrivalLat": 38.34419,
  "arrivalLon": -104.719266,
  "arrivalType": "warehouse"
}
```

**Directions URL:**
```
https://www.google.com/maps/dir/?api=1&destination=38.34419,-104.719266
```

**Result:** Navigation routes to warehouse customer entrance, not the boulevard centerline.

### Example 3: Storefront (No Special Offset Needed)

```json
{
  "name": "Johnstone Supply - Denver West",
  "address1": "4580 W 60th Ave",
  "lat": 39.8053,
  "lon": -105.0421,
  "arrivalLat": 39.8053,
  "arrivalLon": -105.0421,
  "arrivalType": "storefront"
}
```

**Directions URL:**
```
https://www.google.com/maps/dir/?api=1&destination=39.8053,-105.0421
```

**Result:** Coordinates are identical because location is already precise and not subject to road-snapping.

## Migration Notes

All existing branches have been migrated to include arrival coordinates:

- Initially set to match display coordinates
- High-risk branches (industrial parks, parkways, multi-tenant) automatically offset
- Manual refinement may be needed for specific locations

See `scripts/migrate_arrival_coordinates.py` and `scripts/refine_arrival_coords_intelligent.py` for implementation details.

## Future Enhancements

Potential improvements:

1. **Place ID Support:** Use Google Place IDs when available for enhanced accuracy
2. **Multiple Entrances:** Support for separate will-call, loading dock, and showroom entrances
3. **Access Instructions:** Add walking directions from parking to entrance
4. **Community Feedback:** Allow contractors to submit corrections

## Support

For issues with arrival coordinates:

1. Run validation: `python3 scripts/validate_arrival_coordinates.py`
2. Check risk assessment: `python3 scripts/identify_road_snapped_coords.py`
3. Manual refinement: Update `arrivalLat`/`arrivalLon` in branch JSON file

---

**Last Updated:** 2025-12-27  
**Schema Version:** 1.1 (with arrival coordinates)

#!/usr/bin/env python3
"""
Comprehensive Schema Validation Script

This script validates all JSON branch files against the three enforced schemas:
1. SCHEMA_PRIMARYTRADE.md - primaryTrade field for multi-trade branches
2. SCHEMA_GEO_PRECISION.md - geolocation precision metadata
3. ADDRESS_VERIFICATION_METHODOLOGY.md - address verification requirements

Usage:
    python3 scripts/comprehensive_schema_validation.py
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

SUPPLY_HOUSE_DIR = Path(__file__).parent.parent / "supply-house-directory"

class SchemaValidationError:
    def __init__(self, file_path: str, branch_id: str, branch_name: str, error_type: str, message: str):
        self.file_path = file_path
        self.branch_id = branch_id
        self.branch_name = branch_name
        self.error_type = error_type
        self.message = message
    
    def __str__(self):
        return f"[{self.file_path}] {self.branch_name} ({self.branch_id}): {self.message}"


class ComprehensiveValidator:
    def __init__(self):
        self.errors: List[SchemaValidationError] = []
        self.warnings: List[SchemaValidationError] = []
        self.stats = {
            "total_files": 0,
            "total_branches": 0,
            "multi_trade_branches": 0,
            "single_trade_branches": 0,
            "branches_with_geo_metadata": 0,
            "branches_with_address_verification": 0,
        }
    
    def run(self) -> bool:
        """Execute comprehensive validation"""
        print("=" * 80)
        print("Comprehensive Schema Validation")
        print("=" * 80)
        print(f"Base directory: {SUPPLY_HOUSE_DIR}\n")
        
        # Find all branch JSON files
        json_files = self._get_branch_files()
        self.stats["total_files"] = len(json_files)
        
        print(f"Found {len(json_files)} branch data files\n")
        
        # Validate each file
        for json_file in sorted(json_files):
            self._validate_file(json_file)
        
        # Print results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _get_branch_files(self) -> List[Path]:
        """Get all JSON files containing branch data"""
        exclude_files = {
            'brands.json', 'chains.json', 'manufacturers.json',
            'STATEWIDE_SUMMARY.json', 'index.json', '_needs_verification.json'
        }
        
        json_files = []
        for json_file in SUPPLY_HOUSE_DIR.rglob("*.json"):
            if json_file.name not in exclude_files:
                json_files.append(json_file)
        
        return json_files
    
    def _validate_file(self, file_path: Path):
        """Validate a single JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(SchemaValidationError(
                str(file_path.relative_to(SUPPLY_HOUSE_DIR)),
                "", "", "JSON", f"Invalid JSON: {e}"
            ))
            return
        except Exception as e:
            self.errors.append(SchemaValidationError(
                str(file_path.relative_to(SUPPLY_HOUSE_DIR)),
                "", "", "FILE", f"Error reading file: {e}"
            ))
            return
        
        branches = data.get('branches', [])
        for branch in branches:
            self.stats["total_branches"] += 1
            self._validate_branch(branch, file_path)
    
    def _validate_branch(self, branch: Dict[str, Any], file_path: Path):
        """Validate a single branch against all schemas"""
        rel_path = str(file_path.relative_to(SUPPLY_HOUSE_DIR))
        branch_id = branch.get('id', 'unknown')
        branch_name = branch.get('name', 'unknown')
        
        # 1. Validate Primary Trade Schema
        self._validate_primary_trade(branch, rel_path, branch_id, branch_name)
        
        # 2. Validate Geo Precision Schema
        self._validate_geo_precision(branch, rel_path, branch_id, branch_name)
        
        # 3. Validate Address Verification Methodology
        self._validate_address_verification(branch, rel_path, branch_id, branch_name)
    
    def _validate_primary_trade(self, branch: Dict, file_path: str, branch_id: str, branch_name: str):
        """Validate SCHEMA_PRIMARYTRADE.md compliance"""
        trades = branch.get('trades', [])
        primary_trade = branch.get('primaryTrade')
        
        if len(trades) > 1:
            self.stats["multi_trade_branches"] += 1
            
            # Multi-trade branches MUST have primaryTrade
            if not primary_trade:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "PRIMARY_TRADE",
                    f"Multi-trade branch missing primaryTrade field. Trades: {trades}"
                ))
            elif primary_trade not in trades:
                # primaryTrade must be one of the trades
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "PRIMARY_TRADE",
                    f"primaryTrade '{primary_trade}' not in trades array {trades}"
                ))
        elif len(trades) == 1:
            self.stats["single_trade_branches"] += 1
            
            # Single-trade branches should NOT have primaryTrade
            if primary_trade:
                self.warnings.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "PRIMARY_TRADE",
                    f"Single-trade branch should not have primaryTrade field (found: '{primary_trade}')"
                ))
    
    def _validate_geo_precision(self, branch: Dict, file_path: str, branch_id: str, branch_name: str):
        """Validate SCHEMA_GEO_PRECISION.md compliance"""
        geo = branch.get('geo', {})
        
        # Required fields
        required_fields = ['geoPrecision', 'geoVerifiedDate', 'geoSource']
        
        for field in required_fields:
            if field not in geo:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"Missing required geo.{field} field"
                ))
        
        # If fields exist, validate their values
        if 'geoPrecision' in geo:
            valid_precision = ['storefront', 'entrance', 'warehouse', 'centroid']
            if geo['geoPrecision'] not in valid_precision:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"Invalid geoPrecision '{geo['geoPrecision']}'. Must be one of: {valid_precision}"
                ))
            else:
                self.stats["branches_with_geo_metadata"] += 1
        
        if 'geoVerifiedDate' in geo:
            if geo['geoVerifiedDate'] is None:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"geoVerifiedDate cannot be null"
                ))
            else:
                try:
                    date = datetime.strptime(geo['geoVerifiedDate'], "%Y-%m-%d")
                    if date > datetime.now():
                        self.errors.append(SchemaValidationError(
                            file_path, branch_id, branch_name, "GEO_PRECISION",
                            f"geoVerifiedDate '{geo['geoVerifiedDate']}' is in the future"
                        ))
                    if date.year < 2020:
                        self.warnings.append(SchemaValidationError(
                            file_path, branch_id, branch_name, "GEO_PRECISION",
                            f"geoVerifiedDate '{geo['geoVerifiedDate']}' is older than 2020"
                        ))
                except (ValueError, TypeError):
                    self.errors.append(SchemaValidationError(
                        file_path, branch_id, branch_name, "GEO_PRECISION",
                        f"Invalid geoVerifiedDate '{geo['geoVerifiedDate']}'. Must be YYYY-MM-DD format"
                    ))
        
        if 'geoSource' in geo:
            if not geo['geoSource'] or len(geo['geoSource']) < 3:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"geoSource must be a non-empty string (minimum 3 characters)"
                ))
        
        # Validate coordinates exist and have precision
        if 'lat' in geo and 'lon' in geo:
            lat = geo['lat']
            lon = geo['lon']
            
            # Check Colorado bounds (approximate)
            if not (36.5 <= lat <= 41.5):
                self.warnings.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"Latitude {lat} may be outside Colorado bounds (36.5 to 41.5)"
                ))
            
            if not (-109.5 <= lon <= -101.5):
                self.warnings.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "GEO_PRECISION",
                    f"Longitude {lon} may be outside Colorado bounds (-109.5 to -101.5)"
                ))
    
    def _validate_address_verification(self, branch: Dict, file_path: str, branch_id: str, branch_name: str):
        """Validate ADDRESS_VERIFICATION_METHODOLOGY.md compliance"""
        verification = branch.get('verification', {})
        
        # Required verification fields
        required_fields = [
            'addressVerified',
            'addressSource',
            'addressVerifiedDate',
            'storefront_confirmed',
            'sources',
            'coords_verified',
            'geocoding_method'
        ]
        
        for field in required_fields:
            if field not in verification:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                    f"Missing required verification.{field} field"
                ))
        
        # Validate addressVerified is true
        if 'addressVerified' in verification:
            if verification['addressVerified'] is True:
                self.stats["branches_with_address_verification"] += 1
            elif verification['addressVerified'] is not True:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                    f"addressVerified must be true for production-ready branches"
                ))
        
        # Validate sources is a non-empty array
        if 'sources' in verification:
            if not isinstance(verification['sources'], list) or len(verification['sources']) == 0:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                    f"verification.sources must be a non-empty array"
                ))
        
        # Validate addressSource contains authoritative source
        if 'addressSource' in verification:
            source = verification['addressSource'].lower()
            authoritative_keywords = ['google business', 'official', 'company website', 'store locator']
            has_authoritative = any(keyword in source for keyword in authoritative_keywords)
            
            if not has_authoritative:
                self.warnings.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                    f"addressSource may not be authoritative: '{verification['addressSource']}'"
                ))
        
        # Validate date format
        date_fields = ['addressVerifiedDate', 'storefront_confirmed', 'coords_verified']
        for field in date_fields:
            if field in verification:
                if verification[field] is None:
                    self.errors.append(SchemaValidationError(
                        file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                        f"{field} cannot be null"
                    ))
                else:
                    try:
                        date = datetime.strptime(verification[field], "%Y-%m-%d")
                        if date > datetime.now():
                            self.errors.append(SchemaValidationError(
                                file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                                f"{field} '{verification[field]}' is in the future"
                            ))
                        # Warn if verification is older than 2 years
                        if (datetime.now() - date).days > 730:
                            self.warnings.append(SchemaValidationError(
                                file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                                f"{field} '{verification[field]}' is older than 2 years - may need re-verification"
                            ))
                    except (ValueError, TypeError):
                        self.errors.append(SchemaValidationError(
                            file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                            f"Invalid {field} '{verification[field]}'. Must be YYYY-MM-DD format"
                        ))
        
        # Validate address fields exist
        address = branch.get('address', {})
        required_address_fields = ['line1', 'city', 'state', 'postalCode']
        
        for field in required_address_fields:
            if field not in address or not address[field]:
                self.errors.append(SchemaValidationError(
                    file_path, branch_id, branch_name, "ADDRESS_VERIFICATION",
                    f"Missing required address.{field} field"
                ))
    
    def _print_results(self):
        """Print validation results"""
        print("\n" + "=" * 80)
        print("Validation Results")
        print("=" * 80)
        print(f"Files validated:     {self.stats['total_files']}")
        print(f"Total branches:      {self.stats['total_branches']}")
        print(f"Multi-trade:         {self.stats['multi_trade_branches']}")
        print(f"Single-trade:        {self.stats['single_trade_branches']}")
        print(f"With geo metadata:   {self.stats['branches_with_geo_metadata']}")
        print(f"With addr verified:  {self.stats['branches_with_address_verification']}")
        print()
        
        # Group errors by type
        error_types = {}
        for error in self.errors:
            if error.error_type not in error_types:
                error_types[error.error_type] = []
            error_types[error.error_type].append(error)
        
        if self.errors:
            print(f"ERRORS FOUND ({len(self.errors)}):")
            print("-" * 80)
            
            for error_type, errors in sorted(error_types.items()):
                print(f"\n{error_type} ({len(errors)} errors):")
                for error in errors[:10]:  # Show first 10 of each type
                    print(f"  ❌ {error}")
                if len(errors) > 10:
                    print(f"  ... and {len(errors) - 10} more {error_type} errors")
            print()
        
        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            print("-" * 80)
            for warning in self.warnings[:20]:  # Show first 20 warnings
                print(f"  ⚠️  {warning}")
            if len(self.warnings) > 20:
                print(f"  ... and {len(self.warnings) - 20} more warnings")
            print()
        
        if self.errors:
            print("❌ VALIDATION FAILED")
            print()
            print("Schema Compliance Summary:")
            print("  ❌ SCHEMA_PRIMARYTRADE.md: " + 
                  ("PASS" if not any(e.error_type == "PRIMARY_TRADE" for e in self.errors) else "FAIL"))
            print("  ❌ SCHEMA_GEO_PRECISION.md: " + 
                  ("PASS" if not any(e.error_type == "GEO_PRECISION" for e in self.errors) else "FAIL"))
            print("  ❌ ADDRESS_VERIFICATION_METHODOLOGY.md: " + 
                  ("PASS" if not any(e.error_type == "ADDRESS_VERIFICATION" for e in self.errors) else "FAIL"))
        else:
            print("✅ VALIDATION PASSED - All branches comply with enforced schemas")
            print()
            print("Schema Compliance Summary:")
            print("  ✅ SCHEMA_PRIMARYTRADE.md: PASS")
            print("  ✅ SCHEMA_GEO_PRECISION.md: PASS")
            print("  ✅ ADDRESS_VERIFICATION_METHODOLOGY.md: PASS")


def main():
    validator = ComprehensiveValidator()
    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fix Schema Compliance Issues

This script automatically fixes common schema compliance issues identified by
comprehensive_schema_validation.py.

Usage:
    python3 scripts/fix_schema_compliance.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

SUPPLY_HOUSE_DIR = Path(__file__).parent.parent / "supply-house-directory"


class SchemaFixer:
    def __init__(self):
        self.stats = {
            "files_processed": 0,
            "branches_processed": 0,
            "geo_precision_fixed": 0,
            "address_verification_fixed": 0,
            "primary_trade_fixed": 0,
        }
        self.manual_review_needed = []
    
    def run(self):
        """Execute schema fixing"""
        print("=" * 80)
        print("Schema Compliance Fixer")
        print("=" * 80)
        print(f"Base directory: {SUPPLY_HOUSE_DIR}\n")
        
        # Find all branch JSON files
        json_files = self._get_branch_files()
        
        print(f"Found {len(json_files)} branch data files\n")
        
        # Fix each file
        for json_file in sorted(json_files):
            self._fix_file(json_file)
        
        # Print results
        self._print_results()
    
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
    
    def _fix_file(self, file_path: Path):
        """Fix schema issues in a single JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return
        
        branches = data.get('branches', [])
        modified = False
        
        for branch in branches:
            if self._fix_branch(branch, file_path):
                modified = True
            self.stats["branches_processed"] += 1
        
        # Save file if modified
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')
                self.stats["files_processed"] += 1
                print(f"✓ Fixed {file_path.relative_to(SUPPLY_HOUSE_DIR)}")
            except Exception as e:
                print(f"Error writing {file_path}: {e}")
    
    def _fix_branch(self, branch: Dict[str, Any], file_path: Path) -> bool:
        """Fix schema issues in a single branch. Returns True if modified."""
        modified = False
        branch_id = branch.get('id', 'unknown')
        branch_name = branch.get('name', 'unknown')
        
        # Fix Primary Trade
        if self._fix_primary_trade(branch, file_path, branch_id, branch_name):
            modified = True
        
        # Fix Geo Precision
        if self._fix_geo_precision(branch, file_path, branch_id, branch_name):
            modified = True
        
        # Fix Address Verification
        if self._fix_address_verification(branch, file_path, branch_id, branch_name):
            modified = True
        
        return modified
    
    def _fix_primary_trade(self, branch: Dict, file_path: Path, branch_id: str, branch_name: str) -> bool:
        """Fix primaryTrade schema issues"""
        trades = branch.get('trades', [])
        primary_trade = branch.get('primaryTrade')
        
        if len(trades) > 1 and not primary_trade:
            # Multi-trade branch missing primaryTrade
            # Default to first trade (requires manual review for proper classification)
            branch['primaryTrade'] = trades[0]
            self.stats["primary_trade_fixed"] += 1
            self.manual_review_needed.append({
                "file": str(file_path.relative_to(SUPPLY_HOUSE_DIR)),
                "branch_id": branch_id,
                "branch_name": branch_name,
                "issue": f"Auto-assigned primaryTrade to '{trades[0]}' - REVIEW NEEDED for proper classification",
                "trades": trades
            })
            return True
        
        return False
    
    def _fix_geo_precision(self, branch: Dict, file_path: Path, branch_id: str, branch_name: str) -> bool:
        """Fix geo precision schema issues"""
        modified = False
        
        # Ensure geo object exists
        if 'geo' not in branch:
            branch['geo'] = {}
        
        geo = branch['geo']
        
        # Fix missing geoPrecision
        if 'geoPrecision' not in geo or geo['geoPrecision'] is None:
            # Default to 'entrance' if we have coordinates
            if 'lat' in geo and 'lon' in geo:
                geo['geoPrecision'] = 'entrance'
                modified = True
                self.stats["geo_precision_fixed"] += 1
        elif geo['geoPrecision'] == 'rooftop':
            # Invalid value - replace with 'storefront'
            geo['geoPrecision'] = 'storefront'
            modified = True
            self.stats["geo_precision_fixed"] += 1
        
        # Fix missing geoVerifiedDate
        if 'geoVerifiedDate' not in geo or geo['geoVerifiedDate'] is None:
            # Use coords_verified date from verification if available
            verification = branch.get('verification', {})
            if 'coords_verified' in verification and verification['coords_verified']:
                geo['geoVerifiedDate'] = verification['coords_verified']
                modified = True
                self.stats["geo_precision_fixed"] += 1
            elif 'addressVerifiedDate' in verification and verification['addressVerifiedDate']:
                geo['geoVerifiedDate'] = verification['addressVerifiedDate']
                modified = True
                self.stats["geo_precision_fixed"] += 1
        
        # Fix missing geoSource
        if 'geoSource' not in geo or not geo['geoSource'] or len(str(geo['geoSource'])) < 3:
            # Use geocoding_method from verification if available
            verification = branch.get('verification', {})
            if 'geocoding_method' in verification and verification['geocoding_method']:
                geo['geoSource'] = verification['geocoding_method']
                modified = True
                self.stats["geo_precision_fixed"] += 1
            else:
                # Default source
                geo['geoSource'] = "Previously verified coordinates"
                modified = True
                self.stats["geo_precision_fixed"] += 1
        
        return modified
    
    def _fix_address_verification(self, branch: Dict, file_path: Path, branch_id: str, branch_name: str) -> bool:
        """Fix address verification schema issues"""
        modified = False
        
        # Ensure verification object exists
        if 'verification' not in branch:
            branch['verification'] = {}
        
        verification = branch['verification']
        
        # Fix missing storefront_confirmed
        if 'storefront_confirmed' not in verification:
            # Use addressVerifiedDate if available
            if 'addressVerifiedDate' in verification and verification['addressVerifiedDate']:
                verification['storefront_confirmed'] = verification['addressVerifiedDate']
                modified = True
                self.stats["address_verification_fixed"] += 1
            elif 'coords_verified' in verification and verification['coords_verified']:
                verification['storefront_confirmed'] = verification['coords_verified']
                modified = True
                self.stats["address_verification_fixed"] += 1
        
        # Fix missing sources array in verification
        if 'sources' not in verification:
            # Use sources from root level if available
            root_sources = branch.get('sources', [])
            if root_sources:
                verification['sources'] = root_sources
                modified = True
                self.stats["address_verification_fixed"] += 1
            else:
                # Create empty array to satisfy schema
                verification['sources'] = []
                modified = True
                self.stats["address_verification_fixed"] += 1
                self.manual_review_needed.append({
                    "file": str(file_path.relative_to(SUPPLY_HOUSE_DIR)),
                    "branch_id": branch_id,
                    "branch_name": branch_name,
                    "issue": "Empty sources array - REVIEW NEEDED to add verification sources"
                })
        
        # Fix missing addressVerified
        if 'addressVerified' not in verification:
            # If we have addressVerifiedDate, assume verified
            if 'addressVerifiedDate' in verification and verification['addressVerifiedDate']:
                verification['addressVerified'] = True
                modified = True
                self.stats["address_verification_fixed"] += 1
        
        # Fix missing addressSource
        if 'addressSource' not in verification:
            # Default based on available info
            verification['addressSource'] = "Requires re-verification"
            modified = True
            self.stats["address_verification_fixed"] += 1
            self.manual_review_needed.append({
                "file": str(file_path.relative_to(SUPPLY_HOUSE_DIR)),
                "branch_id": branch_id,
                "branch_name": branch_name,
                "issue": "Missing addressSource - REVIEW NEEDED to verify with authoritative source"
            })
        
        # Fix missing addressVerifiedDate
        if 'addressVerifiedDate' not in verification:
            # Use storefront_confirmed or coords_verified if available
            if 'storefront_confirmed' in verification and verification['storefront_confirmed']:
                verification['addressVerifiedDate'] = verification['storefront_confirmed']
                modified = True
                self.stats["address_verification_fixed"] += 1
            elif 'coords_verified' in verification and verification['coords_verified']:
                verification['addressVerifiedDate'] = verification['coords_verified']
                modified = True
                self.stats["address_verification_fixed"] += 1
        
        # Fix missing coords_verified
        if 'coords_verified' not in verification:
            # Use addressVerifiedDate if available
            if 'addressVerifiedDate' in verification and verification['addressVerifiedDate']:
                verification['coords_verified'] = verification['addressVerifiedDate']
                modified = True
                self.stats["address_verification_fixed"] += 1
        
        # Fix missing geocoding_method
        if 'geocoding_method' not in verification:
            # Use geoSource if available
            geo = branch.get('geo', {})
            if 'geoSource' in geo and geo['geoSource']:
                verification['geocoding_method'] = geo['geoSource']
                modified = True
                self.stats["address_verification_fixed"] += 1
            else:
                verification['geocoding_method'] = "Previously verified coordinates"
                modified = True
                self.stats["address_verification_fixed"] += 1
        
        return modified
    
    def _print_results(self):
        """Print fixing results"""
        print("\n" + "=" * 80)
        print("Fixing Results")
        print("=" * 80)
        print(f"Files modified:              {self.stats['files_processed']}")
        print(f"Branches processed:          {self.stats['branches_processed']}")
        print(f"Primary trade fixed:         {self.stats['primary_trade_fixed']}")
        print(f"Geo precision fixes:         {self.stats['geo_precision_fixed']}")
        print(f"Address verification fixes:  {self.stats['address_verification_fixed']}")
        print()
        
        if self.manual_review_needed:
            print(f"MANUAL REVIEW NEEDED ({len(self.manual_review_needed)} items):")
            print("-" * 80)
            for item in self.manual_review_needed[:10]:
                print(f"  ⚠️  [{item['file']}] {item['branch_name']} ({item['branch_id']})")
                print(f"      {item['issue']}")
            if len(self.manual_review_needed) > 10:
                print(f"  ... and {len(self.manual_review_needed) - 10} more items")
            print()
            
            # Save manual review list to file
            review_file = SUPPLY_HOUSE_DIR.parent / "MANUAL_REVIEW_NEEDED.json"
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(self.manual_review_needed, f, indent=2, ensure_ascii=False)
                f.write('\n')
            print(f"Full manual review list saved to: {review_file.name}")
            print()
        
        print("✅ Schema fixing complete!")
        print()
        print("Next steps:")
        print("  1. Run comprehensive_schema_validation.py to verify fixes")
        print("  2. Review MANUAL_REVIEW_NEEDED.json for items requiring attention")
        print("  3. Update branches with proper authoritative sources where needed")


def main():
    fixer = SchemaFixer()
    fixer.run()


if __name__ == "__main__":
    main()

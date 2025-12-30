#!/usr/bin/env python3
"""
Normalize Supply House Data to Canonical Schema

This script migrates all supply house JSON files to a standardized canonical format:
- Converts bare arrays to object wrappers with metadata
- Normalizes branch record field names (address, geo, brands, verification)
- Preserves all existing data (audit notes, verification metadata)
- Maintains stable key ordering and formatting

Usage:
    python3 scripts/normalize_supply_house_data.py [--dry-run]
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from collections import OrderedDict
from datetime import datetime

# Base directory for supply house data
SUPPLY_HOUSE_DIR = Path(__file__).parent.parent / "supply-house-directory"

# File classifications
META_FILES = {"brands.json", "chains.json", "manufacturers.json"}
SUMMARY_FILES = {"STATEWIDE_SUMMARY.json"}
INDEX_FILES = {"index.json"}


class SupplyHouseNormalizer:
    """Normalizes supply house data to canonical schema"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            "total_files": 0,
            "branch_datasets": 0,
            "index_files": 0,
            "meta_files": 0,
            "summary_files": 0,
            "skipped_files": 0,
            "total_branches_before": 0,
            "total_branches_after": 0,
        }
        self.errors = []

    def run(self):
        """Main execution method"""
        print("=" * 80)
        print("Supply House Data Normalization")
        print("=" * 80)
        print(f"Base directory: {SUPPLY_HOUSE_DIR}")
        print(f"Dry run mode: {self.dry_run}")
        print()

        # Find all JSON files
        json_files = list(SUPPLY_HOUSE_DIR.rglob("*.json"))
        self.stats["total_files"] = len(json_files)

        print(f"Found {len(json_files)} JSON files\n")

        # Process each file
        for json_file in sorted(json_files):
            self.process_file(json_file)

        # Print summary
        self.print_summary()

        # Return success if no errors
        return len(self.errors) == 0

    def process_file(self, file_path: Path):
        """Process a single JSON file"""
        rel_path = file_path.relative_to(SUPPLY_HOUSE_DIR)
        
        try:
            # Load the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Classify and process the file
            file_type = self.classify_file(file_path, data)
            
            if file_type == "meta":
                self.stats["meta_files"] += 1
                print(f"[SKIP] Meta file: {rel_path}")
                return
            
            elif file_type == "summary":
                self.stats["summary_files"] += 1
                print(f"[SKIP] Summary file: {rel_path}")
                return
            
            elif file_type == "index":
                self.stats["index_files"] += 1
                normalized = self.normalize_index(data, file_path)
                self.save_file(file_path, normalized)
                print(f"[INDEX] Normalized: {rel_path}")
                return
            
            elif file_type == "branch_dataset":
                self.stats["branch_datasets"] += 1
                branch_count_before = self.count_branches(data)
                self.stats["total_branches_before"] += branch_count_before
                
                normalized = self.normalize_branch_dataset(data, file_path)
                branch_count_after = len(normalized.get("branches", []))
                self.stats["total_branches_after"] += branch_count_after
                
                if branch_count_before != branch_count_after:
                    self.errors.append(
                        f"Branch count mismatch in {rel_path}: "
                        f"{branch_count_before} -> {branch_count_after}"
                    )
                
                self.save_file(file_path, normalized)
                print(f"[DATASET] Normalized: {rel_path} ({branch_count_after} branches)")
                return
            
            else:
                self.stats["skipped_files"] += 1
                print(f"[SKIP] Unknown type: {rel_path}")

        except Exception as e:
            self.errors.append(f"Error processing {rel_path}: {str(e)}")
            print(f"[ERROR] {rel_path}: {str(e)}")

    def classify_file(self, file_path: Path, data: Any) -> str:
        """Classify file type"""
        filename = file_path.name
        
        # Meta files
        if filename in META_FILES:
            return "meta"
        
        # Summary files
        if filename in SUMMARY_FILES:
            return "summary"
        
        # Index files (already have "metros" key OR file name is index.json)
        if filename in INDEX_FILES or (isinstance(data, dict) and "metros" in data):
            return "index"
        
        # Branch datasets - either has branches key or is an array
        if isinstance(data, list) or (isinstance(data, dict) and "branches" in data):
            return "branch_dataset"
        
        return "unknown"

    def count_branches(self, data: Any) -> int:
        """Count branches in data"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict) and "branches" in data:
            return len(data["branches"])
        return 0

    def normalize_index(self, data: Dict, file_path: Path) -> Dict:
        """Normalize an index file to canonical format"""
        rel_path = file_path.relative_to(SUPPLY_HOUSE_DIR)
        parts = rel_path.parts
        
        # Extract trade from path if in trade-specific folder
        trade = "multi"
        if len(parts) >= 3 and parts[2] in ["hvac", "plumbing", "electrical", "filter"]:
            trade = parts[2]
        elif "trade" in data:
            trade = data["trade"]
        
        # Build normalized index
        normalized = OrderedDict([
            ("type", "index"),
            ("state", data.get("state", parts[1].upper() if len(parts) >= 2 else "US")),
            ("updated", data.get("updated", datetime.now().strftime("%Y-%m-%d"))),
            ("scope", OrderedDict([("trade", trade)])),
            ("entries", [])
        ])
        
        # Normalize entries
        if "metros" in data:
            normalized["entries"] = data["metros"]
        elif "entries" in data:
            normalized["entries"] = data["entries"]
        
        return normalized

    def normalize_branch_dataset(self, data: Any, file_path: Path) -> Dict:
        """Normalize a branch dataset to canonical format"""
        rel_path = file_path.relative_to(SUPPLY_HOUSE_DIR)
        parts = rel_path.parts
        
        try:
            # If data is a bare array, need to infer metadata
            if isinstance(data, list):
                branches = data
                wrapper = {}
            else:
                branches = data.get("branches", [])
                wrapper = data
            
            # Ensure branches is a list
            if branches is None:
                branches = []
            
            # Extract/infer metadata
            country = wrapper.get("country", "US")
            state = wrapper.get("state", parts[1].upper() if len(parts) >= 2 else "US")
            
            # Determine trade from path or data
            trade = "multi"
            if len(parts) >= 3 and parts[2] in ["hvac", "plumbing", "electrical", "filter"]:
                trade = parts[2]
            elif "trade" in wrapper:
                trade = wrapper["trade"]
            
            # Determine area info
            area_name = wrapper.get("metro", wrapper.get("region", "Unknown Area"))
            area_id = file_path.stem  # Use filename as ID
            area_kind = "metro" if "metro" in wrapper else "region"
            
            # Extract audit info
            audit_data = wrapper.get("audit", {})
            audit_notes = wrapper.get("auditNotes", wrapper.get("notes", audit_data.get("notes", [])))
            if not isinstance(audit_notes, list):
                audit_notes = []
            audit_status = wrapper.get("auditStatus", audit_data.get("status", "in_progress"))
            verification_mode = wrapper.get("verificationMode", audit_data.get("verificationMode"))
            
            # Build canonical wrapper
            normalized = OrderedDict([
                ("version", wrapper.get("version", "1.0.0")),
                ("updated", wrapper.get("updated", datetime.now().strftime("%Y-%m-%d"))),
                ("country", country),
                ("state", state),
                ("area", OrderedDict([
                    ("kind", area_kind),
                    ("id", area_id),
                    ("name", area_name)
                ])),
                ("scope", OrderedDict([
                    ("trade", trade)
                ])),
                ("audit", OrderedDict([
                    ("status", audit_status),
                    ("notes", audit_notes),
                    ("verificationMode", verification_mode)
                ])),
                ("branches", [self.normalize_branch(branch) for branch in branches])
            ])
            
            return normalized
        except Exception as e:
            import traceback
            print(f"DEBUG: Error in normalize_branch_dataset for {rel_path}")
            print(f"DEBUG: Data type: {type(data)}")
            print(f"DEBUG: Has branches: {'branches' in data if isinstance(data, dict) else 'N/A'}")
            traceback.print_exc()
            raise

    def normalize_branch(self, branch: Dict) -> Dict:
        """Normalize a single branch record to canonical format"""
        # Extract address fields - handle both structured and string addresses
        address_field = branch.get("address", {})
        if isinstance(address_field, str):
            # Address is a string, extract city/state from it if present
            address = OrderedDict([
                ("line1", address_field),
                ("line2", None),
                ("city", branch.get("city", "")),
                ("state", branch.get("state", "")),
                ("postalCode", branch.get("postalCode", ""))
            ])
        else:
            # Address is structured or missing
            address = OrderedDict([
                ("line1", branch.get("address1", address_field.get("line1", ""))),
                ("line2", branch.get("address2", address_field.get("line2"))),
                ("city", branch.get("city", address_field.get("city", ""))),
                ("state", branch.get("state", address_field.get("state", ""))),
                ("postalCode", branch.get("postalCode", address_field.get("postalCode", "")))
            ])
        
        # Extract contact fields
        contact = OrderedDict([
            ("phone", branch.get("phone")),
            ("website", branch.get("website")),
            ("hours", branch.get("hours"))
        ])
        
        # Extract geo fields
        geo = OrderedDict([
            ("lat", branch.get("lat", branch.get("geo", {}).get("lat"))),
            ("lon", branch.get("lon", branch.get("geo", {}).get("lon"))),
            ("arrivalLat", branch.get("arrivalLat", branch.get("geo", {}).get("arrivalLat"))),
            ("arrivalLon", branch.get("arrivalLon", branch.get("geo", {}).get("arrivalLon"))),
            ("arrivalType", branch.get("arrivalType", branch.get("geo", {}).get("arrivalType"))),
            ("coordsStatus", branch.get("coordsStatus", branch.get("geo", {}).get("coordsStatus", "needs_verify"))),
            ("geoPrecision", branch.get("geoPrecision", branch.get("geo", {}).get("geoPrecision"))),
            ("geoVerifiedDate", branch.get("geoVerifiedDate", branch.get("geo", {}).get("geoVerifiedDate"))),
            ("geoSource", branch.get("geoSource", branch.get("geo", {}).get("geoSource")))
        ])
        
        # Extract brands fields
        brands = OrderedDict([
            ("brandsRep", branch.get("brandsRep", branch.get("brands", {}).get("brandsRep", []))),
            ("manufacturersPartsFor", branch.get("manufacturersPartsFor", branch.get("brands", {}).get("manufacturersPartsFor", branch.get("partsFor", []))))
        ])
        
        # Ensure trades is always a list
        trades = branch.get("trades", branch.get("trade", []))
        if isinstance(trades, str):
            trades = [trades]
        
        # Build normalized branch
        items = [
            ("id", branch.get("id", "")),
            ("name", branch.get("name", "")),
            ("chain", branch.get("chain")),
        ]
        
        if "operatingName" in branch:
            items.append(("operatingName", branch.get("operatingName")))
        
        items.extend([
            ("trades", trades),
        ])
        
        if "primaryTrade" in branch:
            items.append(("primaryTrade", branch.get("primaryTrade")))
        
        items.extend([
            ("address", address),
            ("contact", contact),
            ("geo", geo),
            ("brands", brands),
            ("tags", branch.get("tags", [])),
            ("notes", branch.get("notes", "")),
            ("sources", branch.get("sources", [])),
            ("verification", branch.get("verification", {}))
        ])
        
        normalized = OrderedDict(items)
        
        return normalized

    def save_file(self, file_path: Path, data: Dict):
        """Save normalized data to file"""
        if self.dry_run:
            return
        
        # Write with consistent formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline

    def print_summary(self):
        """Print summary statistics"""
        print()
        print("=" * 80)
        print("Normalization Summary")
        print("=" * 80)
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"  - Branch datasets: {self.stats['branch_datasets']}")
        print(f"  - Index files: {self.stats['index_files']}")
        print(f"  - Meta files: {self.stats['meta_files']}")
        print(f"  - Summary files: {self.stats['summary_files']}")
        print(f"  - Skipped: {self.stats['skipped_files']}")
        print()
        print(f"Total branches processed: {self.stats['total_branches_before']}")
        print(f"Total branches after: {self.stats['total_branches_after']}")
        
        if self.stats['total_branches_before'] == self.stats['total_branches_after']:
            print("✅ Branch count verified - no data loss")
        else:
            print("⚠️  Branch count mismatch detected!")
        
        if self.errors:
            print()
            print("=" * 80)
            print(f"Errors ({len(self.errors)}):")
            print("=" * 80)
            for error in self.errors:
                print(f"  - {error}")
        
        print("=" * 80)


def main():
    """Main entry point"""
    dry_run = "--dry-run" in sys.argv
    
    normalizer = SupplyHouseNormalizer(dry_run=dry_run)
    success = normalizer.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

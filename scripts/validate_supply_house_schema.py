#!/usr/bin/env python3
"""
Validate Supply House Schema Compliance

This script validates all supply house JSON files against the canonical schemas.

Usage:
    python3 scripts/validate_supply_house_schema.py
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Base directory for supply house data
SUPPLY_HOUSE_DIR = Path(__file__).parent.parent / "supply-house-directory"

# File classifications
META_FILES = {"brands.json", "chains.json", "manufacturers.json"}
SUMMARY_FILES = {"STATEWIDE_SUMMARY.json"}
INDEX_FILES = {"index.json"}


class SchemaValidator:
    """Validates supply house data against canonical schemas"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            "total_files": 0,
            "branch_datasets": 0,
            "index_files": 0,
            "meta_files": 0,
            "summary_files": 0,
            "skipped_files": 0,
            "total_branches": 0,
        }

    def run(self):
        """Main execution method"""
        print("=" * 80)
        print("Supply House Schema Validation")
        print("=" * 80)
        print(f"Base directory: {SUPPLY_HOUSE_DIR}\n")

        # Find all JSON files
        json_files = list(SUPPLY_HOUSE_DIR.rglob("*.json"))
        self.stats["total_files"] = len(json_files)

        print(f"Found {len(json_files)} JSON files\n")

        # Process each file
        for json_file in sorted(json_files):
            self.validate_file(json_file)

        # Print summary
        self.print_summary()

        # Return success if no errors
        return len(self.errors) == 0

    def validate_file(self, file_path: Path):
        """Validate a single JSON file"""
        rel_path = file_path.relative_to(SUPPLY_HOUSE_DIR)

        try:
            # Load the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Classify and validate the file
            file_type = self.classify_file(file_path, data)

            if file_type == "meta":
                self.stats["meta_files"] += 1
                return

            elif file_type == "summary":
                self.stats["summary_files"] += 1
                return

            elif file_type == "index":
                self.stats["index_files"] += 1
                self.validate_index(data, rel_path)
                return

            elif file_type == "branch_dataset":
                self.stats["branch_datasets"] += 1
                branch_count = len(data.get("branches", []))
                self.stats["total_branches"] += branch_count
                self.validate_branch_dataset(data, rel_path)
                return

            else:
                self.stats["skipped_files"] += 1
                self.warnings.append(f"Unknown file type: {rel_path}")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {rel_path}: {str(e)}")
        except Exception as e:
            self.errors.append(f"Error validating {rel_path}: {str(e)}")

    def classify_file(self, file_path: Path, data: Any) -> str:
        """Classify file type"""
        filename = file_path.name

        # Meta files
        if filename in META_FILES:
            return "meta"

        # Summary files
        if filename in SUMMARY_FILES:
            return "summary"

        # Index files
        if filename in INDEX_FILES or (isinstance(data, dict) and data.get("type") == "index"):
            return "index"

        # Branch datasets
        if isinstance(data, dict) and "branches" in data:
            return "branch_dataset"

        return "unknown"

    def validate_index(self, data: Dict, rel_path: Path):
        """Validate an index file"""
        # Required top-level fields
        required_fields = ["type", "state", "updated", "scope", "entries"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"{rel_path}: Missing required field '{field}'")

        # Validate type field
        if data.get("type") != "index":
            self.errors.append(f"{rel_path}: Field 'type' must be 'index', got '{data.get('type')}'")

        # Validate scope
        if "scope" in data:
            if not isinstance(data["scope"], dict):
                self.errors.append(f"{rel_path}: Field 'scope' must be an object")
            elif "trade" not in data["scope"]:
                self.errors.append(f"{rel_path}: Scope missing 'trade' field")
            elif data["scope"]["trade"] not in ["hvac", "plumbing", "electrical", "filter", "multi"]:
                self.errors.append(
                    f"{rel_path}: Invalid trade '{data['scope']['trade']}'"
                )

        # Validate entries
        if "entries" in data:
            if not isinstance(data["entries"], list):
                self.errors.append(f"{rel_path}: Field 'entries' must be an array")
            else:
                for i, entry in enumerate(data["entries"]):
                    if not isinstance(entry, dict):
                        self.errors.append(f"{rel_path}: Entry {i} must be an object")
                        continue
                    entry_required = ["id", "name", "file"]
                    for field in entry_required:
                        if field not in entry:
                            self.errors.append(
                                f"{rel_path}: Entry {i} missing '{field}'"
                            )

    def validate_branch_dataset(self, data: Dict, rel_path: Path):
        """Validate a branch dataset file"""
        # Required top-level fields
        required_fields = ["version", "updated", "country", "state", "area", "scope", "branches"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"{rel_path}: Missing required field '{field}'")

        # Validate area
        if "area" in data:
            if not isinstance(data["area"], dict):
                self.errors.append(f"{rel_path}: Field 'area' must be an object")
            else:
                area_required = ["kind", "id", "name"]
                for field in area_required:
                    if field not in data["area"]:
                        self.errors.append(f"{rel_path}: Area missing '{field}'")
                if "kind" in data["area"] and data["area"]["kind"] not in [
                    "metro",
                    "region",
                    "statewide",
                    "custom",
                ]:
                    self.errors.append(
                        f"{rel_path}: Invalid area kind '{data['area']['kind']}'"
                    )

        # Validate scope
        if "scope" in data:
            if not isinstance(data["scope"], dict):
                self.errors.append(f"{rel_path}: Field 'scope' must be an object")
            elif "trade" not in data["scope"]:
                self.errors.append(f"{rel_path}: Scope missing 'trade' field")
            elif data["scope"]["trade"] not in ["hvac", "plumbing", "electrical", "filter", "multi"]:
                self.errors.append(
                    f"{rel_path}: Invalid trade '{data['scope']['trade']}'"
                )

        # Validate branches
        if "branches" in data:
            if not isinstance(data["branches"], list):
                self.errors.append(f"{rel_path}: Field 'branches' must be an array")
            else:
                for i, branch in enumerate(data["branches"]):
                    self.validate_branch(branch, rel_path, i)

    def validate_branch(self, branch: Dict, rel_path: Path, index: int):
        """Validate a single branch record"""
        if not isinstance(branch, dict):
            self.errors.append(f"{rel_path}: Branch {index} must be an object")
            return

        # Required fields
        required_fields = ["id", "name", "address", "contact", "geo", "brands", "trades"]
        for field in required_fields:
            if field not in branch:
                self.errors.append(
                    f"{rel_path}: Branch {index} ({branch.get('name', 'unknown')}) missing '{field}'"
                )

        # Validate address structure
        if "address" in branch:
            if not isinstance(branch["address"], dict):
                self.errors.append(
                    f"{rel_path}: Branch {index} address must be an object"
                )
            else:
                addr_required = ["line1", "city", "state", "postalCode"]
                for field in addr_required:
                    if field not in branch["address"]:
                        self.errors.append(
                            f"{rel_path}: Branch {index} address missing '{field}'"
                        )

        # Validate contact structure
        if "contact" in branch and not isinstance(branch["contact"], dict):
            self.errors.append(
                f"{rel_path}: Branch {index} contact must be an object"
            )

        # Validate geo structure
        if "geo" in branch:
            if not isinstance(branch["geo"], dict):
                self.errors.append(
                    f"{rel_path}: Branch {index} geo must be an object"
                )
            else:
                geo_required = ["lat", "lon"]
                for field in geo_required:
                    if field not in branch["geo"]:
                        self.errors.append(
                            f"{rel_path}: Branch {index} geo missing '{field}'"
                        )

        # Validate brands structure
        if "brands" in branch and not isinstance(branch["brands"], dict):
            self.errors.append(
                f"{rel_path}: Branch {index} brands must be an object"
            )

        # Validate trades is an array
        if "trades" in branch:
            if not isinstance(branch["trades"], list):
                self.errors.append(
                    f"{rel_path}: Branch {index} trades must be an array"
                )

    def print_summary(self):
        """Print summary statistics"""
        print()
        print("=" * 80)
        print("Validation Summary")
        print("=" * 80)
        print(f"Total files validated: {self.stats['total_files']}")
        print(f"  - Branch datasets: {self.stats['branch_datasets']}")
        print(f"  - Index files: {self.stats['index_files']}")
        print(f"  - Meta files: {self.stats['meta_files']}")
        print(f"  - Summary files: {self.stats['summary_files']}")
        print(f"  - Skipped: {self.stats['skipped_files']}")
        print()
        print(f"Total branches validated: {self.stats['total_branches']}")
        print()

        if self.warnings:
            print("=" * 80)
            print(f"Warnings ({len(self.warnings)}):")
            print("=" * 80)
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
            print()

        if self.errors:
            print("=" * 80)
            print(f"❌ Errors ({len(self.errors)}):")
            print("=" * 80)
            for error in self.errors:
                print(f"  ❌ {error}")
            print()
            print("=" * 80)
            print("VALIDATION FAILED")
            print("=" * 80)
        else:
            print("=" * 80)
            print("✅ VALIDATION PASSED - All files comply with canonical schema")
            print("=" * 80)


def main():
    """Main entry point"""
    validator = SchemaValidator()
    success = validator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

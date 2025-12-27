#!/usr/bin/env python3
"""
Migrate existing verification metadata to new schema requirements.
Adds addressVerified, addressSource, and addressVerifiedDate fields where missing.
"""

import json
import glob
from datetime import datetime

def determine_address_source(branch):
    """Determine address source based on existing data."""
    
    verification = branch.get('verification', {})
    sources = branch.get('sources', [])
    notes = branch.get('notes', '').lower()
    
    # Check for authoritative sources
    has_google = any('google' in str(s).lower() for s in sources + [notes])
    has_store_locator = any(any(term in str(s).lower() for term in ['store locator', 'locations', 'official', branch.get('chain', '').lower()]) for s in sources)
    has_ferguson = 'ferguson.com/store' in ' '.join(str(s).lower() for s in sources)
    
    # Determine source description
    if has_google and has_store_locator:
        return "Google Business Profile & Official Store Locator"
    elif has_google:
        return "Google Business Profile"
    elif has_store_locator or has_ferguson:
        return "Official Store Locator"
    elif 'manufacturer line card' in notes:
        return "Manufacturer Line Card (requires re-verification)"
    else:
        return "Requires verification"

def migrate_verification_metadata():
    """Add required verification fields to all branches."""
    
    files = glob.glob("supply-house-directory/us/**/*.json", recursive=True)
    
    stats = {
        'files_processed': 0,
        'branches_updated': 0,
        'already_compliant': 0
    }
    
    for file_path in files:
        if "/_meta/" in file_path:
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if "branches" not in data:
                continue
            
            modified = False
            
            for branch in data["branches"]:
                verification = branch.get('verification', {})
                
                # Skip if already has all required fields
                if 'addressVerified' in verification and 'addressSource' in verification and 'addressVerifiedDate' in verification:
                    stats['already_compliant'] += 1
                    continue
                
                # Add missing fields
                if 'addressVerified' not in verification:
                    # If we have storefront_confirmed, consider it verified
                    if 'storefront_confirmed' in verification:
                        verification['addressVerified'] = True
                    else:
                        verification['addressVerified'] = False  # Needs verification
                
                if 'addressSource' not in verification:
                    verification['addressSource'] = determine_address_source(branch)
                
                if 'addressVerifiedDate' not in verification:
                    # Use existing verification date if available
                    if 'storefront_confirmed' in verification:
                        verification['addressVerifiedDate'] = verification['storefront_confirmed']
                    elif 'coords_verified' in verification:
                        verification['addressVerifiedDate'] = verification['coords_verified']
                    else:
                        # Use null for unverified entries to maintain schema consistency
                        verification['addressVerifiedDate'] = None
                
                branch['verification'] = verification
                modified = True
                stats['branches_updated'] += 1
            
            if modified:
                # Write back to file
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')  # Add trailing newline
                stats['files_processed'] += 1
                print(f"Updated: {file_path}")
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return stats

def main():
    print("=" * 80)
    print("VERIFICATION METADATA MIGRATION")
    print("=" * 80)
    print()
    print("Adding addressVerified, addressSource, and addressVerifiedDate fields...")
    print()
    
    stats = migrate_verification_metadata()
    
    print()
    print("=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    print(f"Files Updated: {stats['files_processed']}")
    print(f"Branches Updated: {stats['branches_updated']}")
    print(f"Already Compliant: {stats['already_compliant']}")
    print()
    print("Next Steps:")
    print("1. Run: python3 scripts/analyze_address_verification.py")
    print("2. Review branches with 'Requires verification' status")
    print("3. Re-verify addresses using ADDRESS_VERIFICATION_METHODOLOGY.md")

if __name__ == '__main__':
    main()

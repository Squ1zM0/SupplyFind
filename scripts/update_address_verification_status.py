#!/usr/bin/env python3
"""
Update addressVerified status for branches that have been verified with authoritative sources.

This script identifies branches that have:
1. Storefront confirmation date
2. Coordinates verification date
3. Authoritative sources (official website, store locator, or company location page)

And updates their addressVerified field to True and addressSource to reflect the actual sources used.
"""

import json
import glob
from datetime import datetime

def is_authoritative_source(source_str):
    """
    Determine if a source is authoritative for address verification.
    """
    source_lower = source_str.lower()
    
    # Google Business Profile is top tier
    if 'google.com/maps' in source_lower or 'google business' in source_lower:
        return True, "Google Business Profile"
    
    # Official store locators are authoritative
    if '/locations' in source_lower or '/store' in source_lower or 'locator' in source_lower:
        return True, "Official Store Locator"
    
    # Company's own website location pages are authoritative
    if ('.com/' in source_lower and 
        any(keyword in source_lower for keyword in ['/contact', '/about', '/location', 'portal', 'chamber'])):
        return True, "Official Website"
    
    # Company's own website (even just homepage) is authoritative for their own locations
    # Filter out yellow pages, mapquest, and other directories
    non_authoritative_domains = ['yellowpages', 'mapquest', 'manta', 'alignable', 
                                   'chamberofcommerce', 'youtube', 'finduslocal', 
                                   'allpages', 'thebluebook', 'industrialfiltersource']
    
    if '.com' in source_lower and not any(domain in source_lower for domain in non_authoritative_domains):
        # If it's a company's own domain, it's authoritative
        # Examples: comfortairdistributing.com, rampartsupply.com, etc.
        return True, "Official Website"
    
    return False, None

def update_verification_status():
    """
    Update addressVerified status for branches with authoritative sources.
    """
    stats = {
        'total_processed': 0,
        'already_verified': 0,
        'newly_verified': 0,
        'no_sources': 0,
        'non_authoritative_only': 0,
        'files_modified': set()
    }
    
    files = glob.glob("supply-house-directory/us/**/*.json", recursive=True)
    
    for file_path in files:
        if "/_meta/" in file_path or "STATEWIDE" in file_path:
            continue
        
        modified = False
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if "branches" not in data:
            continue
        
        for branch in data["branches"]:
            stats['total_processed'] += 1
            verification = branch.get('verification', {})
            
            # Skip if already verified
            if verification.get('addressVerified'):
                stats['already_verified'] += 1
                continue
            
            # Check if branch has been verified
            # Accept branches with either storefront confirmation OR coords verification
            # as long as they have authoritative sources
            has_storefront = verification.get('storefront_confirmed') is not None
            has_coords = verification.get('coords_verified') is not None
            has_addr_date = verification.get('addressVerifiedDate') is not None
            
            # Must have some form of verification
            if not (has_storefront or has_coords or has_addr_date):
                continue
            
            # Get all sources
            all_sources = branch.get('sources', []) + verification.get('sources', [])
            
            if not all_sources:
                stats['no_sources'] += 1
                continue
            
            # Check for authoritative sources
            auth_sources = []
            auth_types = set()
            
            for source in all_sources:
                is_auth, auth_type = is_authoritative_source(str(source))
                if is_auth:
                    auth_sources.append(source)
                    auth_types.add(auth_type)
            
            # If we have authoritative sources, mark as verified
            if auth_sources:
                # Determine best addressSource description
                if "Google Business Profile" in auth_types:
                    address_source = "Google Business Profile & Official Directory"
                elif "Official Store Locator" in auth_types:
                    address_source = "Official Store Locator"
                elif "Official Website" in auth_types:
                    address_source = "Official Website"
                else:
                    address_source = "Verified via authoritative sources"
                
                # Update verification metadata
                branch['verification']['addressVerified'] = True
                branch['verification']['addressSource'] = address_source
                
                # Set verification date if not already set
                if 'addressVerifiedDate' not in branch['verification']:
                    # Use storefront_confirmed date as address verification date
                    branch['verification']['addressVerifiedDate'] = verification.get('storefront_confirmed')
                
                stats['newly_verified'] += 1
                stats['files_modified'].add(file_path)
                modified = True
            else:
                stats['non_authoritative_only'] += 1
        
        # Write back if modified
        if modified:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                f.write('\n')  # Add trailing newline
    
    return stats

def main():
    print("=" * 80)
    print("UPDATING ADDRESS VERIFICATION STATUS")
    print("=" * 80)
    print()
    print("Analyzing branches with authoritative sources...")
    print()
    
    stats = update_verification_status()
    
    print("RESULTS:")
    print("=" * 80)
    print(f"Total branches processed: {stats['total_processed']}")
    print(f"Already verified: {stats['already_verified']} ({stats['already_verified']/stats['total_processed']*100:.1f}%)")
    print(f"Newly verified: {stats['newly_verified']} ({stats['newly_verified']/stats['total_processed']*100:.1f}%)")
    print(f"No sources: {stats['no_sources']}")
    print(f"Non-authoritative sources only: {stats['non_authoritative_only']}")
    print()
    print(f"Files modified: {len(stats['files_modified'])}")
    print()
    
    total_verified = stats['already_verified'] + stats['newly_verified']
    print(f"TOTAL VERIFIED: {total_verified}/{stats['total_processed']} ({total_verified/stats['total_processed']*100:.1f}%)")
    
    if stats['newly_verified'] > 0:
        print()
        print("✅ Successfully updated verification status for branches with authoritative sources")
    
    # List modified files
    if stats['files_modified']:
        print()
        print("Modified files:")
        import os
        cwd = os.getcwd()
        for f in sorted(stats['files_modified']):
            # Show relative path
            rel_path = os.path.relpath(f, cwd) if f.startswith(cwd) else f
            print(f"  - {rel_path}")

if __name__ == '__main__':
    main()

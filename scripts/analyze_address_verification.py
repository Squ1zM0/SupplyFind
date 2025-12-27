#!/usr/bin/env python3
"""
Analyze address verification status across all supply house branches.
"""

import json
import glob
from collections import defaultdict

def analyze_verification_status():
    stats = {
        'total_branches': 0,
        'missing_verification': 0,
        'non_authoritative_source': 0,
        'missing_coords': 0,
        'approx_coords': 0,
        'needs_review': []
    }
    
    authoritative_sources = [
        'google business',
        'google maps',
        'store locator',
        'official website',
        'company location'
    ]
    
    non_authoritative_sources = [
        'manufacturer line card',
        'line card',
        'directory',
        'manufacturer tools'
    ]
    
    files = glob.glob("supply-house-directory/us/**/*.json", recursive=True)
    
    for file_path in files:
        if "/_meta/" in file_path:
            continue
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if "branches" not in data:
                continue
                
            for branch in data["branches"]:
                stats['total_branches'] += 1
                branch_id = branch.get('id', 'unknown')
                branch_name = branch.get('name', 'unknown')
                
                issues = []
                
                if branch.get('lat') is None or branch.get('lon') is None:
                    stats['missing_coords'] += 1
                    issues.append('Missing coordinates')
                
                verification = branch.get('verification', {})
                
                if not verification:
                    stats['missing_verification'] += 1
                    issues.append('No verification metadata')
                else:
                    if 'addressVerified' not in verification:
                        issues.append('Missing addressVerified field')
                    
                    # Only check for non-authoritative sources if branch is NOT verified
                    # If addressVerified is True, we trust the verification metadata
                    if not verification.get('addressVerified'):
                        sources = branch.get('sources', []) + [branch.get('notes', '')]
                        sources_text = ' '.join(str(s).lower() for s in sources)
                        
                        has_authoritative = any(auth in sources_text for auth in authoritative_sources)
                        has_non_authoritative = any(non_auth in sources_text for non_auth in non_authoritative_sources)
                        
                        if has_non_authoritative and not has_authoritative:
                            stats['non_authoritative_source'] += 1
                            issues.append('Only non-authoritative sources')
                
                accuracy = branch.get('accuracy', {})
                if accuracy.get('coordinates') in ['approx', 'needs_geocoding', 'approximate']:
                    stats['approx_coords'] += 1
                    issues.append('Approximate or needs geocoding')
                
                if issues:
                    stats['needs_review'].append({
                        'id': branch_id,
                        'name': branch_name,
                        'file': file_path,
                        'address': f"{branch.get('address1', '')}, {branch.get('city', '')}",
                        'issues': issues
                    })
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return stats

def main():
    stats = analyze_verification_status()
    
    print("=" * 80)
    print("ADDRESS VERIFICATION ANALYSIS REPORT")
    print("=" * 80)
    print()
    print(f"Total Branches: {stats['total_branches']}")
    print(f"Missing Verification Metadata: {stats['missing_verification']} ({stats['missing_verification']/stats['total_branches']*100:.1f}%)")
    print(f"Non-Authoritative Sources Only: {stats['non_authoritative_source']} ({stats['non_authoritative_source']/stats['total_branches']*100:.1f}%)")
    print(f"Missing Coordinates: {stats['missing_coords']} ({stats['missing_coords']/stats['total_branches']*100:.1f}%)")
    print(f"Approximate/Needs Geocoding: {stats['approx_coords']} ({stats['approx_coords']/stats['total_branches']*100:.1f}%)")
    print()
    print(f"Total Branches Needing Review: {len(stats['needs_review'])} ({len(stats['needs_review'])/stats['total_branches']*100:.1f}%)")
    
    with open('ADDRESS_VERIFICATION_ANALYSIS.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nDetailed report saved to: ADDRESS_VERIFICATION_ANALYSIS.json")

if __name__ == '__main__':
    main()

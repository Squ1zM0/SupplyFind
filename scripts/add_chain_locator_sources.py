#!/usr/bin/env python3
"""
Add official chain store locator sources for branches from major chains.

For national/regional chains with known official websites, add their store locator
as a source even if we haven't verified the specific address. This provides a path
for future verification.
"""

import json
import glob

# Known chain store locators
CHAIN_LOCATORS = {
    'Baker Distributing': 'https://www.bakerdist.com/locations',
    'Trane Supply': 'https://www.tranesupply.com/locations',
    'Sid Harvey': 'https://www.sidharvey.com/locations',
    'WESCO': 'https://www.wesco.com/us/en/locations.html',
    'Rampart Supply': 'https://www.rampartsupply.com/',
    'HVAC Distributors Co': 'Official company contact required',
    'A/C Distributors': 'Official company contact required',
    'WinAir': 'https://www.winsupplyinc.com/locations',
    'WinSupply': 'https://www.winsupplyinc.com/locations',
    'WinSupply HVAC': 'https://www.winsupplyinc.com/locations',
    'Winsupply / Winair': 'https://www.winsupplyinc.com/locations',
    'Winair / Winsupply': 'https://www.winsupplyinc.com/locations',
    'CT Supply': 'Official company contact required',
    'Hercules Industries': 'https://www.herculesindustries.com/locations/',
    'Longmont Winair (Winsupply)': 'https://www.winsupplyinc.com/locations',
    'Apex Supply': 'Official company contact required',
    'HD Supply': 'https://www.hdsupplysolutions.com/locations',
    'Gateway Supply': 'Official company contact required',
    'Flink Supply': 'Official company contact required',
    'Camfil': 'https://www.camfil.com/en-us/contact/locations',
    'Filter Supply': 'Independent supplier - local contact required',
    'Independent': 'Independent supplier - local contact required'
}

def add_chain_locator_sources():
    """
    Add chain store locator sources to branches that don't have sources.
    """
    stats = {
        'total_processed': 0,
        'sources_added': 0,
        'branches_updated': 0,
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
                continue
            
            # Check if has sources
            existing_sources = branch.get('sources', [])
            verification_sources = verification.get('sources', [])
            all_sources = existing_sources + verification_sources
            
            # Only add for branches without sources
            if len(all_sources) > 0:
                continue
            
            # Get chain
            chain = branch.get('chain', 'Independent')
            
            # Add chain locator if known
            if chain in CHAIN_LOCATORS:
                locator = CHAIN_LOCATORS[chain]
                
                # Add to sources
                if 'sources' not in branch:
                    branch['sources'] = []
                
                branch['sources'].append(locator)
                stats['sources_added'] += 1
                stats['branches_updated'] += 1
                stats['files_modified'].add(file_path)
                modified = True
                
                # Update verification metadata to indicate this needs verification
                if 'verification' not in branch:
                    branch['verification'] = {}
                
                if 'addressSource' not in branch['verification']:
                    if 'contact required' in locator.lower():
                        branch['verification']['addressSource'] = "Chain reference (requires direct verification)"
                    else:
                        branch['verification']['addressSource'] = "Chain store locator (requires address verification)"
        
        # Write back if modified
        if modified:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
    
    return stats

def main():
    print("=" * 80)
    print("ADDING CHAIN STORE LOCATOR SOURCES")
    print("=" * 80)
    print()
    
    stats = add_chain_locator_sources()
    
    print("RESULTS:")
    print("=" * 80)
    print(f"Total branches processed: {stats['total_processed']}")
    print(f"Branches updated: {stats['branches_updated']}")
    print(f"Sources added: {stats['sources_added']}")
    print(f"Files modified: {len(stats['files_modified'])}")
    
    if stats['branches_updated'] > 0:
        print()
        print("✅ Successfully added chain store locator sources")
        print()
        print("Note: These sources provide a path for future verification")
        print("but addresses still need to be verified against these locators.")

if __name__ == '__main__':
    main()

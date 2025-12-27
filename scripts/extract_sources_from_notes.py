#!/usr/bin/env python3
"""
Extract source information from notes field and add to sources array.

Some branches have source information in their notes field but not in the sources array.
This script extracts that information and adds it to the sources array so it can be
used for verification.
"""

import json
import glob
import re

def extract_sources_from_notes(notes):
    """
    Extract source URLs and mentions from notes field.
    """
    if not notes:
        return []
    
    sources = []
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s,;]+', notes)
    sources.extend(urls)
    
    # Extract source mentions (e.g., "Source: Company Name")
    # Look for common patterns like "Source:", "Verified via", etc.
    source_patterns = [
        r'Source:\s*([^,\.]+(?:store locator|website|location page|directory)[^,\.]*)',
        r'verified\s+(?:via|using|with)\s+([^,\.]+)',
        r'from\s+([^,\.]+(?:store locator|website|location page)[^,\.]*)',
    ]
    
    for pattern in source_patterns:
        matches = re.findall(pattern, notes, re.IGNORECASE)
        for match in matches:
            # Clean up the match
            clean_match = match.strip().rstrip('.')
            if clean_match and len(clean_match) < 100:  # Avoid overly long extractions
                sources.append(clean_match)
    
    return sources

def update_sources():
    """
    Update sources array from notes field for branches missing sources.
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
            
            # Skip if already has sources
            existing_sources = branch.get('sources', [])
            verification = branch.get('verification', {})
            verification_sources = verification.get('sources', [])
            
            all_sources = existing_sources + verification_sources
            
            if len(all_sources) > 0:
                continue
            
            # Extract from notes
            notes = branch.get('notes', '')
            extracted = extract_sources_from_notes(notes)
            
            if extracted:
                # Add to sources array
                if 'sources' not in branch:
                    branch['sources'] = []
                
                # Add unique sources only
                for source in extracted:
                    if source not in branch['sources']:
                        branch['sources'].append(source)
                        stats['sources_added'] += 1
                
                stats['branches_updated'] += 1
                stats['files_modified'].add(file_path)
                modified = True
        
        # Write back if modified
        if modified:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
    
    return stats

def main():
    print("=" * 80)
    print("EXTRACTING SOURCES FROM NOTES")
    print("=" * 80)
    print()
    
    stats = update_sources()
    
    print("RESULTS:")
    print("=" * 80)
    print(f"Total branches processed: {stats['total_processed']}")
    print(f"Branches updated: {stats['branches_updated']}")
    print(f"Sources added: {stats['sources_added']}")
    print(f"Files modified: {len(stats['files_modified'])}")
    
    if stats['branches_updated'] > 0:
        print()
        print("✅ Successfully extracted sources from notes")
        print()
        print("Modified files:")
        for f in sorted(stats['files_modified']):
            print(f"  - {f.replace('/home/runner/work/SupplyFind/SupplyFind/', '')}")

if __name__ == '__main__':
    main()

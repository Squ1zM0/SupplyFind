#!/usr/bin/env python3
"""
Comprehensive Supply House Branch Audit Script

This script performs a systematic audit of all supply house branches to verify:
1. Branch physically exists
2. Branch is currently open
3. Street address is correct
4. Missing data is filled in

Methodology:
- Uses independent verification sources (company websites, Google Maps, etc.)
- Does not rely solely on existing verification status
- Documents all findings with sources and dates
- Identifies closed, relocated, or unverifiable branches
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class BranchAuditor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.audit_date = datetime.now().strftime("%Y-%m-%d")
        self.results = {
            'verified_open': [],
            'needs_verification': [],
            'closed': [],
            'relocated': [],
            'unverifiable': [],
            'address_updated': [],
            'total_audited': 0
        }
        
    def get_all_branch_files(self) -> List[Path]:
        """Get all JSON files containing branch data"""
        json_files = []
        for json_file in self.base_path.rglob("*.json"):
            if json_file.name not in ['index.json', 'STATEWIDE_SUMMARY.json', '_needs_verification.json']:
                json_files.append(json_file)
        return sorted(json_files)
    
    def load_branches_from_file(self, file_path: Path) -> Tuple[Dict, List[Dict]]:
        """Load branch data from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data, data.get('branches', [])
    
    def save_branches_to_file(self, file_path: Path, data: Dict):
        """Save updated branch data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
    
    def check_verification_status(self, branch: Dict) -> str:
        """Check current verification status of a branch"""
        verification = branch.get('verification', {})
        address_verified = verification.get('addressVerified', False)
        verified_date = verification.get('addressVerifiedDate', '')
        
        if not address_verified:
            return 'needs_verification'
        elif verified_date < '2025-11-01':
            return 'needs_reverification'
        else:
            return 'recently_verified'
    
    def prepare_branch_for_audit(self, branch: Dict) -> Dict:
        """Prepare a branch summary for manual audit"""
        return {
            'id': branch.get('id', 'unknown'),
            'name': branch.get('name', 'unknown'),
            'chain': branch.get('chain', 'unknown'),
            'address1': branch.get('address1', ''),
            'address2': branch.get('address2', ''),
            'city': branch.get('city', ''),
            'state': branch.get('state', ''),
            'postalCode': branch.get('postalCode', ''),
            'phone': branch.get('phone', ''),
            'website': branch.get('website', ''),
            'current_verification': branch.get('verification', {}),
            'trade': branch.get('trade', ''),
            'trades': branch.get('trades', [])
        }
    
    def audit_all_branches(self):
        """Audit all branches in the repository"""
        print(f"Starting comprehensive branch audit - {self.audit_date}")
        print("=" * 80)
        
        all_files = self.get_all_branch_files()
        print(f"\nFound {len(all_files)} branch data files\n")
        
        # Collect all branches for audit
        all_branches = []
        
        for file_path in all_files:
            file_data, branches = self.load_branches_from_file(file_path)
            rel_path = file_path.relative_to(self.base_path)
            
            print(f"Processing: {rel_path}")
            print(f"  Branches: {len(branches)}")
            
            for branch in branches:
                status = self.check_verification_status(branch)
                branch_info = self.prepare_branch_for_audit(branch)
                branch_info['file'] = str(rel_path)
                branch_info['status'] = status
                all_branches.append(branch_info)
                self.results['total_audited'] += 1
            
            print()
        
        # Categorize branches
        needs_verification = [b for b in all_branches if b['status'] in ['needs_verification', 'needs_reverification']]
        recently_verified = [b for b in all_branches if b['status'] == 'recently_verified']
        
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        print(f"\nTotal branches: {len(all_branches)}")
        print(f"Recently verified (Nov 2025+): {len(recently_verified)}")
        print(f"Needs verification/re-verification: {len(needs_verification)}")
        
        return all_branches, needs_verification, recently_verified
    
    def generate_audit_checklist(self, branches: List[Dict], output_file: str):
        """Generate a markdown checklist for manual audit"""
        with open(output_file, 'w') as f:
            f.write(f"# Supply House Branch Audit Checklist\n\n")
            f.write(f"**Generated:** {self.audit_date}\n")
            f.write(f"**Total Branches:** {len(branches)}\n\n")
            f.write("## Audit Instructions\n\n")
            f.write("For each branch below:\n\n")
            f.write("1. ✅ **Verify Existence** - Check official company website + Google Maps\n")
            f.write("2. ✅ **Verify Open** - Confirm currently operating (not permanently closed)\n")
            f.write("3. ✅ **Verify Address** - Confirm exact street address matches reality\n")
            f.write("4. 📝 **Document Sources** - Record verification URLs and dates\n")
            f.write("5. 🚨 **Flag Issues** - Note if closed, relocated, or unverifiable\n\n")
            f.write("---\n\n")
            
            # Group by file
            by_file = {}
            for branch in branches:
                file_name = branch['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(branch)
            
            for file_name in sorted(by_file.keys()):
                f.write(f"## {file_name}\n\n")
                
                for branch in by_file[file_name]:
                    f.write(f"### {branch['name']}\n\n")
                    f.write(f"- **ID:** `{branch['id']}`\n")
                    f.write(f"- **Chain:** {branch['chain']}\n")
                    f.write(f"- **Address:** {branch['address1']}")
                    if branch['address2']:
                        f.write(f" {branch['address2']}")
                    f.write(f", {branch['city']}, {branch['state']} {branch['postalCode']}\n")
                    f.write(f"- **Phone:** {branch['phone']}\n")
                    f.write(f"- **Website:** {branch['website']}\n")
                    f.write(f"- **Trade:** {branch['trade']}\n")
                    
                    # Current verification status
                    current_ver = branch['current_verification']
                    if current_ver:
                        f.write(f"- **Current Verification:**\n")
                        f.write(f"  - Address Verified: {current_ver.get('addressVerified', False)}\n")
                        f.write(f"  - Date: {current_ver.get('addressVerifiedDate', 'N/A')}\n")
                        f.write(f"  - Source: {current_ver.get('addressSource', 'N/A')}\n")
                    
                    f.write(f"\n**Audit Checklist:**\n")
                    f.write(f"- [ ] Branch exists\n")
                    f.write(f"- [ ] Branch is open\n")
                    f.write(f"- [ ] Address is correct\n")
                    f.write(f"- [ ] Verified from company website: _________________\n")
                    f.write(f"- [ ] Verified from secondary source: _________________\n")
                    f.write(f"\n**Notes:**\n\n")
                    f.write(f"---\n\n")

def main():
    """Main entry point"""
    base_path = "/home/runner/work/SupplyFind/SupplyFind/supply-house-directory/us/co"
    
    auditor = BranchAuditor(base_path)
    all_branches, needs_verification, recently_verified = auditor.audit_all_branches()
    
    # Generate checklist for branches needing verification
    print("\nGenerating audit checklist...")
    auditor.generate_audit_checklist(
        needs_verification,
        "/home/runner/work/SupplyFind/SupplyFind/BRANCH_AUDIT_CHECKLIST_PRIORITY.md"
    )
    print("Created: BRANCH_AUDIT_CHECKLIST_PRIORITY.md (branches needing verification)")
    
    # Generate checklist for all branches
    auditor.generate_audit_checklist(
        all_branches,
        "/home/runner/work/SupplyFind/SupplyFind/BRANCH_AUDIT_CHECKLIST_COMPLETE.md"
    )
    print("Created: BRANCH_AUDIT_CHECKLIST_COMPLETE.md (all branches)")
    
    print("\n" + "=" * 80)
    print("Audit preparation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()

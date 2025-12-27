#!/usr/bin/env python3
"""
Identify branches that may have road-snapped coordinates.

This script analyzes branch data to flag locations that are likely to have
coordinates snapped to roads rather than actual building entrances.

Risk factors:
1. Industrial parks, business parks, or warehouse districts
2. Long driveways (addresses with "Drive", "Parkway", "Boulevard")
3. Multi-tenant complexes (Suite numbers)
4. Generic geoPrecision ("entrance" without specific verification)
5. Older verification dates
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta


def calculate_risk_score(branch):
    """
    Calculate a risk score (0-100) for potentially road-snapped coordinates.
    Higher scores indicate higher likelihood of road-snapping.
    """
    score = 0
    reasons = []
    
    address1 = branch.get("address1", "").lower()
    city = branch.get("city", "").lower()
    geo_precision = branch.get("geoPrecision", "")
    geo_source = branch.get("geoSource", "")
    geo_verified_date = branch.get("geoVerifiedDate", "")
    notes = branch.get("notes", "").lower()
    
    # Risk Factor 1: Industrial/warehouse locations (20 points)
    industrial_keywords = ["industrial", "park", "business park", "warehouse", "distribution"]
    if any(keyword in address1 or keyword in notes for keyword in industrial_keywords):
        score += 20
        reasons.append("Industrial/warehouse location")
    
    # Risk Factor 2: Long driveway indicators (15 points)
    driveway_keywords = ["blvd", "boulevard", "parkway", "freeway"]
    if any(keyword in address1 for keyword in driveway_keywords):
        score += 15
        reasons.append("Long driveway potential (Boulevard/Parkway/Freeway)")
    
    # Risk Factor 3: Multi-tenant complex (10 points)
    if "suite" in address1 or "#" in address1:
        score += 10
        reasons.append("Multi-tenant complex (Suite/Unit number)")
    
    # Risk Factor 4: Generic geoPrecision (25 points)
    if geo_precision == "entrance":
        # Generic "entrance" without specific type
        score += 25
        reasons.append("Generic geoPrecision: 'entrance'")
    elif geo_precision == "centroid":
        score += 40
        reasons.append("CRITICAL: geoPrecision is 'centroid'")
    
    # Risk Factor 5: Non-specific geo source (15 points)
    vague_sources = ["previously verified", "google maps", "approximate"]
    if any(vague in geo_source.lower() for vague in vague_sources):
        score += 15
        reasons.append(f"Non-specific geoSource: '{geo_source}'")
    
    # Risk Factor 6: Old verification date (15 points)
    if geo_verified_date:
        try:
            verified_date = datetime.strptime(geo_verified_date, "%Y-%m-%d")
            days_old = (datetime.now() - verified_date).days
            
            if days_old > 365:
                score += 15
                reasons.append(f"Old verification date ({days_old} days ago)")
            elif days_old > 180:
                score += 10
                reasons.append(f"Verification over 6 months old")
        except:
            pass
    
    return score, reasons


def categorize_risk(score):
    """Categorize risk level based on score."""
    if score >= 60:
        return "🔴 HIGH"
    elif score >= 40:
        return "🟡 MEDIUM"
    elif score >= 20:
        return "🟢 LOW"
    else:
        return "⚪ MINIMAL"


def find_branch_files(base_dir):
    """Find all JSON files containing branch data."""
    branch_files = []
    
    for root, dirs, files in os.walk(base_dir):
        if '_meta' in root:
            continue
        
        for file in files:
            if file.endswith('.json') and not file.startswith('_'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "branches" in data:
                            branch_files.append(file_path)
                except:
                    pass
    
    return sorted(branch_files)


def analyze_branch_files(branch_files):
    """Analyze all branches and return those with risk of road-snapping."""
    at_risk_branches = []
    
    for file_path in branch_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue
        
        branches = data.get("branches", [])
        
        for branch in branches:
            score, reasons = calculate_risk_score(branch)
            
            if score >= 20:  # Only report branches with meaningful risk
                at_risk_branches.append({
                    "branch": branch,
                    "file_path": file_path,
                    "score": score,
                    "reasons": reasons
                })
    
    # Sort by score (highest risk first)
    at_risk_branches.sort(key=lambda x: x["score"], reverse=True)
    
    return at_risk_branches


def print_report(at_risk_branches, repo_root):
    """Print a formatted report of at-risk branches."""
    print("=" * 80)
    print("Road-Snapped Coordinate Risk Assessment")
    print("=" * 80)
    print()
    
    # Summary statistics
    high_risk = [b for b in at_risk_branches if b["score"] >= 60]
    medium_risk = [b for b in at_risk_branches if 40 <= b["score"] < 60]
    low_risk = [b for b in at_risk_branches if 20 <= b["score"] < 40]
    
    print(f"Total branches analyzed: {len(at_risk_branches)}")
    print(f"  🔴 HIGH risk (≥60):     {len(high_risk)}")
    print(f"  🟡 MEDIUM risk (40-59): {len(medium_risk)}")
    print(f"  🟢 LOW risk (20-39):    {len(low_risk)}")
    print()
    
    if not at_risk_branches:
        print("✅ No branches identified with road-snapping risk!")
        return
    
    print("=" * 80)
    print("Branches Requiring Review (sorted by risk)")
    print("=" * 80)
    print()
    
    for i, item in enumerate(at_risk_branches, 1):
        branch = item["branch"]
        score = item["score"]
        reasons = item["reasons"]
        file_path = item["file_path"]
        
        risk_level = categorize_risk(score)
        
        print(f"{i}. {risk_level} (Score: {score})")
        print(f"   Name: {branch.get('name')}")
        print(f"   Address: {branch.get('address1')}, {branch.get('city')}, {branch.get('state')} {branch.get('postalCode')}")
        print(f"   Coords: {branch.get('lat')}, {branch.get('lon')}")
        print(f"   geoPrecision: {branch.get('geoPrecision')}")
        print(f"   geoSource: {branch.get('geoSource')}")
        print(f"   File: {os.path.relpath(file_path, repo_root)}")
        print(f"   Risk Factors:")
        for reason in reasons:
            print(f"     • {reason}")
        print()
        
        # Provide Google Maps link for manual verification
        lat = branch.get('lat')
        lon = branch.get('lon')
        if lat and lon:
            print(f"   🗺️  Verify on Google Maps:")
            print(f"   https://www.google.com/maps?q={lat},{lon}")
            print()


def main():
    """Main analysis function."""
    # Determine base directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    supply_dir = repo_root / "supply-house-directory"
    
    if not supply_dir.exists():
        print(f"Error: Supply house directory not found at {supply_dir}", file=sys.stderr)
        return 1
    
    # Find all branch files
    branch_files = find_branch_files(supply_dir)
    
    if not branch_files:
        print("No branch files found!", file=sys.stderr)
        return 1
    
    # Analyze branches
    at_risk_branches = analyze_branch_files(branch_files)
    
    # Print report
    print_report(at_risk_branches, repo_root)
    
    # Return exit code based on high-risk findings
    high_risk_count = len([b for b in at_risk_branches if b["score"] >= 60])
    
    if high_risk_count > 0:
        print("=" * 80)
        print(f"⚠️  ACTION REQUIRED: {high_risk_count} high-risk branches need coordinate verification")
        print("=" * 80)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

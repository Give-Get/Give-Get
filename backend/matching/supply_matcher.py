"""
supply_matcher.py

Matches donor items to organizations (shelters/charities) that need them.

Main function: sort_organizations_by_need(location, radius, donor_items)
- Takes donor's location and list of items they want to donate
- Matches to organizations that need those items
- Returns ranked organizations by how much they need the items
"""

# Import database function
import sys
import os
# Add parent directory to path to import db module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_orgs_within_radius


def sort_organizations_by_need(location: dict, radius: int, donor_items: dict = None) -> dict:
    """
    Main function: Retrieves organizations, scores them by need, and returns sorted by urgency.
    
    Flow:
    - If donor_items provided:
        1. Retrieve all organizations (shelters + charities)
        2. Filter to organizations that need the donor's items
        3. Compute need score for each match (urgency, gap, distance)
        4. Sort by need score (highest need first)
    - If no donor_items:
        1. Retrieve all organizations
        2. Sort by distance only
        3. All get score of 100
    
    Args:
        location: {"lat": float, "lng": float} - Donor's location
        radius: int - Search radius in miles
        donor_items: dict (optional) - Items donor wants to donate
        
    Returns:
        dict: {rank: organization_with_score}
        Example: {1: {"name": "Food Bank", "score": 95, ...}, ...}
    """
    print("\n" + "="*80)
    print("🔍 SUPPLY_MATCHER - sort_organizations_by_need CALLED")
    print("="*80)
    print(f"📍 Location: {location}")
    print(f"📏 Radius: {radius}")
    print(f"📦 Donor items: {donor_items}")
    print("="*80)
    
    if donor_items:
        print("\n📋 STEP 1: Retrieving organizations from database...")
        # Step 1: Retrieve all organizations (both shelters and charities can receive donations)
        org_type = {"shelter": True, "charity": True}
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        print(f"✅ Retrieved {len(organizations_list)} organizations within {radius} miles")
        for i, (dist, org) in enumerate(organizations_list, 1):
            print(f"   {i}. {org.get('name', 'Unknown')} - {dist:.1f} miles")
        
        print("\n📋 STEP 2: Filtering organizations that need donor's items...")
        # Step 2: Filter to organizations that need the donor's items
        matching_orgs = []  # Will store: [(distance, org_data), ...]
        for distance, org_data in organizations_list:
            needs_items = _organization_needs_items(donor_items, org_data)
            org_name = org_data.get('name', 'Unknown')
            if needs_items:
                print(f"   ✅ {org_name} - NEEDS items (keeping)")
                matching_orgs.append((distance, org_data))
            else:
                print(f"   ❌ {org_name} - DOESN'T NEED items (filtering out)")
        print(f"✅ {len(matching_orgs)} organizations need donor's items")
        
        print("\n📋 STEP 3: Computing scores for matching organizations...")
        # Step 3: Compute need scores for each matching organization
        scored_list = []  # Will be list of (distance, org_data, score) tuples
        for distance, org_data in matching_orgs:
            score = _compute_need_score(donor_items, org_data, distance)
            org_name = org_data.get('name', 'Unknown')
            print(f"   📊 {org_name} - Score: {score:.2f}")
            scored_list.append((distance, org_data, score))
        
        print("\n📋 STEP 4: Sorting by score (highest first)...")
        # Step 4: Sort by need score (highest need first)
        sorted_list = sorted(scored_list, key=lambda x: x[2], reverse=True)
        print(f"✅ Sorted {len(sorted_list)} organizations")
        
    else:
        # No donor items - retrieve all organizations and sort by distance
        # All organizations get perfect score of 100 (no filtering applied)
        org_type = {"shelter": True, "charity": True}
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        sorted_list = [(dist, org, 100) for dist, org in organizations_list]
    
    print("\n📋 FINAL: Converting to ranked dictionary...")
    # Convert sorted list to dictionary with integer keys based on rank
    # Add score to each organization object
    ranked_orgs = {}
    for i, (distance, org_data, score) in enumerate(sorted_list, 1):
        # Create a copy of org_data and add the score
        org_with_score = org_data.copy()
        org_with_score["score"] = int(round(score))  # Always round to integer
        ranked_orgs[i] = org_with_score
        print(f"   Rank {i}: {org_with_score.get('name', 'Unknown')} - Score: {org_with_score['score']}")
    
    print(f"\n✅ RETURNING {len(ranked_orgs)} ranked organizations")
    print("="*80 + "\n")
    return ranked_orgs


def _organization_needs_items(donor_items: dict, organization: dict) -> bool:
    """
    Check if organization needs any of the items the donor has.
    
    Args:
        donor_items: Dictionary of items donor wants to donate
            Example: {
                "items": [
                    {"category": "food", "item": "canned beans", "quantity": 50},
                    {"category": "clothing", "item": "jackets", "quantity": 20}
                ]
            }
        organization: Organization data with needs
        
    Returns:
        bool: True if organization needs any of the donor's items
    """
    org_name = organization.get("name", "Unknown")
    donor_item_list = donor_items.get("items", [])
    org_needs = organization.get("needs", {})
    
    print(f"\n      🔍 Checking {org_name}...")
    print(f"         Donor categories: {[item.get('category', '').lower() for item in donor_item_list]}")
    print(f"         Org has {len(org_needs)} need items")
    
    if not donor_item_list or not org_needs:
        print(f"         ❌ No donor items or org has no needs")
        return False
    
    # Check if any donor item matches a category the org needs
    for donor_item in donor_item_list:
        donor_category = donor_item.get("category", "").lower()
        print(f"         Checking donor category: '{donor_category}'")
        
        # Check if org has any needs in this category with a gap (needed > have)
        for item_name, item_data in org_needs.items():
            org_category = item_data.get("category", "").lower()
            needed = item_data.get("needed", 0)
            have = item_data.get("have", 0)
            gap = needed - have
            
            print(f"            Checking item: {item_name}")
            print(f"               Org category: '{org_category}' vs Donor category: '{donor_category}'")
            print(f"               Match? {org_category == donor_category}")
            
            if org_category == donor_category:
                print(f"            📦 CATEGORY MATCH! Item: {item_name}")
                print(f"            📊 GAP CALCULATION:")
                print(f"               needed (type={type(needed).__name__}): {needed}")
                print(f"               have (type={type(have).__name__}): {have}")
                print(f"               gap = needed - have = {needed} - {have} = {gap}")
                print(f"               Checking: {needed} > {have} = {needed > have}")
                
                if needed > have:
                    print(f"            ✅ GAP CHECK PASSED! Org NEEDS this category (gap={gap} > 0)")
                    return True  # Org needs items in this category
                else:
                    print(f"            ❌ GAP CHECK FAILED! Org has enough (gap={gap} <= 0)")
    
    print(f"         ❌ No matching categories with gaps")
    return False


def _compute_need_score(donor_items: dict, organization: dict, distance_miles: float) -> float:
    """
    Compute need score based on urgency, gap size, and distance (0-100 scale).
    Higher score = organization needs these items more urgently.
    
    Scoring components:
    - Urgency score (40%): How urgent is the organization's need?
    - Gap score (35%): How big is the gap between needed and have?
    - Distance score (25%): How close is the donor?
    
    Args:
        donor_items: Items donor wants to donate
        organization: Organization data with needs
        distance_miles: Pre-calculated distance in miles
        
    Returns:
        float: Score from 0-100 (100 = highest need)
    """
    urgency_score = _calculate_urgency_score(donor_items, organization)
    gap_score = _calculate_gap_score(donor_items, organization)
    distance_score = _calculate_distance_score(distance_miles)
    
    total = (
        urgency_score * 0.40 +   # Urgency is most important
        gap_score * 0.35 +        # Gap size is second most important
        distance_score * 0.25     # Distance is least important for donations
    )
    
    return round(total * 100, 2)


def _calculate_urgency_score(donor_items: dict, organization: dict) -> float:
    """
    Calculate urgency score based on organization's urgency levels (0-1 scale).
    
    Looks at the urgency of items the org needs in categories donor has.
    
    Args:
        donor_items: Items donor wants to donate
        organization: Organization data with needs
        
    Returns:
        float: Score from 0-1 (1 = highest urgency)
    """
    donor_item_list = donor_items.get("items", [])
    org_needs = organization.get("needs", {})
    
    urgency_map = {
        "high": 1.0,
        "medium": 0.6,
        "low": 0.3
    }
    
    matching_urgencies = []
    
    # Find urgency levels for items in categories donor has
    for donor_item in donor_item_list:
        donor_category = donor_item.get("category", "").lower()
        
        for item_name, item_data in org_needs.items():
            org_category = item_data.get("category", "").lower()
            
            if org_category == donor_category:
                urgency = item_data.get("urgency", "low").lower()
                urgency_score = urgency_map.get(urgency, 0.3)
                matching_urgencies.append(urgency_score)
    
    if not matching_urgencies:
        return 0.0  # No matching categories
    
    # Return the highest urgency (most urgent need)
    return max(matching_urgencies)


def _calculate_gap_score(donor_items: dict, organization: dict) -> float:
    """
    Calculate gap score based on how much organization needs vs has (0-1 scale).
    
    Bigger gap = higher score = more need.
    
    Args:
        donor_items: Items donor wants to donate
        organization: Organization data with needs
        
    Returns:
        float: Score from 0-1 (1 = biggest gap)
    """
    donor_item_list = donor_items.get("items", [])
    org_needs = organization.get("needs", {})
    
    gap_scores = []
    
    # Calculate gap for items in categories donor has
    for donor_item in donor_item_list:
        donor_category = donor_item.get("category", "").lower()
        donor_quantity = donor_item.get("quantity", 0)
        
        for item_name, item_data in org_needs.items():
            org_category = item_data.get("category", "").lower()
            
            if org_category == donor_category:
                needed = item_data.get("needed", 0)
                have = item_data.get("have", 0)
                gap = needed - have
                
                if gap > 0:
                    # Calculate what percentage of the gap the donor can fill
                    fill_percentage = min(donor_quantity / gap, 1.0)
                    
                    # Calculate gap severity (how big is the gap relative to need)
                    gap_severity = gap / needed if needed > 0 else 0
                    
                    # Combine: reward both large gaps and donor's ability to fill them
                    gap_score = (gap_severity * 0.6) + (fill_percentage * 0.4)
                    gap_scores.append(gap_score)
    
    if not gap_scores:
        return 0.0  # No gaps found
    
    # Return the average gap score across all matching categories
    return sum(gap_scores) / len(gap_scores)


def _calculate_distance_score(distance_miles: float) -> float:
    """
    Convert distance in miles to a score (0-1 scale).
    Closer distance = higher score.
    
    Args:
        distance_miles: Pre-calculated distance in miles
        
    Returns:
        float: Score from 0-1 (1 = closest, 0 = farthest)
    """
    # For donations, distance is less critical, so we're more lenient
    # 0 miles = 1.0 (perfect)
    # 50+ miles = 0.0 (worst)
    max_reasonable_distance = 50.0
    
    if distance_miles <= 0:
        return 1.0
    elif distance_miles >= max_reasonable_distance:
        return 0.0
    else:
        # Linear decay: closer = better
        return 1.0 - (distance_miles / max_reasonable_distance)


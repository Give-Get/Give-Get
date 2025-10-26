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
    if donor_items:
        # Step 1: Retrieve all organizations (both shelters and charities can receive donations)
        org_type = {"shelter": True, "charity": True}
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        
        # Step 2: Filter to organizations that need the donor's items
        matching_orgs = []  # Will store: [(distance, org_data), ...]
        for distance, org_data in organizations_list:
            if _organization_needs_items(donor_items, org_data):
                matching_orgs.append((distance, org_data))
        
        # Step 3: Compute need scores for each matching organization
        scored_list = []  # Will be list of (distance, org_data, score) tuples
        for distance, org_data in matching_orgs:
            score = _compute_need_score(donor_items, org_data, distance)
            scored_list.append((distance, org_data, score))
        
        # Step 4: Sort by need score (highest need first)
        sorted_list = sorted(scored_list, key=lambda x: x[2], reverse=True)
        
    else:
        # No donor items - retrieve all organizations and sort by distance
        # All organizations get perfect score of 100 (no filtering applied)
        org_type = {"shelter": True, "charity": True}
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        sorted_list = [(dist, org, 100) for dist, org in organizations_list]
    
    # Convert sorted list to dictionary with integer keys based on rank
    # Add score to each organization object
    ranked_orgs = {}
    for i, (distance, org_data, score) in enumerate(sorted_list, 1):
        # Create a copy of org_data and add the score
        org_with_score = org_data.copy()
        org_with_score["score"] = int(round(score))  # Always round to integer
        ranked_orgs[i] = org_with_score
    
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
    donor_item_list = donor_items.get("items", [])
    org_needs = organization.get("needs", {})
    
    if not donor_item_list or not org_needs:
        return False
    
    # Check if any donor item matches a category the org needs
    for donor_item in donor_item_list:
        donor_category = donor_item.get("category", "").lower()
        
        # Check if org has any needs in this category with a gap (needed > have)
        for item_name, item_data in org_needs.items():
            org_category = item_data.get("category", "").lower()
            needed = item_data.get("needed", 0)
            have = item_data.get("have", 0)
            
            if org_category == donor_category and needed > have:
                return True  # Org needs items in this category
    
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


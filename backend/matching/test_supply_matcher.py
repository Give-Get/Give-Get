"""
test_supply_matcher.py

Test file for supply_matcher.py functionality.
Mocks the missing database import and tests donation matching.
"""

import sys
sys.path.insert(0, '/Users/arshawn/Desktop/GiveAndGet/Give-Get/backend/matching')

# Mock the database function
def mock_get_orgs_within_radius(location, radius, org_type):
    """
    Mock database function - returns test organizations with distances.
    
    Returns: [(distance_miles, organization_dict), ...] sorted by distance
    """
    import math
    
    def calculate_distance(loc1, loc2):
        """Calculate Haversine distance"""
        R = 3959.0
        lat1 = math.radians(loc1.get("lat", 0))
        lon1 = math.radians(loc1.get("lng", 0))
        lat2 = math.radians(loc2.get("lat", 0))
        lon2 = math.radians(loc2.get("lng", 0))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return round(R * c, 2)
    
    # Test organizations with needs
    food_bank = {
        "type": {"shelter": False, "charity": True},
        "name": "Centre County Food Bank",
        "location": {"lat": 40.7950, "lng": -77.8650},
        "ammenities": {},
        "quality_rating": 4.8,
        "needs": {
            "canned_beans": {"category": "food", "needed": 200, "have": 150, "urgency": "high"},
            "rice": {"category": "food", "needed": 100, "have": 80, "urgency": "high"},
            "pasta": {"category": "food", "needed": 150, "have": 20, "urgency": "high"}
        }
    }
    
    shelter = {
        "type": {"shelter": True, "charity": False},
        "name": "Safe Haven Shelter",
        "location": {"lat": 40.7934, "lng": -77.8600},
        "ammenities": {},
        "quality_rating": 4.5,
        "needs": {
            "blankets": {"category": "bedding", "needed": 50, "have": 10, "urgency": "high"},
            "pillows": {"category": "bedding", "needed": 40, "have": 35, "urgency": "low"}
        }
    }
    
    clothing_drive = {
        "type": {"shelter": False, "charity": True},
        "name": "Community Clothing Drive",
        "location": {"lat": 40.7900, "lng": -77.8550},
        "ammenities": {},
        "quality_rating": 3.5,
        "needs": {
            "jackets": {"category": "clothing", "needed": 50, "have": 5, "urgency": "high"},
            "shirts": {"category": "clothing", "needed": 100, "have": 10, "urgency": "medium"},
            "pants": {"category": "clothing", "needed": 80, "have": 75, "urgency": "low"}
        }
    }
    
    toy_drive = {
        "type": {"shelter": False, "charity": True},
        "name": "Holiday Toy Drive",
        "location": {"lat": 40.8000, "lng": -77.8700},
        "ammenities": {},
        "quality_rating": 4.0,
        "needs": {
            "toys": {"category": "toys", "needed": 200, "have": 50, "urgency": "medium"},
            "books": {"category": "toys", "needed": 100, "have": 90, "urgency": "low"}
        }
    }
    
    # Return based on org_type filter
    all_orgs = [
        ("food_bank", food_bank),
        ("shelter", shelter),
        ("clothing_drive", clothing_drive),
        ("toy_drive", toy_drive)
    ]
    
    # Filter by type and calculate distances
    filtered_orgs_with_distance = []
    for org_id, org_data in all_orgs:
        org_type_data = org_data.get("type", {})
        
        # Check if this org matches the requested type
        should_include = False
        if org_type.get("shelter") and org_type_data.get("shelter"):
            should_include = True
        elif org_type.get("charity") and org_type_data.get("charity"):
            should_include = True
        
        if should_include:
            # Calculate distance
            org_location = org_data.get("location", {})
            distance = calculate_distance(location, org_location)
            filtered_orgs_with_distance.append((distance, org_data))
    
    # Sort by distance (ascending)
    filtered_orgs_with_distance.sort(key=lambda x: x[0])
    
    print(f"[MOCK] get_orgs_within_radius returned {len(filtered_orgs_with_distance)} organizations")
    return filtered_orgs_with_distance


# Inject mock into the module namespace
import supply_matcher
supply_matcher.get_orgs_within_radius = mock_get_orgs_within_radius

# Now we can safely import everything
from supply_matcher import (
    sort_organizations_by_need,
    _organization_needs_items,
    _compute_need_score,
    _calculate_urgency_score,
    _calculate_gap_score,
    _calculate_distance_score
)


# ==================== TEST DATA ====================

TEST_LOCATION = {"lat": 40.7930, "lng": -77.8600}  # State College, PA

# Donor with food items
donor_with_food = {
    "location": TEST_LOCATION,
    "items": [
        {"category": "food", "item": "canned beans", "quantity": 100},
        {"category": "food", "item": "rice", "quantity": 50}
    ]
}

# Donor with clothing
donor_with_clothing = {
    "location": TEST_LOCATION,
    "items": [
        {"category": "clothing", "item": "jackets", "quantity": 30},
        {"category": "clothing", "item": "shirts", "quantity": 20}
    ]
}

# Donor with mix of items
donor_with_mix = {
    "location": TEST_LOCATION,
    "items": [
        {"category": "food", "item": "pasta", "quantity": 200},
        {"category": "clothing", "item": "jackets", "quantity": 50},
        {"category": "bedding", "item": "blankets", "quantity": 25}
    ]
}

# Donor with items nobody needs
donor_with_toys = {
    "location": TEST_LOCATION,
    "items": [
        {"category": "electronics", "item": "old phones", "quantity": 10}
    ]
}


# ==================== TEST FUNCTIONS ====================

def test_organization_needs_check():
    """Test checking if organizations need donor's items"""
    print("\n" + "="*70)
    print("TEST: Organization Needs Checking")
    print("="*70)
    
    # Get test organizations
    orgs_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": True})
    food_bank = orgs_list[0][1]  # Food bank should be first (closest)
    
    print("\n1. Food Bank needs food items:")
    needs_food = _organization_needs_items(donor_with_food, food_bank)
    print(f"   Needs food: {needs_food}")
    
    print("\n2. Food Bank needs clothing:")
    needs_clothing = _organization_needs_items(donor_with_clothing, food_bank)
    print(f"   Needs clothing: {needs_clothing}")


def test_scoring_components():
    """Test individual scoring components"""
    print("\n" + "="*70)
    print("TEST: Scoring Components")
    print("="*70)
    
    orgs_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": True})
    food_bank_distance, food_bank = orgs_list[0]
    
    # Test urgency score
    print("\n1. Urgency Score (Food Bank needs food urgently):")
    urgency = _calculate_urgency_score(donor_with_food, food_bank)
    print(f"   Urgency: {urgency:.2f}/1.0")
    
    # Test gap score
    print("\n2. Gap Score (How big is the need gap?):")
    gap = _calculate_gap_score(donor_with_food, food_bank)
    print(f"   Gap: {gap:.2f}/1.0")
    
    # Test distance score
    print("\n3. Distance Score:")
    distance_score = _calculate_distance_score(food_bank_distance)
    print(f"   Distance ({food_bank_distance} mi): {distance_score:.2f}/1.0")


def test_overall_need_scoring():
    """Test overall need scoring"""
    print("\n" + "="*70)
    print("TEST: Overall Need Scoring")
    print("="*70)
    
    orgs_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": True})
    food_bank_distance, food_bank = orgs_list[0]
    
    print("\n1. Food Bank need score for food donation:")
    score = _compute_need_score(donor_with_food, food_bank, food_bank_distance)
    print(f"   Total Score: {score}/100")


def test_full_pipeline_food_donation():
    """Test the full matching pipeline for food donations"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline - Food Donation")
    print("="*70)
    
    print("\n1. Donor with 100 canned beans + 50 rice:")
    results = sort_organizations_by_need(TEST_LOCATION, 25, donor_with_food)
    print(f"   Matches found: {len(results)}")
    if len(results) > 0:
        print(f"\n   Ranked Dictionary Output:")
        import json
        print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
        print(f"\n   Details:")
        for rank, org_data in results.items():
            org_name = org_data.get("name", "Unknown")
            org_score = org_data.get("score", "N/A")
            print(f"      Rank {rank}: {org_name} (Need Score: {org_score}/100)")


def test_full_pipeline_clothing_donation():
    """Test the full matching pipeline for clothing donations"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline - Clothing Donation")
    print("="*70)
    
    print("\n1. Donor with 30 jackets + 20 shirts:")
    results = sort_organizations_by_need(TEST_LOCATION, 25, donor_with_clothing)
    print(f"   Matches found: {len(results)}")
    if len(results) > 0:
        print(f"\n   Ranked Dictionary Output:")
        import json
        print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
        print(f"\n   Details:")
        for rank, org_data in results.items():
            org_name = org_data.get("name", "Unknown")
            org_score = org_data.get("score", "N/A")
            print(f"      Rank {rank}: {org_name} (Need Score: {org_score}/100)")


def test_full_pipeline_mixed_donation():
    """Test the full matching pipeline for mixed donations"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline - Mixed Donation")
    print("="*70)
    
    print("\n1. Donor with pasta, jackets, and blankets:")
    results = sort_organizations_by_need(TEST_LOCATION, 25, donor_with_mix)
    print(f"   Matches found: {len(results)}")
    if len(results) > 0:
        print(f"\n   Ranked Dictionary Output:")
        import json
        print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
        print(f"\n   Details:")
        for rank, org_data in results.items():
            org_name = org_data.get("name", "Unknown")
            org_score = org_data.get("score", "N/A")
            print(f"      Rank {rank}: {org_name} (Need Score: {org_score}/100)")


def test_no_items():
    """Test distance-only search without donor items"""
    print("\n" + "="*70)
    print("TEST: Distance-Only Search (No Donor Items)")
    print("="*70)
    
    print("\n1. Getting all organizations sorted by distance:")
    results = sort_organizations_by_need(TEST_LOCATION, 25, donor_items=None)
    print(f"   Organizations found: {len(results)}")
    print(f"\n   Ranked Dictionary Output:")
    import json
    print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
    print(f"\n   Details (all get score of 100):")
    for rank, org_data in results.items():
        org_name = org_data.get("name", "Unknown")
        score = org_data.get("score", "N/A")
        print(f"      Rank {rank}: {org_name} - Score: {score}/100")


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPPLY MATCHER TEST SUITE")
    print("="*70)
    
    test_organization_needs_check()
    test_scoring_components()
    test_overall_need_scoring()
    test_full_pipeline_food_donation()
    test_full_pipeline_clothing_donation()
    test_full_pipeline_mixed_donation()
    test_no_items()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")


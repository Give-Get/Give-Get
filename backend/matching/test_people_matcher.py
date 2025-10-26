"""
test_people_matcher.py

Test file for people_matcher.py functionality.
Mocks the missing imports (get_orgs_within_radius, sort_by_match_score)
"""

import sys
sys.path.insert(0, '/Users/arshawn/Desktop/GiveAndGet/Give-Get/backend/matching')

# Mock the missing imports before importing people_matcher
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
    
    # Test shelter
    shelter_1 = {
        "type": {"shelter": True, "charity": False},
        "name": "Safe Haven Shelter",
        "location": {"lat": 40.7934, "lng": -77.8600},  # ~0.2 miles from test location
        "ammenities": {
            "accessible": True,
            "pet_friendly": True,
            "lgbtq_only": False,
            "male_only": False,
            "female_only": False,
            "all_gender": True,
            "languages": ["english", "spanish"],
            "family_rooming": True,
            "beds_available": 15,
            "medical_support": True,
            "counseling_support": True,
            "provides_meals": True,
            "showers": True,
            "fees": 0,
            "age_minimum": 18,
            "age_maximum": 65,
            "veteran_only": False,
            "immigrant_only": False,
            "refugee_only": False,
            "good_criminal_record_standing": False,
            "sobriety_required": False,
            "id_required": False,
            "max_stay_days": 90
        },
        "quality_rating": 4.5,
        "needs": {}
    }
    
    shelter_2 = {
        "type": {"shelter": True, "charity": False},
        "name": "Veterans Only Shelter",
        "location": {"lat": 40.8000, "lng": -77.8700},  # ~1 mile from test location
        "ammenities": {
            "accessible": False,
            "pet_friendly": False,
            "lgbtq_only": False,
            "male_only": True,
            "female_only": False,
            "all_gender": False,
            "languages": ["english"],
            "family_rooming": False,
            "beds_available": 5,
            "medical_support": False,
            "counseling_support": False,
            "provides_meals": False,
            "showers": True,
            "fees": 10,
            "age_minimum": 18,
            "age_maximum": None,
            "veteran_only": True,
            "immigrant_only": False,
            "refugee_only": False,
            "good_criminal_record_standing": True,
            "sobriety_required": True,
            "id_required": True,
            "max_stay_days": 30
        },
        "quality_rating": 3.0,
        "needs": {}
    }
    
    # Test charity
    charity_1 = {
        "type": {"shelter": False, "charity": True},
        "name": "Centre County Food Bank",
        "location": {"lat": 40.7950, "lng": -77.8650},  # ~0.5 miles from test location
        "ammenities": {},
        "quality_rating": 4.8,
        "needs": {
            "canned_beans": {"category": "food", "needed": 200, "have": 150, "urgency": "high"},
            "rice": {"category": "food", "needed": 100, "have": 80, "urgency": "medium"},
            "jackets": {"category": "clothing", "needed": 50, "have": 30, "urgency": "low"},
            "bandages": {"category": "medical", "needed": 30, "have": 25, "urgency": "medium"}
        }
    }
    
    charity_2 = {
        "type": {"shelter": False, "charity": True},
        "name": "Community Clothing Drive",
        "location": {"lat": 40.7900, "lng": -77.8550},  # ~0.3 miles from test location
        "ammenities": {},
        "quality_rating": 3.5,
        "needs": {
            "shirts": {"category": "clothing", "needed": 100, "have": 5, "urgency": "high"},
            "pants": {"category": "clothing", "needed": 80, "have": 10, "urgency": "high"}
        }
    }
    
    # Return based on org_type filter
    all_orgs = [
        ("shelter_1", shelter_1),
        ("shelter_2", shelter_2),
        ("charity_1", charity_1),
        ("charity_2", charity_2)
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


# Inject mocks into the module namespace
import people_matcher
people_matcher.get_orgs_within_radius = mock_get_orgs_within_radius

# Now we can safely import everything
from people_matcher import (
    sort_shelters_by_score,
    feasibility_check,
    _compute_organization_score,
    _calculate_urgency_score,
    _calculate_distance_score,
    _calculate_fit_score,
    _calculate_capacity_score,
    _calculate_charity_stock_score
)


# ==================== TEST DATA ====================

TEST_LOCATION = {"lat": 40.7930, "lng": -77.8600}  # State College, PA

# Person needing housing - good fit for Safe Haven Shelter
person_housing_good_fit = {
    "needs_housing": True,
    "location": TEST_LOCATION,
    "beds_needed": 2,
    "needs_handicapped_access": True,
    "owns_pets": True,
    "days_homeless": 45,
    "preferred_duration_days": 60,
    
    # Preferences
    "prefers_family_rooming": True,
    "can_pay_fees": False,
    "max_affordable_fee": 0,
    "lgbtq_identity": False,
    "prefers_medical_support": True,
    "prefers_counseling": True,
    "prefers_meals_provided": True,
    "prefers_showers": True,
    "duration_flexibility": "flexible",
    
    # Demographics
    "urgency_level": "immediate",
    "max_travel_distance_miles": 25,
    "gender": "male",
    "age": 35,
    "language": "english",
    "veteran_status": "no",
    "criminal_record": "no",
    "sobriety": "no",
    "has_id": True
}

# Person needing housing - would only match Veterans shelter
person_veteran = {
    "needs_housing": True,
    "location": TEST_LOCATION,
    "beds_needed": 1,
    "needs_handicapped_access": False,
    "owns_pets": False,
    "days_homeless": 10,
    
    "prefers_family_rooming": False,
    "can_pay_fees": True,
    "max_affordable_fee": 15,
    
    "urgency_level": "within_week",
    "max_travel_distance_miles": 25,
    "gender": "male",
    "age": 45,
    "language": "english",
    "veteran_status": "yes",
    "criminal_record": "no",
    "sobriety": "yes",
    "has_id": True
}

# Person needing resources from charity
person_charity_needs = {
    "needs_housing": False,
    "location": TEST_LOCATION,
    
    # Resource needs
    "needs_food": True,
    "needs_clothing": True,
    "needs_medical": False,
    "needs_mental_health": False,
    
    # Demographics
    "urgency_level": "immediate",
    "max_travel_distance_miles": 25,
    "gender": "female",
    "age": 28,
    "language": "spanish"
}


# ==================== TEST FUNCTIONS ====================

def test_feasibility_check():
    """Test feasibility checking for various scenarios"""
    print("\n" + "="*70)
    print("TEST: Feasibility Checking")
    print("="*70)
    
    # Get test shelter
    orgs_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": False})
    shelter = orgs_list[0][1]  # Get first org from (distance, org) tuple
    
    # Test 1: Good fit person
    print("\n1. Testing person with good fit for Safe Haven Shelter:")
    result = feasibility_check(person_housing_good_fit, shelter)
    print(f"   Is Feasible: {result['is_feasible']}")
    print(f"   Constraints Passed: {len(result['constraints_passed'])}")
    print(f"   Constraints Failed: {len(result['constraints_failed'])}")
    if result['failure_reasons']:
        print(f"   Failure Reasons: {result['failure_reasons']}")
    
    # Test 2: Person requiring more beds than available
    print("\n2. Testing person needing 20 beds (shelter only has 15):")
    person_too_many_beds = person_housing_good_fit.copy()
    person_too_many_beds["beds_needed"] = 20
    result = feasibility_check(person_too_many_beds, shelter)
    print(f"   Is Feasible: {result['is_feasible']}")
    if result['failure_reasons']:
        print(f"   Failure Reasons: {result['failure_reasons']}")
    
    # Test 3: Veteran matching
    print("\n3. Testing veteran against Veterans Only Shelter:")
    vet_orgs_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": False})
    vet_shelter = vet_orgs_list[1][1]  # Get second org (Veterans shelter)
    result = feasibility_check(person_veteran, vet_shelter)
    print(f"   Is Feasible: {result['is_feasible']}")
    print(f"   Constraints Passed: {len(result['constraints_passed'])}")


def test_scoring_components():
    """Test individual scoring components"""
    print("\n" + "="*70)
    print("TEST: Scoring Components")
    print("="*70)
    
    shelter_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": False})
    charity_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": False, "charity": True})
    
    shelter_distance, shelter = shelter_list[0]  # Unpack (distance, org)
    charity_distance, charity = charity_list[0]
    
    # Test urgency score
    print("\n1. Urgency Scores:")
    urgency_immediate = _calculate_urgency_score(person_housing_good_fit)
    urgency_week = _calculate_urgency_score(person_veteran)
    print(f"   Immediate urgency (45 days homeless): {urgency_immediate:.2f}")
    print(f"   Within week (10 days homeless): {urgency_week:.2f}")
    
    # Test distance score
    print("\n2. Distance Scores:")
    distance_shelter_score = _calculate_distance_score(shelter_distance)
    distance_charity_score = _calculate_distance_score(charity_distance)
    print(f"   Distance to Safe Haven Shelter ({shelter_distance} mi): {distance_shelter_score:.2f}")
    print(f"   Distance to Food Bank ({charity_distance} mi): {distance_charity_score:.2f}")
    
    # Test fit score
    print("\n3. Fit Scores:")
    fit_shelter = _calculate_fit_score(person_housing_good_fit, shelter)
    fit_charity = _calculate_fit_score(person_charity_needs, charity)
    print(f"   Shelter fit (many preferences matched): {fit_shelter:.2f}")
    print(f"   Charity fit (has food + clothing): {fit_charity:.2f}")
    
    # Test capacity score
    print("\n4. Capacity Score:")
    capacity = _calculate_capacity_score(person_housing_good_fit, shelter)
    print(f"   Shelter capacity (15 beds available): {capacity:.2f}")
    
    # Test stock score
    print("\n5. Charity Stock Score:")
    stock = _calculate_charity_stock_score(person_charity_needs, charity)
    print(f"   Charity stock availability: {stock:.2f}")


def test_overall_scoring():
    """Test overall scoring for different scenarios"""
    print("\n" + "="*70)
    print("TEST: Overall Organization Scoring")
    print("="*70)
    
    shelter_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": True, "charity": False})
    charity_list = mock_get_orgs_within_radius(TEST_LOCATION, 25, {"shelter": False, "charity": True})
    
    shelter_distance, shelter = shelter_list[0]
    charity_distance, charity = charity_list[0]
    
    print("\n1. Housing Match Score (Safe Haven Shelter):")
    score_housing = _compute_organization_score(person_housing_good_fit, shelter, shelter_distance)
    print(f"   Total Score: {score_housing}/100")
    
    print("\n2. Charity Match Score (Food Bank):")
    score_charity = _compute_organization_score(person_charity_needs, charity, charity_distance)
    print(f"   Total Score: {score_charity}/100")


def test_full_pipeline_housing():
    """Test the full matching pipeline for housing needs"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline - Housing Search")
    print("="*70)
    
    print("\n1. Person with pets, needs accessibility, prefers family rooming:")
    results = sort_shelters_by_score(TEST_LOCATION, 25, person_housing_good_fit)
    print(f"   Matches found: {len(results)}")
    print(f"\n   Ranked Dictionary Output:")
    import json
    print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
    print(f"\n   Details:")
    for rank, org_data in results.items():
        org_name = org_data.get("name", "Unknown")
        org_score = org_data.get("score", "N/A")
        print(f"      Rank {rank}: {org_name} (Score: {org_score}/100)")
    
    print("\n2. Veteran with sobriety looking for shelter:")
    results = sort_shelters_by_score(TEST_LOCATION, 25, person_veteran)
    print(f"   Matches found: {len(results)}")
    print(f"\n   Ranked Dictionary Output:")
    print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
    print(f"\n   Details:")
    for rank, org_data in results.items():
        org_name = org_data.get("name", "Unknown")
        org_score = org_data.get("score", "N/A")
        print(f"      Rank {rank}: {org_name} (Score: {org_score}/100)")


def test_full_pipeline_charity():
    """Test the full matching pipeline for charity needs"""
    print("\n" + "="*70)
    print("TEST: Full Pipeline - Charity/Resource Search")
    print("="*70)
    
    print("\n1. Person needing food and clothing:")
    results = sort_shelters_by_score(TEST_LOCATION, 25, person_charity_needs)
    print(f"   Matches found: {len(results)}")
    if len(results) > 0:
        print(f"\n   Ranked Dictionary Output:")
        import json
        print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'score': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
        print(f"\n   Details:")
        for rank, org_data in results.items():
            org_name = org_data.get("name", "Unknown")
            org_score = org_data.get("score", "N/A")
            print(f"      Rank {rank}: {org_name} (Score: {org_score}/100)")
    else:
        print(f"   No matches found (check constraints)")


def test_no_filters():
    """Test distance-only search without person filters"""
    print("\n" + "="*70)
    print("TEST: Distance-Only Search (No Person Filters)")
    print("="*70)
    
    print("\n1. Getting all organizations sorted by distance:")
    results = sort_shelters_by_score(TEST_LOCATION, 25, person_filters=None)
    print(f"   Organizations found: {len(results)}")
    print(f"\n   Ranked Dictionary Output:")
    import json
    print(f"   {json.dumps({k: {'name': v.get('name', 'Unknown'), 'distance': v.get('score', 0)} for k, v in results.items()}, indent=6)}")
    print(f"\n   Details (sorted by distance - closest first):")
    for rank, org_data in results.items():
        org_name = org_data.get("name", "Unknown")
        org_type = org_data.get("type", {})
        type_str = "Shelter" if org_type.get("shelter") else "Charity"
        distance = org_data.get("score", "N/A")  # In this case, score = distance
        print(f"      Rank {rank}: {org_name} ({type_str}) - {distance} miles")


# ==================== RUN ALL TESTS ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PEOPLE MATCHER TEST SUITE")
    print("="*70)
    
    test_feasibility_check()
    test_scoring_components()
    test_overall_scoring()
    test_full_pipeline_housing()
    test_full_pipeline_charity()
    test_no_filters()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")


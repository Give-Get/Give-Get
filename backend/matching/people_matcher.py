"""
people_matcher.py

Matches people/families to shelters in real-time.

Main function: match_person_to_shelters(person, shelters)
- Takes one person dict and list of shelter dicts
- Returns best matches with scores and explanations
- Returns results in <2 seconds for real-time experience

"""

# Import database function
import sys
import os
# Add parent directory to path to import db module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_orgs_within_radius

def sort_shelters_by_score(location: dict, radius: int, person_filters: dict = None) -> list[tuple]:
    """
    Main function: Retrieves organizations, scores them, and returns sorted by score.
    
    Flow:
    - If person_filters provided: 
        1. Determine org type based on needs_housing
        2. Retrieve matching organizations from database (with distances)
        3. Filter to feasible matches only
        4. Compute score for each feasible match (using pre-calculated distance)
        5. Sort by score (highest first)
    - If no person_filters:
        1. Retrieve all organizations (shelters + charities)
        2. Already sorted by distance from database
    
    Args:
        location: {"lat": float, "lng": float} - Required location
        radius: int - Search radius in miles
        person_filters: dict (optional) - Person's needs and preferences
        
    Returns:
        list[tuple]: Sorted list of (distance_miles, organization_dict, score)
        - If person_filters provided: sorted by score (highest first)
        - If no person_filters: sorted by distance (closest first)
    """
    if person_filters:
        # Step 1: Determine organization type based on person's needs
        needs_housing = person_filters.get("needs_housing", False)
        if needs_housing:
            org_type = {"shelter": True, "charity": False}
        else:
            org_type = {"shelter": False, "charity": True}
        
        # Step 2: Retrieve organizations from database
        # Returns: [(distance_miles, organization_dict), ...]
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        
        # Step 3: Filter to feasible organizations only
        feasible_orgs = []  # Will store: [(distance, org_data), ...]
        for distance, org_data in organizations_list:
            result = feasibility_check(person_filters, org_data)
            if result["is_feasible"]:
                feasible_orgs.append((distance, org_data))
        
        # Step 4: Compute scores for each feasible organization
        scored_list = []  # Will be list of (distance, org_data, score) tuples
        for distance, org_data in feasible_orgs:
            score = _compute_organization_score(person_filters, org_data, distance)
            scored_list.append((distance, org_data, score))
        
        # Step 5: Sort by score (highest to lowest)
        sorted_list = sorted(scored_list, key=lambda x: x[2], reverse=True)
        
    else:
        # No person filters - retrieve all organization types, sorted by distance
        # All organizations get perfect score of 100 (no filtering applied)
        org_type = {"shelter": True, "charity": True}
        organizations_list = get_orgs_within_radius(location, radius, org_type)
        sorted_list = [(dist, org, 100) for dist, org in organizations_list]  # Score always 100

    # Convert sorted list to dictionary with integer keys based on rank
    # Add score to each organization object
    ranked_orgs = {}
    for i, (distance, org_data, score) in enumerate(sorted_list, 1):
        # Create a copy of org_data and add the score
        org_with_score = org_data.copy()
        org_with_score["score"] = int(round(score))  # Always round to integer
        ranked_orgs[i] = org_with_score
    
    return ranked_orgs


def feasibility_check(person_filters, shelter):


    """
    Expected person_filters dictionary structure:
    {
        # Core need type - determines if we match to shelters or charities
        "needs_housing": bool (required),  # True = match to shelters, False = match to charities
        
        # Location (required for distance calculation)
        "location": {"lat": float, "lng": float} (required),
        
        # Housing-specific fields (only relevant if needs_housing = true)
        "beds_needed": int (default: 1),
        "needs_handicapped_access": bool (default: False),  # HARD constraint
        "owns_pets": bool (default: False),  # HARD constraint
        "days_homeless": int (optional: for urgency boost),
        "preferred_duration_days": int (default: 30),
        
        # Housing preferences (for fit scoring, not hard constraints)
        "prefers_family_rooming": bool (default: False),
        "can_pay_fees": bool (default: False),
        "max_affordable_fee": int (default: 0),  # Max fee in dollars
        "lgbtq_identity": bool (default: False),
        "prefers_medical_support": bool (default: False),
        "prefers_counseling": bool (default: False),
        "prefers_meals_provided": bool (default: False),
        "prefers_showers": bool (default: False),
        "duration_flexibility": str (default: "flexible"),  # "flexible" or "fixed"
        
        # General fields
        "urgency_level": str (required: "immediate", "within_week", "within_month"),
        "max_travel_distance_miles": int (default: 25),
        "gender": str (required: "male", "female", "other"),
        "age": int (required: 18-65),
        "language": str (default: "english"),
        "immigration_status": str (optional: "citizen", "permanent_resident", "temporary_resident", "refugee", "other"),
        "veteran_status": str (default: "no"),
        "criminal_record": str (default: "no"),
        "sobriety": str (default: "no"),
        
        # Resource needs (relevant for charity matching)
        "needs_food": bool (default: False),
        "needs_clothing": bool (default: False),
        "needs_medical": bool (default: False),
        "needs_mental_health": bool (default: False)
    }

    Expected organization/shelter dictionary structure (NEW FORMAT):
   {
  {
    "type": {"shelter": true, "charity": false},
    "EIN": 6,
    "name": "Shelter1",
    "address": "123 Shelter St",
    "location": { "lat": 0, "lng": 0},
    "ammenities": {
        "accessible": false,
        "lgbtq_only": false,
        "male_only": false,
        "female_only": false,
        "all_gender": false,
        "pet_friendly": false,
        "languages": ["english"],
        "family_rooming": false,
        "beds_available": 10,
        "medical_support": true,
        "counseling_support": true,
        "fees": 0,
        "age_minimum": 0,
        "age_maximum": 18,
        "veteran_only": true,
        "immigrant_only": true,
        "refugee_only": true,
        "good_criminal_record_standing": false,
        "sobriety_required": true,
        "showers": true,
        "id_required": false
    },

    Output:
    {
        "is_feasible": bool,
        "constraints_passed": list[str],
        "constraints_failed": list[str],
        "failure_reasons": list[str],
    """
    passed_constraints = []
    failed_constraints = []
    failure_reasons = []

    # Define all constraints as a list of rules
    # Each rule: (name, check_function, failure_message_function)
    # Note: Using new nested structure with 'ammenities' key
    # NOTE: Organization type filtering already handled by get_orgs_within_radius()
    constraints = [
        # ===== HOUSING-SPECIFIC CONSTRAINTS (only apply if needs_housing = True) =====
        
        # Pets constraint
        {
            "name": "pets",
            "applies": lambda p, s: p.get("needs_housing", False) and p.get("owns_pets", False),
            "passes": lambda p, s: s.get("ammenities", {}).get("pet_friendly", False),
            "failure_msg": lambda p, s: "Shelter does not allow pets"
        },
        # Wheelchair/handicapped access
        {
            "name": "wheelchair_access",
            "applies": lambda p, s: p.get("needs_housing", False) and p.get("needs_handicapped_access", False),
            "passes": lambda p, s: s.get("ammenities", {}).get("accessible", False),
            "failure_msg": lambda p, s: "Shelter is not wheelchair accessible"
        },
        # Capacity check (only for housing)
        {
            "name": "capacity",
            "applies": lambda p, s: p.get("needs_housing", False),  # Only for housing needs
            "passes": lambda p, s: p.get("beds_needed", 1) <= s.get("ammenities", {}).get("beds_available", 0),
            "failure_msg": lambda p, s: f"Not enough beds (need {p.get('beds_needed', 1)}, available {s.get('ammenities', {}).get('beds_available', 0)})"
        },
        
        # ===== GENERAL CONSTRAINTS (apply to both housing and charity needs) =====
        
        # Gender restrictions
        {
            "name": "gender",
            "applies": lambda p, s: _has_gender_restriction(s),
            "passes": lambda p, s: _check_gender_match(p, s),
            "failure_msg": lambda p, s: _get_gender_restriction_message(s)
        },
        # Age restrictions
        {
            "name": "age",
            "applies": lambda p, s: s.get("ammenities", {}).get("age_minimum") or s.get("ammenities", {}).get("age_maximum"),
            "passes": lambda p, s: _check_age_range(p, s),
            "failure_msg": lambda p, s: f"Age requirements not met (shelter: {s.get('ammenities', {}).get('age_minimum', 'N/A')}-{s.get('ammenities', {}).get('age_maximum', 'N/A')})"
        },
        # Criminal record
        {
            "name": "criminal_record",
            "applies": lambda p, s: p.get("criminal_record", "no") == "yes",
            "passes": lambda p, s: not s.get("ammenities", {}).get("good_criminal_record_standing", False),
            "failure_msg": lambda p, s: "Shelter requires good criminal record standing"
        },
        # Sobriety requirement
        {
            "name": "sobriety",
            "applies": lambda p, s: s.get("ammenities", {}).get("sobriety_required", False),
            "passes": lambda p, s: p.get("sobriety", "no") == "yes",
            "failure_msg": lambda p, s: "Shelter requires sobriety"
        },
        # ID requirement
        {
            "name": "id_requirement",
            "applies": lambda p, s: s.get("ammenities", {}).get("id_required", False),
            "passes": lambda p, s: p.get("has_id", True),
            "failure_msg": lambda p, s: "Shelter requires government-issued ID"
        },
        # Veteran priority
        {
            "name": "veteran_priority",
            "applies": lambda p, s: s.get("ammenities", {}).get("veteran_only", False),
            "passes": lambda p, s: p.get("veteran_status", "no") == "yes",
            "failure_msg": lambda p, s: "Shelter is veterans-only"
        },
        # Immigrant priority
        {
            "name": "immigrant_priority",
            "applies": lambda p, s: s.get("ammenities", {}).get("immigrant_only", False),
            "passes": lambda p, s: p.get("immigration_status", "") in ["permanent_resident", "temporary_resident", "refugee", "other"],
            "failure_msg": lambda p, s: "Shelter is for immigrants only"
        },
        # Refugee priority
        {
            "name": "refugee_priority",
            "applies": lambda p, s: s.get("ammenities", {}).get("refugee_only", False),
            "passes": lambda p, s: p.get("immigration_status", "") == "refugee",
            "failure_msg": lambda p, s: "Shelter is for refugees only"
        },
        # Language support - only for shelters (housing needs), not charities
        {
            "name": "language_support",
            "applies": lambda p, s: p.get("needs_housing", False) and p.get("language", "english").lower() != "english",
            "passes": lambda p, s: _check_language_support(p, s),
            "failure_msg": lambda p, s: f"Shelter does not have {p.get('language', 'required')} language support"
        }
    ]
    
    # Process all constraints
    for constraint in constraints:
        constraint_name = constraint["name"]
        
        # Check if constraint applies to this person/shelter combination
        if constraint["applies"](person_filters, shelter):
            # Constraint applies - check if it passes
            if constraint["passes"](person_filters, shelter):
                passed_constraints.append(constraint_name)
            else:
                failed_constraints.append(constraint_name)
                failure_reasons.append(constraint["failure_msg"](person_filters, shelter))
        else:
            # Constraint doesn't apply - automatically passes
            passed_constraints.append(constraint_name)
    
    return {
        "is_feasible": len(failed_constraints) == 0,
        "constraints_passed": passed_constraints,
        "constraints_failed": failed_constraints,
        "failure_reasons": failure_reasons
    }




def _has_gender_restriction(shelter: dict) -> bool:
    """Check if shelter has any gender restrictions."""
    ammenities = shelter.get("ammenities", {})
    return (ammenities.get("male_only", False) or 
            ammenities.get("female_only", False) or 
            ammenities.get("lgbtq_only", False))


def _check_gender_match(person: dict, shelter: dict) -> bool:
    """Check if person's gender matches shelter's restrictions (NEW FORMAT)."""
    ammenities = shelter.get("ammenities", {})
    person_gender = person.get("gender", "").lower()
    
    # Check each gender restriction type
    if ammenities.get("male_only", False):
        return person_gender in ["male", "m"]
    
    if ammenities.get("female_only", False):
        return person_gender in ["female", "f"]
    
    if ammenities.get("lgbtq_only", False):
        # Assuming person has specified lgbtq identity
        return person.get("lgbtq", False) or person_gender in ["non-binary", "other", "lgbtq"]
    
    # all_gender or no restriction
    return True


def _get_gender_restriction_message(shelter: dict) -> str:
    """Get human-readable message for gender restriction."""
    ammenities = shelter.get("ammenities", {})
    
    if ammenities.get("male_only", False):
        return "Shelter is male-only"
    if ammenities.get("female_only", False):
        return "Shelter is female-only"
    if ammenities.get("lgbtq_only", False):
        return "Shelter is LGBTQ+ only"
    
    return "Shelter has gender restrictions"


def _check_age_range(person: dict, shelter: dict) -> bool:
    """Check if person's age falls within shelter's accepted range (NEW FORMAT)."""
    person_age = person.get("age", None)
    if person_age is None:
        return False  # Can't verify without age
    
    ammenities = shelter.get("ammenities", {})
    min_age = ammenities.get("age_minimum")
    max_age = ammenities.get("age_maximum")
    
    # Handle None and 0 values
    if min_age is not None and min_age > 0 and person_age < min_age:
        return False
    if max_age is not None and max_age > 0 and person_age > max_age:
        return False
    
    return True


def _check_language_support(person: dict, shelter: dict) -> bool:
    """
    Check if shelter supports the language person needs (NEW FORMAT).
    Person specifies what language they speak/need.
    Shelter has list of languages their staff can support in ammenities.languages.
    """
    person_language = person.get("language", "english").lower()
    
    # Get shelter's supported languages from ammenities (could be a list or single string)
    ammenities = shelter.get("ammenities", {})
    shelter_languages = ammenities.get("languages", ["english"])
    
    # If shelter_languages is a string, convert to list
    if isinstance(shelter_languages, str):
        shelter_languages = [shelter_languages]
    
    # Normalize to lowercase for comparison
    shelter_languages = [lang.lower() for lang in shelter_languages]
    
    # Check if person's language is in shelter's supported languages
    return person_language in shelter_languages

def _compute_organization_score(person_filters: dict, organization: dict, distance_miles: float) -> float:
    """
    Compute organization score based on person's needs and organization's attributes (0-100 scale).
    Higher score = better match.
    
    Args:
        person_filters: Person's information including needs and preferences
        organization: Organization data including attributes
        distance_miles: Pre-calculated distance in miles from person to organization
        
    Returns:
        float: Score from 0-100 (100 = perfect match)
    """

    if person_filters.get("needs_housing", False):
        # ===== HOUSING SCORING =====
        urgency_score = _calculate_urgency_score(person_filters)
        distance_score = _calculate_distance_score(distance_miles)
        fit_score = _calculate_fit_score(person_filters, organization)
        capacity_score = _calculate_capacity_score(person_filters, organization)
        
        total = (
            urgency_score * 0.35 +
            distance_score * 0.30 +
            fit_score * 0.25 +
            capacity_score * 0.10
        )
        
    else:
        # ===== CHARITY SCORING (No urgency!) =====
        distance_score = _calculate_distance_score(distance_miles)
        fit_score = _calculate_fit_score(person_filters, organization)
        stock_score = _calculate_charity_stock_score(person_filters, organization)
        
        total = (
            distance_score * 0.40 +   # Closest is best
            fit_score * 0.35 +         # Has what I need
            stock_score * 0.25         # Has it available
        )
    
    return round(total * 100, 2)


def _calculate_urgency_score(person_filters: dict) -> float:
    """
    Calculate urgency score based on person's situation (0-1 scale).
    Higher urgency = higher score = higher priority.
    
    Args:
        person_filters: Person's information including urgency_level
        
    Returns:
        float: Score from 0-1 (1 = most urgent)
    """
    urgency_level = person_filters.get("urgency_level", "within_month")

    urgency_map = {
        "immediate": 1.0,       # Currently homeless/in crisis - highest priority
        "within_week": 0.7,     # At immediate risk - high priority
        "within_month": 0.4     # Planning ahead - medium priority
    }
    
    # Start with base score for urgency level
    base_score = urgency_map.get(urgency_level, 0.4)
    
    # BONUS: Add extra urgency for days already homeless (if housing needed)
    if person_filters.get("needs_housing", False):
        days_homeless = person_filters.get("days_homeless", 0)
        
        if days_homeless > 0:
            # Add up to 0.2 bonus points for being homeless longer
            # 30+ days homeless = maximum 0.2 bonus
            bonus = min(days_homeless / 30.0, 1.0) * 0.2
            base_score = min(base_score + bonus, 1.0)  # Cap at 1.0
    
    return base_score

def _calculate_distance_score(distance_miles: float) -> float:
    """
    Convert distance in miles to a score (0-1 scale).
    Higher distance = lower score = worse match.
    
    Args:
        distance_miles: Pre-calculated distance in miles
        
    Returns:
        float: Score from 0-1 (1 = closest, 0 = farthest)
    """
    # Convert distance to score (0-1 scale)
    # 0 miles = 1.0 (perfect)
    # 25+ miles = 0.0 (worst)
    max_reasonable_distance = 25.0
    
    if distance_miles <= 0:
        return 1.0
    elif distance_miles >= max_reasonable_distance:
        return 0.0
    else:
        # Linear decay: closer = better
        return 1.0 - (distance_miles / max_reasonable_distance)



def _calculate_fit_score(person_filters: dict, organization: dict) -> float:
    """
    Dispatcher for fit scoring - routes to shelter or charity fit calculation.
    
    SHELTERS: Quality, services, amenities (medical, meals, showers)
    CHARITIES: Do they provide the categories person needs? (food, clothing)
    """
    
    if person_filters.get("needs_housing", False):
        # === SHELTER FIT: Quality & amenities ===
        return _calculate_shelter_fit_score(person_filters, organization)
    else:
        # === CHARITY FIT: Category matching ===
        return _calculate_charity_fit_score(person_filters, organization)

def _calculate_shelter_fit_score(person_filters: dict, organization: dict) -> float:
    """
    Calculate shelter fit score based on survey preferences and shelter amenities (0-1 scale).
    
    Matches person's preferences to shelter's offerings:
    - Family rooming preference
    - Fee affordability
    - LGBTQ+ friendly
    - Medical support
    - Counseling/mental health
    - Meals provided
    - Shower facilities
    - Duration match
    - Quality rating
    
    Returns: 0-1 score (higher = better match)
    """
    points = 0.0
    max_points = 0.0
    
    ammenities = organization.get("ammenities", {})
    
    # 1. Family rooming preference (1 point)
    if person_filters.get("prefers_family_rooming", False):
        max_points += 1.0
        if ammenities.get("family_rooming", False):
            points += 1.0  # Has family rooms
        else:
            points += 0.2  # Doesn't have, minor penalty
    
    # 2. Fee affordability (1.5 points - important!)
    max_points += 1.5
    shelter_fee = ammenities.get("fees", 0)
    can_pay = person_filters.get("can_pay_fees", False)
    max_affordable = person_filters.get("max_affordable_fee", 0)
    
    if shelter_fee == 0:
        points += 1.5  # Free shelter - perfect!
    elif can_pay and shelter_fee <= max_affordable:
        points += 1.5  # Can afford it
    elif can_pay and shelter_fee <= max_affordable * 1.2:
        points += 0.8  # Slightly over budget but close
    elif not can_pay and shelter_fee > 0:
        points += 0.0  # Can't afford fees
    else:
        points += 0.3  # Too expensive
    
    # 3. LGBTQ+ friendly (0.8 points)
    if person_filters.get("lgbtq_identity", False):
        max_points += 0.8
        if ammenities.get("lgbtq_only", False) or ammenities.get("all_gender", False):
            points += 0.8  # LGBTQ-friendly
        else:
            points += 0.2  # Not specifically LGBTQ-friendly
    
    # 4. Medical support preference (0.8 points)
    if person_filters.get("prefers_medical_support", False):
        max_points += 0.8
        if ammenities.get("medical_support", False):
            points += 0.8
        else:
            points += 0.1  # Doesn't have it
    
    # 5. Counseling/mental health support (0.8 points)
    if person_filters.get("prefers_counseling", False):
        max_points += 0.8
        if ammenities.get("counseling_support", False):
            points += 0.8
        else:
            points += 0.1  # Doesn't have it
    
    # 6. Meals provided (1 point - important!)
    if person_filters.get("prefers_meals_provided", False):
        max_points += 1.0
        # Check if shelter provides meals (might be in ammenities as 'provides_meals' or inferred)
        provides_meals = ammenities.get("provides_meals", False)
        if provides_meals:
            points += 1.0
        else:
            points += 0.1  # No meals
    
    # 7. Shower facilities (0.6 points)
    if person_filters.get("prefers_showers", False):
        max_points += 0.6
        if ammenities.get("showers", False):
            points += 0.6
        else:
            points += 0.1  # No showers
    
    # 8. Duration match (1 point)
    max_points += 1.0
    preferred_duration = person_filters.get("preferred_duration_days", 30)
    max_stay = ammenities.get("max_stay_days", None)
    flexibility = person_filters.get("duration_flexibility", "flexible")
    
    if max_stay is None:
        points += 1.0  # No limit, perfect
    elif max_stay >= preferred_duration:
        points += 1.0  # Can stay long enough
    elif flexibility == "flexible" and max_stay >= preferred_duration * 0.5:
        points += 0.7  # Flexible and can stay decent time
    elif flexibility == "flexible":
        points += 0.4  # Flexible but short stay
    elif max_stay >= preferred_duration * 0.8:
        points += 0.6  # Fixed need but close enough
    else:
        points += 0.2  # Can't stay long enough
    
    # 9. Quality rating (1.5 points)
    max_points += 1.5
    quality = organization.get("quality_rating", None)
    if quality:
        points += (quality / 5.0) * 1.5  # Normalize 0-5 to 0-1.5
    else:
        points += 0.75  # Unknown quality, neutral
    
    # Normalize to 0-1
    if max_points == 0:
        return 0.5  # No preferences specified, neutral
    
    return min(points / max_points, 1.0)

def _calculate_charity_fit_score(person_filters: dict, organization: dict) -> float:

    """
    Calculate charity fit score based on whether charity has items the person needs (0-1 scale).
    
    Checks:
    1. Does charity have available items in categories person needs? (food, clothing, medical, etc.)
    2. How much stock do they currently have? (higher "have" = better)
    3. Quality rating bonus
    
    Returns: 0-1 score (higher = better match)
    """
    points = 0.0
    max_points = 0.0
    
    needs_dict = organization.get("needs", {})
    
    # Extract all categories this charity has items in
    charity_inventory = {}  # {category: total_have}
    for item_name, item_data in needs_dict.items():
        category = item_data.get("category", "").lower()
        have = item_data.get("have", 0)
        
        if category:
            if category not in charity_inventory:
                charity_inventory[category] = 0
            charity_inventory[category] += have  # Sum up all items they have in this category
    
    # Check each category person needs
    # Food
    if person_filters.get("needs_food", False):
        max_points += 1.5  # Food is critical
        if "food" in charity_inventory and charity_inventory["food"] > 0:
            # Score based on quantity available
            stock_level = charity_inventory["food"]
            stock_score = min(stock_level / 100, 1.0)  # Normalize: 100+ units = perfect
            points += 1.5 * stock_score
        else:
            points += 0.0  # No food available
    
    # Clothing
    if person_filters.get("needs_clothing", False):
        max_points += 1.0
        if "clothing" in charity_inventory and charity_inventory["clothing"] > 0:
            stock_level = charity_inventory["clothing"]
            stock_score = min(stock_level / 50, 1.0)  # Normalize: 50+ units = perfect
            points += 1.0 * stock_score
        else:
            points += 0.0  # No clothing available
    
    # Medical supplies
    if person_filters.get("needs_medical", False):
        max_points += 1.0
        if "medical" in charity_inventory and charity_inventory["medical"] > 0:
            stock_level = charity_inventory["medical"]
            stock_score = min(stock_level / 30, 1.0)  # Normalize: 30+ units = perfect
            points += 1.0 * stock_score
        else:
            points += 0.0  # No medical supplies available
    
    # Mental health / counseling services
    if person_filters.get("needs_mental_health", False):
        max_points += 0.8
        mental_health_stock = charity_inventory.get("mental_health", 0) + charity_inventory.get("counseling", 0)
        if mental_health_stock > 0:
            stock_score = min(mental_health_stock / 20, 1.0)  # Normalize: 20+ units = perfect
            points += 0.8 * stock_score
        else:
            points += 0.0  # No mental health services available
    
    # Quality rating bonus (if available)
    quality = organization.get("quality_rating", None)
    if quality:
        max_points += 0.7
        points += (quality / 5.0) * 0.7
    else:
        max_points += 0.7
        points += 0.35  # Neutral if unknown
    
    # If person didn't specify any needs, return neutral
    if max_points == 0:
        return 0.5
    
    return min(points / max_points, 1.0)


def _calculate_capacity_score(person_filters: dict, organization: dict) -> float:
    """
    Calculate shelter capacity score based on bed availability (0-1 scale).
    
    Higher bed availability = higher score = less crowded.
    This is only used for shelters (housing needs).
    
    Args:
        person_filters: Person's information (not really used here)
        organization: Shelter data with beds_available
        
    Returns:
        float: Score from 0-1 (1 = plenty of beds, 0 = nearly full)
    """
    ammenities = organization.get("ammenities", {})
    beds_available = ammenities.get("beds_available", 0)
    
    # Score based on bed availability
    # 20+ beds = 1.0 (lots of capacity)
    # 10-19 beds = 0.7 (moderate capacity)
    # 5-9 beds = 0.5 (limited capacity)
    # 1-4 beds = 0.3 (very limited)
    # 0 beds = 0.0 (no capacity)
    
    if beds_available >= 20:
        return 1.0
    elif beds_available >= 10:
        return 0.7 + (beds_available - 10) / 10 * 0.3  # Scale from 0.7 to 1.0
    elif beds_available >= 5:
        return 0.5 + (beds_available - 5) / 5 * 0.2  # Scale from 0.5 to 0.7
    elif beds_available >= 1:
        return 0.3 + (beds_available - 1) / 4 * 0.2  # Scale from 0.3 to 0.5
    else:
        return 0.0


def _calculate_charity_stock_score(person_filters: dict, organization: dict) -> float:
    """
    Calculate charity stock score based on overall inventory availability (0-1 scale).
    
    Looks at how well-stocked the charity is across all categories they offer.
    Higher "have" levels = better score.
    
    Args:
        person_filters: Person's information (not really used here)
        organization: Charity data with needs/inventory
        
    Returns:
        float: Score from 0-1 (1 = well-stocked, 0 = low stock)
    """
    needs_dict = organization.get("needs", {})
    
    if not needs_dict:
        return 0.5  # No inventory data, neutral
    
    total_stock_score = 0.0
    item_count = 0
    
    # Calculate average stock level across all items
    for item_name, item_data in needs_dict.items():
        have = item_data.get("have", 0)
        needed = item_data.get("needed", 1)  # Avoid division by zero
        
        # Calculate stock percentage for this item
        stock_pct = have / needed if needed > 0 else 0
        total_stock_score += min(stock_pct, 1.0)  # Cap at 100%
        item_count += 1
    
    if item_count == 0:
        return 0.5  # No items, neutral
    
    # Average stock percentage across all items
    avg_stock = total_stock_score / item_count
    
    return round(avg_stock, 2)

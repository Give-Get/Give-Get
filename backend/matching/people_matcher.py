"""
people_matcher.py

Matches people/families to shelters in real-time.

Main function: match_person_to_shelters(person, shelters)
- Takes one person dict and list of shelter dicts
- Returns best matches with scores and explanations
- Returns results in <2 seconds for real-time experience

"""
def match_person_to_shelters(person_filters: dict, shelters: list[dict]) -> dict:

def _filter_feasible_shelters(person_filters, shelters: list[Shelter]):
    """
    Filter out shelters that do not meet the person's criteria.
    """
    feasible_shelters = []
    for shelter in shelters:
        result = _feasibility_check(person_filters, shelter)
        if result["is_feasible"]:
            feasible_shelters.append(result)
    return feasible_shelters

def _feasibility_check(person_filters, shelter):


    """
    Expected person_filters dictionary structure:
    {         
        "needs_family_rooms": bool (required),
        "beds_needed": int (required),
        "needs_handicapped_access": bool (required),
        "owns_pets": bool (required),
        "shelter_requires_id": bool (required),
        "urgency_level": str (required: "immediate", "within_week", "within_month"),
        "current_location": str (required: zip code),
        "max_travel_distance_miles": int (default: 25)
        "gender": str (required: "male", "female", "other"),
        "age": int (required: 18-65),
        "language": str (required: "english", "spanish", "other"),
        "immigration_status": str (required: "citizen", "permanent_resident", "temporary_resident", "refugee", "other"),
        "veteran_status": str (required: "yes", "no"),
        "criminal_record": str (required: "yes", "no"),
        "sobriety": str (required: "yes", "no"),
        "needs_food": str (required: "yes", "no"),
        "needs_shelter": str (required: "yes", "no"),
        "needs_clothing": str (required: "yes", "no"),
        "needs_medical": str (required: "yes", "no"),
        "needs_mental_health": str (required: "yes", "no")
    }

    Expected shelter dictionary structure:
    {
        "name": str (required),
        "address": str (required),
        "city": str (required),
        "state": str (required),
        "zip_code": str (required),
        "phone": str (required),
        "allows_pets": bool (default: False),
        "has_wheelchair_access": bool (default: False),
        "available_beds": int (required),
        "available_family_rooms": int (default: 0),
        "gender_restriction": str (optional: "male_only", "female_only", None),
        "min_age": int (optional),
        "max_age": int (optional),
        "accepts_criminal_record": bool (default: True),
        "requires_sobriety": bool (default: False),
        "requires_id": bool (default: False),
        "veterans_only": bool (default: False),
        "languages_supported": list[str] or str (default: ["english"]),
    }

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
    constraints = [
        # Pets constraint
        {
            "name": "pets",
            "applies": lambda p, s: p.get("owns_pets", False),
            "passes": lambda p, s: s.get("allows_pets", False),
            "failure_msg": lambda p, s: "Shelter does not allow pets"
        },
        # Wheelchair/handicapped access
        {
            "name": "wheelchair_access",
            "applies": lambda p, s: p.get("needs_handicapped_access", False),
            "passes": lambda p, s: s.get("has_wheelchair_access", False),
            "failure_msg": lambda p, s: "Shelter is not wheelchair accessible"
        },
        # Capacity check
        {
            "name": "capacity",
            "applies": lambda p, s: True,  # Always applies
            "passes": lambda p, s: p.get("beds_needed", 1) <= s.get("available_beds", 0),
            "failure_msg": lambda p, s: f"Not enough beds (need {p.get('beds_needed', 1)}, available {s.get('available_beds', 0)})"
        },
        # Family room
        {
            "name": "family_room",
            "applies": lambda p, s: p.get("needs_family_rooms", False),
            "passes": lambda p, s: s.get("available_family_rooms", 0) > 0,
            "failure_msg": lambda p, s: "No family rooms available"
        },
        # Gender restrictions
        {
            "name": "gender",
            "applies": lambda p, s: s.get("gender_restriction", None) is not None,
            "passes": lambda p, s: _check_gender_match(p, s),
            "failure_msg": lambda p, s: f"Shelter is {s.get('gender_restriction', 'restricted')}"
        },
        # Age restrictions
        {
            "name": "age",
            "applies": lambda p, s: s.get("min_age", None) or s.get("max_age", None),
            "passes": lambda p, s: _check_age_range(p, s),
            "failure_msg": lambda p, s: f"Age requirements not met (shelter: {s.get('min_age', 'N/A')}-{s.get('max_age', 'N/A')})"
        },
        # Criminal record
        {
            "name": "criminal_record",
            "applies": lambda p, s: p.get("criminal_record", "no") == "yes",
            "passes": lambda p, s: s.get("accepts_criminal_record", True),
            "failure_msg": lambda p, s: "Shelter does not accept individuals with criminal records"
        },
        # Sobriety requirement
        {
            "name": "sobriety",
            "applies": lambda p, s: s.get("requires_sobriety", False),
            "passes": lambda p, s: p.get("sobriety", "no") == "yes",
            "failure_msg": lambda p, s: "Shelter requires sobriety"
        },
        # ID requirement
        {
            "name": "id_requirement",
            "applies": lambda p, s: s.get("requires_id", False),
            "passes": lambda p, s: p.get("has_id", True),
            "failure_msg": lambda p, s: "Shelter requires government-issued ID"
        },
        # Veteran priority (not a hard constraint, but can be)
        {
            "name": "veteran_priority",
            "applies": lambda p, s: s.get("veterans_only", False),
            "passes": lambda p, s: p.get("veteran_status", "no") == "yes",
            "failure_msg": lambda p, s: "Shelter is veterans-only"
        },
        # Language support - person needs language, shelter must support it
        {
            "name": "language_support",
            "applies": lambda p, s: p.get("language", "english").lower() != "english",
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
    
    return shelter.append({
        "is_feasible": len(failed_constraints) == 0,
        "constraints_passed": passed_constraints,
        "constraints_failed": failed_constraints,
        "failure_reasons": failure_reasons})


# Helper functions for complex constraint checks
def _check_gender_match(person: dict, shelter: dict) -> bool:
    """Check if person's gender matches shelter's restrictions."""
    gender_restriction = shelter.get("gender_restriction", None)
    if not gender_restriction:
        return True
    
    person_gender = person.get("gender", "").lower()
    
    if gender_restriction == "male_only":
        return person_gender in ["male", "m"]
    elif gender_restriction == "female_only":
        return person_gender in ["female", "f"]
    else:
        return True


def _check_age_range(person: dict, shelter: dict) -> bool:
    """Check if person's age falls within shelter's accepted range."""
    person_age = person.get("age", None)
    if person_age is None:
        return False  # Can't verify without age
    
    min_age = shelter.get("min_age", None)
    max_age = shelter.get("max_age", None)
    
    if min_age and person_age < min_age:
        return False
    if max_age and person_age > max_age:
        return False
    
    return True


def _check_language_support(person: dict, shelter: dict) -> bool:
    """
    Check if shelter supports the language person needs.
    Person specifies what language they speak/need.
    Shelter has list of languages their staff can support.
    """
    person_language = person.get("language", "english").lower()
    
    # Get shelter's supported languages (could be a list or single string)
    shelter_languages = shelter.get("languages_supported", ["english"])
    
    # If shelter_languages is a string, convert to list
    if isinstance(shelter_languages, str):
        shelter_languages = [shelter_languages]
    
    # Normalize to lowercase for comparison
    shelter_languages = [lang.lower() for lang in shelter_languages]
    
    # Check if person's language is in shelter's supported languages
    return person_language in shelter_languages

def score_all_matches(person_filters, shelters: list[Shelter]):

def calculate_urgency_score(person_filters):



def calculate_distance_score(person_filters, shelters: list[Shelter]):

def estimate_distance_from_zip(zip_code1, zip_code2):

def calculate_fit_score(person_filters, shelters: list[Shelter]):

def calculate_capacity_utilization_score(person: dict, shelter: dict) -> float:

#If time
def add_explanations(person: dict, scored_matches: list[dict]) -> list[dict]:
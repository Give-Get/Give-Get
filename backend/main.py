"""
api.py

FastAPI endpoints for matching services and organization management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os
import json
from pathlib import Path


# Add backend directory to path for imports
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Import matching functions
from matching.people_matcher import sort_shelters_by_score
from matching.supply_matcher import sort_organizations_by_need

# Import verification service
from validation_service import VerificationService, Organization

# Initialize verification service
verifier = VerificationService()

from db import (
    create_user,
    create_organization,
    update_user,
    update_organization,
    collect_user,
    collect_organization,
    get_orgs_within_radius,
    get_account_id
)

# Initialize FastAPI app
app = FastAPI(
    title="Give and Get API",
    description="Complete API for matching people to shelters/charities, donors to organizations, and organization management",
    version="1.0.0"
)

# CORS middleware (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production (e.g., ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== PYDANTIC MODELS ====================

class Location(BaseModel):
    """Geographic coordinates"""
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lng: float = Field(..., description="Longitude", ge=-180, le=180)


class PersonFilters(BaseModel):
    """Person's needs and preferences for shelter/charity matching"""
    
    # Core need type - determines if we match to shelters or charities
    needs_housing: bool = Field(
        ..., 
        description="True if needs housing (match to shelters), False if needs resources only (match to charities)"
    )
    
    # Housing-specific fields (only relevant if needs_housing = true)
    beds_needed: Optional[int] = Field(1, description="Number of beds needed", ge=1)
    needs_handicapped_access: Optional[bool] = Field(False, description="Requires wheelchair accessibility")
    owns_pets: Optional[bool] = Field(False, description="Has pets that need accommodation")
    preferred_duration_days: Optional[int] = Field(30, description="Preferred stay duration in days", ge=1)
    days_homeless: Optional[int] = Field(None, description="Number of days homeless (for urgency calculation)", ge=0)
    # Housing preferences (for fit scoring, not hard constraints)
    prefers_family_rooming: Optional[bool] = Field(False, description="Prefers family room accommodation")
    can_pay_fees: Optional[bool] = Field(False, description="Able to pay shelter fees")
    max_affordable_fee: Optional[int] = Field(0, description="Maximum affordable fee in dollars", ge=0)
    lgbtq_identity: Optional[bool] = Field(False, description="Identifies as LGBTQ+")
    prefers_medical_support: Optional[bool] = Field(False, description="Prefers medical support services")
    prefers_counseling: Optional[bool] = Field(False, description="Prefers counseling services")
    prefers_meals_provided: Optional[bool] = Field(False, description="Prefers meals provided")
    prefers_showers: Optional[bool] = Field(False, description="Prefers shower facilities")
    duration_flexibility: Optional[str] = Field(
        "flexible", 
        description="Duration flexibility: 'flexible' or 'fixed'"
    )
    
    # General fields (apply to both housing and charity needs)
    urgency_level: str = Field(
        ..., 
        description="Urgency level: 'immediate', 'within_week', or 'within_month'"
    )
    max_travel_distance_miles: Optional[int] = Field(25, description="Maximum travel distance in miles", ge=1, le=500)
    gender: str = Field(..., description="Gender: 'male', 'female', or 'other'")
    age: int = Field(..., description="Age in years", ge=0, le=120)
    language: Optional[str] = Field("english", description="Preferred language")
    immigration_status: Optional[str] = Field(
        None, 
        description="Immigration status: 'citizen', 'permanent_resident', 'temporary_resident', 'refugee', or 'other'"
    )
    veteran_status: Optional[str] = Field("no", description="Veteran status: 'yes' or 'no'")
    criminal_record: Optional[str] = Field("no", description="Criminal record: 'yes' or 'no'")
    sobriety: Optional[str] = Field("no", description="Sober status: 'yes' or 'no'")
    has_id: Optional[bool] = Field(True, description="Has government-issued ID")
    
    # Resource needs (relevant for charity matching when needs_housing = false)
    needs_food: Optional[bool] = Field(False, description="Needs food assistance")
    needs_clothing: Optional[bool] = Field(False, description="Needs clothing")
    needs_medical: Optional[bool] = Field(False, description="Needs medical supplies")
    needs_mental_health: Optional[bool] = Field(False, description="Needs mental health support")


class DonorItem(BaseModel):
    """Single item a donor wants to donate"""
    category: str = Field(..., description="Item category: 'food', 'clothing', 'bedding', 'medical', 'toys', etc.")
    item: str = Field(..., description="Specific item name (e.g., 'canned beans', 'jackets')")
    quantity: int = Field(..., description="Quantity to donate", ge=1)


class DonorItems(BaseModel):
    """Items a donor wants to donate"""
    items: List[DonorItem] = Field(..., description="List of items to donate", min_items=1)


class PeopleMatchRequest(BaseModel):
    """Request body for people matching endpoint"""
    location: Location = Field(..., description="Person's current location")
    radius: int = Field(25, description="Search radius in miles", ge=1, le=100)
    person_filters: Optional[PersonFilters] = Field(
        None, 
        description="Person's needs and preferences. If omitted, returns all nearby orgs sorted by distance"
    )


class SupplyMatchRequest(BaseModel):
    """Request body for supply matching endpoint"""
    location: Location = Field(..., description="Donor's location")
    radius: int = Field(25, description="Search radius in miles", ge=1, le=100)
    donor_items: Optional[DonorItems] = Field(
        None, 
        description="Items to donate. If omitted, returns all nearby orgs sorted by distance"
    )

#======= DB Pydantic Models ========
class OrgType(BaseModel):
    charity: bool
    shelter: bool


class ContactInfo(BaseModel):
    phone: str
    email: str
    website: Optional[str] = ""


class OrganizationValidationContact(BaseModel):
    """Optional contact details used for lightweight validation"""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""


class OrganizationValidationRequest(BaseModel):
    """Payload from the front-end validator prior to full org creation"""
    EIN: Optional[str] = ""
    name: Optional[str] = ""
    address: Optional[str] = ""
    verified: Optional[bool] = False
    contact: OrganizationValidationContact = Field(default_factory=OrganizationValidationContact)


class Location(BaseModel):
    lat: float
    lng: float


class NeedItem(BaseModel):
    category: str
    needed: int
    have: int
    urgency: str


class Ammenities(BaseModel):
    accessible: Optional[bool] = False
    lgbtq_only: Optional[bool] = False
    male_only: Optional[bool] = False
    female_only: Optional[bool] = False
    all_gender: Optional[bool] = False
    pet_friendly: Optional[bool] = False
    languages: Optional[List[str]] = ["english"]
    family_rooming: Optional[bool] = False
    beds_available: Optional[int] = 0
    medical_support: Optional[bool] = False
    counseling_support: Optional[bool] = False
    fees: Optional[int] = 0
    age_minimum: Optional[int] = 0
    age_maximum: Optional[int] = 120
    veteran_only: Optional[bool] = False
    immigrant_only: Optional[bool] = False
    refugee_only: Optional[bool] = False
    good_criminal_record_standing: Optional[bool] = False
    sobriety_required: Optional[bool] = False
    showers: Optional[bool] = False
    id_required: Optional[bool] = False


class Hours(BaseModel):
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str


# ---------- Main Organization Model ----------

class OrganizationModel(BaseModel):
    _id: Optional[str]
    image_url: Optional[str] = ""
    type: OrgType
    EIN: str
    name: str
    address: str
    location: Location
    ammenities: Ammenities
    needs: Dict[str, NeedItem]
    hours: Hours
    description: Optional[str] = ""
    contact: ContactInfo
    verified: bool
    timestamp: Optional[str] = ""

    class Config:
        extra = "allow"

class DonorItem(BaseModel):
    item: str
    quantity: int
    description: Optional[str] = ""
    category: str

class UserModel(BaseModel):
    _id: Optional[str]
    name: str
    charity: bool
    shelter: bool
    donor: bool
    phone_number: str
    email: str
    password: str
    items_donating: Optional[List[DonorItem]] = None

    class Config:
        extra = "allow"


# ---------- Update Request ----------
class UpdateRequest(BaseModel):
    _id: str
    new_json: Dict[str, Any]


# ---------- Radius Query ----------
class RadiusOrgType(BaseModel):
    shelter: bool
    charity: bool

class RadiusQuery(BaseModel):
    location: Location
    radius: float
    org_type: Optional[RadiusOrgType] = None


# ---------- Login Request ----------
class LoginRequest(BaseModel):
    email: str
    password: str

# ==================== ORGANIZATION MODELS (from validation1.py) ====================

class OrganizationType(BaseModel):
    """Organization type flags"""
    shelter: bool
    charity: bool


class Amenities(BaseModel):
    """Organization amenities and restrictions"""
    accessible: bool
    lgbtq_only: bool
    male_only: bool
    female_only: bool
    all_gender: bool
    pet_friendly: bool
    languages: List[str]
    family_rooming: bool
    beds_available: int
    medical_support: bool
    counseling_support: bool
    fees: float
    age_minimum: int
    age_maximum: int
    veteran_only: bool
    immigrant_only: bool
    refugee_only: bool
    good_criminal_record_standing: bool
    sobriety_required: bool
    showers: bool
    id_required: bool


class Hours(BaseModel):
    """Operating hours for each day of the week"""
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str


class Contact(BaseModel):
    """Contact information"""
    phone: str
    email: str
    website: str


class OrganizationCreate(BaseModel):
    """Request body for creating a new organization"""
    type: OrganizationType
    EIN: int
    name: str
    address: str
    location: Location
    ammenities: Amenities
    needs: Dict[str, Any]
    hours: Hours
    description: str
    contact: Contact
    verified: bool
    timestamp: str


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Give and Get Matching API",
        "version": "1.0.0",
        "endpoints": {
            "people_matching": "/api/match-people",
            "supply_matching": "/api/match-supplies",
            "about_us": "/api/about",
            "organizations": "/api/organizations",
            "pending_users": "/api/users/pending",
            "documentation": "/docs"
        }
    }


# ==================== ORGANIZATION MANAGEMENT ENDPOINTS ====================

def save_organization_to_json(org_data: dict) -> str:
    """Save organization data to organizations.json"""
    json_path = Path("organizations.json")
    
    if json_path.exists():
        with json_path.open("r") as f:
            orgs = json.load(f)
    else:
        orgs = {}
    
    if orgs:
        max_id = max(int(k) for k in orgs.keys())
        new_id = str(max_id + 1)
    else:
        new_id = "1"
    
    # Add new organization
    orgs[new_id] = org_data
    
    # Save back to file
    with json_path.open("w") as f:
        json.dump(orgs, f, indent=2)
    
    return new_id


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Backend is running"}


@app.post("/api/organizations")
async def create_organization(org: OrganizationCreate):
    """Create a new organization"""
    try:
        # Convert Pydantic model to dict
        org_data = org.dict()
        
        # Save to organizations.json
        org_id = save_organization_to_json(org_data)
        
        # Create Organization object for verification
        organization = Organization(
            ein=str(org_data["EIN"]),
            org_name=org_data["name"],
            email=org_data["contact"]["email"],
            phone=org_data["contact"]["phone"],
            website=org_data["contact"]["website"],
            address=org_data["address"]
        )
        
        # Create user in verification system
        verification_result = verifier.create_user({
            'name': organization.org_name,
            'email': organization.email,
            'phone': organization.phone,
            'address': organization.address,
            'id_uploaded': False,  # Will need manual verification
            'ein': organization.ein
        })
        
        # Determine if organization is verified (TRUSTED level = verified)
        is_verified = verification_result.trust_level == "TRUSTED"
        
        return {
            "success": True,
            "message": "Organization created successfully",
            "organization_id": org_id,
            "verification_status": {
                "user_id": verification_result.id,
                "trust_score": verification_result.trust_score,
                "trust_level": verification_result.trust_level,
                "status": "pending_review" if verification_result.trust_score < 70 else "approved",
                "verified": is_verified
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating organization: {str(e)}")


@app.post("/api/org/validate")
async def validate_organization(org: OrganizationValidationRequest):
    """
    Run lightweight verification checks for an organization without persisting it.
    Used by the front-end form before full submission.
    """
    try:
        verification_payload = {
            'name': org.name or "",
            'email': (org.contact.email or "").strip(),
            'phone': (org.contact.phone or "").strip(),
            'address': (org.address or "").strip(),
            'id_uploaded': bool(org.verified),
            'ein': (org.EIN or "").strip()
        }

        verification_result = verifier.verify_individual(verification_payload)
        status = verification_result['status']
        success = status != 'rejected'

        if status == 'approved':
            message = "Organization passed automated verification."
        elif status == 'manual_review':
            message = "Organization requires manual review."
        else:
            message = "Organization failed automated verification."

        return {
            "success": success,
            "message": message,
            "verification": {
                "status": status,
                "trust_score": verification_result['score'],
                "trust_level": verification_result['trust_level'],
                "checks": verification_result['checks']
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "organization validation"}
        )


class DonorValidationRequest(BaseModel):
    """Payload from the front-end donor signup form for validation"""
    name: str
    email: str
    phone_number: str
    address: str


@app.post("/api/donor/validate")
async def validate_donor(donor: DonorValidationRequest):
    """
    Run lightweight verification checks for a donor without persisting them.
    Used by the front-end donor signup form before full submission.
    """
    try:
        verification_payload = {
            'name': donor.name.strip(),
            'email': donor.email.strip(),
            'phone': donor.phone_number.strip(),
            'address': donor.address.strip(),
            'id_uploaded': False  # Donors don't upload ID during signup
        }

        verification_result = verifier.verify_individual(verification_payload)
        status = verification_result['status']
        success = status != 'rejected'

        if status == 'approved':
            message = "Donor passed automated verification."
        elif status == 'manual_review':
            message = "Donor requires manual review."
        else:
            message = "Donor failed automated verification."

        return {
            "success": success,
            "message": message,
            "verification": {
                "status": status,
                "trust_score": verification_result['score'],
                "trust_level": verification_result['trust_level'],
                "checks": verification_result['checks']
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "donor validation"}
        )


@app.get("/api/organizations")
async def get_organizations():
    """Get all organizations"""
    try:
        json_path = Path("organizations.json")
        
        if json_path.exists():
            with json_path.open("r") as f:
                orgs = json.load(f)
            return {
                "success": True,
                "organizations": orgs
            }
        else:
            return {
                "success": True,
                "organizations": {}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching organizations: {str(e)}")


@app.get("/api/organizations/{org_id}")
async def get_organization(org_id: str):
    """Get a specific organization"""
    try:
        json_path = Path("organizations.json")
        
        if json_path.exists():
            with json_path.open("r") as f:
                orgs = json.load(f)
            
            if org_id in orgs:
                return {
                    "success": True,
                    "organization": orgs[org_id]
                }
            else:
                raise HTTPException(status_code=404, detail="Organization not found")
        else:
            raise HTTPException(status_code=404, detail="No organizations found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching organization: {str(e)}")


@app.get("/api/users/pending")
async def get_pending_users():
    """Get users pending verification"""
    try:
        pending = verifier.get_pending_users()
        users_data = []
        
        for user in pending:
            users_data.append({
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "trust_score": user.trust_score,
                "trust_level": user.trust_level,
                "verification_checks": user.verification_checks
            })
        
        return {
            "success": True,
            "pending_users": users_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending users: {str(e)}")


@app.post("/api/users/{user_id}/approve")
async def approve_user(user_id: int):
    """Approve a user"""
    try:
        success = verifier.approve_user(user_id)
        
        if success:
            return {
                "success": True,
                "message": f"User {user_id} approved"
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving user: {str(e)}")


@app.post("/api/users/{user_id}/reject")
async def reject_user(user_id: int):
    """Reject a user"""
    try:
        success = verifier.reject_user(user_id)
        
        if success:
            return {
                "success": True,
                "message": f"User {user_id} rejected"
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting user: {str(e)}")


# ==================== MATCHING ENDPOINTS ====================

@app.post("/api/match-people", response_model=Dict[str, Any])
def match_people(request: PeopleMatchRequest):
    """
    Match people to shelters/charities based on their needs.
    
    **Behavior:**
    - If `person_filters` provided: Returns organizations ranked by match score (0-100)
        - If `needs_housing = true`: matches to shelters with feasibility filtering
        - If `needs_housing = false`: matches to charities based on resource needs
    - If `person_filters` omitted: Returns all nearby organizations sorted by distance (all score = 100)
    
    **Returns:**
    - `ranked_organizations`: Dictionary with ranks as keys (1, 2, 3, ...) and organization data as values
    - Each organization includes a `score` field (0-100, higher = better match)
    
    **Example Response:**
    ```json
    {
      "success": true,
      "matches_found": 3,
      "ranked_organizations": {
        "1": {"name": "Safe Haven Shelter", "score": 95, ...},
        "2": {"name": "Community Shelter", "score": 82, ...},
        "3": {"name": "Food Bank", "score": 70, ...}
      }
    }
    ```
    """
    try:
        # Convert Pydantic models to dicts
        location_dict = request.location.dict()
        person_filters_dict = request.person_filters.dict() if request.person_filters else None
        
        # Call matching function
        ranked_orgs = sort_shelters_by_score(
            location=location_dict,
            radius=request.radius,
            person_filters=person_filters_dict
        )
        
        return {
            "success": True,
            "matches_found": len(ranked_orgs),
            "ranked_organizations": ranked_orgs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Matching error",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@app.post("/api/match-supplies", response_model=Dict[str, Any])
def match_supplies(request: SupplyMatchRequest):
    """
    Match donors to organizations that need their items.
    
    **Behavior:**
    - If `donor_items` provided: Returns organizations ranked by need score (0-100)
        - Higher score = organization needs these items more urgently
        - Scoring based on urgency, gap size, and distance
    - If `donor_items` omitted: Returns all nearby organizations sorted by distance (all score = 100)
    
    **Returns:**
    - `ranked_organizations`: Dictionary with ranks as keys (1, 2, 3, ...) and organization data as values
    - Each organization includes a `score` field (0-100, higher = greater need)
    
    **Example Response:**
    ```json
    {
      "success": true,
      "matches_found": 2,
      "ranked_organizations": {
        "1": {"name": "Food Bank", "score": 95, "needs": {...}},
        "2": {"name": "Clothing Drive", "score": 78, "needs": {...}}
      }
    }
    ```
    """
    try:
        # Convert Pydantic models to dicts
        location_dict = request.location.dict()
        donor_items_dict = None
        
        if request.donor_items:
            donor_items_dict = {
                "items": [item.dict() for item in request.donor_items.items]
            }
        
        # Call matching function
        ranked_orgs = sort_organizations_by_need(
            location=location_dict,
            radius=request.radius,
            donor_items=donor_items_dict
        )
        
        return {
            "success": True,
            "matches_found": len(ranked_orgs),
            "ranked_organizations": ranked_orgs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Matching error",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@app.get("/api/about")
async def get_about_us():
    """
    Get About Us information including mission, impact metrics, and team info.
    Perfect for displaying on an About Us page.
    """
    try:
        # Calculate real-time impact metrics
        json_path = Path("organizations.json")
        total_organizations = 0
        total_beds_available = 0
        total_items_needed = 0
        shelters_count = 0
        charities_count = 0
        
        if json_path.exists():
            with json_path.open("r") as f:
                orgs = json.load(f)
                total_organizations = len(orgs)
                
                for org_id, org_data in orgs.items():
                    # Count organization types
                    org_type = org_data.get("type", {})
                    if org_type.get("shelter"):
                        shelters_count += 1
                        # Count beds
                        amenities = org_data.get("ammenities", {})
                        total_beds_available += amenities.get("beds_available", 0)
                    if org_type.get("charity"):
                        charities_count += 1
                    
                    # Count items needed
                    needs = org_data.get("needs", {})
                    if isinstance(needs, dict):
                        for item_name, item_data in needs.items():
                            if isinstance(item_data, dict):
                                needed = item_data.get("needed", 0)
                                have = item_data.get("have", 0)
                                gap = needed - have
                                if gap > 0:
                                    total_items_needed += gap
        
        # Get user verification stats
        pending_users = verifier.get_pending_users()
        all_users = verifier.get_all_users()
        
        return {
            "mission": {
                "title": "Our Mission",
                "description": "Give and Get connects people in need with shelters and charities, while efficiently matching donors with organizations that need their contributions. We use smart matching algorithms to ensure resources reach those who need them most.",
                "vision": "A community where no one goes without shelter or basic necessities, and every donation creates maximum impact."
            },
            "story": {
                "title": "Our Story",
                "content": "Give and Get was born from a simple observation: generous donors want to help, shelters and charities desperately need resources, yet connecting them efficiently remains a challenge. We built an intelligent matching system that considers urgency, location, capacity, and specific needs to create optimal matches in real-time."
            },
            "impact": {
                "title": "Our Impact",
                "metrics": {
                    "organizations_partnered": total_organizations,
                    "shelters": shelters_count,
                    "charities": charities_count,
                    "beds_available": total_beds_available,
                    "items_needed": total_items_needed,
                    "verified_users": len([u for u in all_users if u.trust_score >= 70]),
                    "pending_verifications": len(pending_users)
                },
                "highlights": [
                    {
                        "number": total_organizations,
                        "label": "Partner Organizations",
                        "description": "Shelters and charities we work with"
                    },
                    {
                        "number": total_beds_available,
                        "label": "Beds Available",
                        "description": "Shelter spaces ready to help families"
                    },
                    {
                        "number": total_items_needed,
                        "label": "Items Needed",
                        "description": "Urgent needs waiting to be filled"
                    },
                    {
                        "number": len(all_users),
                        "label": "Community Members",
                        "description": "Donors and organizations making a difference"
                    }
                ]
            },
            "how_it_works": {
                "title": "How It Works",
                "steps": [
                    {
                        "step": 1,
                        "title": "Share Your Needs",
                        "description": "People in need fill out a simple form with their requirements. Donors tell us what they want to give.",
                        "icon": "📝"
                    },
                    {
                        "step": 2,
                        "title": "Smart Matching",
                        "description": "Our intelligent algorithm finds the best matches based on location, urgency, capacity, and specific needs.",
                        "icon": "🤖"
                    },
                    {
                        "step": 3,
                        "title": "Instant Results",
                        "description": "Get matched with verified shelters and charities in seconds. See scores and explanations for each match.",
                        "icon": "⚡"
                    },
                    {
                        "step": 4,
                        "title": "Make Impact",
                        "description": "Connect directly with organizations. Track your impact and see how your contribution helps real people.",
                        "icon": "❤️"
                    }
                ]
            },
            "values": [
                {
                    "title": "Transparency",
                    "description": "Every match comes with a detailed explanation of why it was made.",
                    "icon": "🔍"
                },
                {
                    "title": "Efficiency",
                    "description": "Smart algorithms ensure resources go where they're needed most.",
                    "icon": "⚙️"
                },
                {
                    "title": "Accessibility",
                    "description": "Easy-to-use platform that works for everyone, regardless of technical expertise.",
                    "icon": "🌟"
                },
                {
                    "title": "Verification",
                    "description": "All organizations are verified to ensure donations reach legitimate causes.",
                    "icon": "✅"
                }
            ],
            "team": {
                "title": "Our Team",
                "description": "Built by students passionate about using technology to solve real-world social challenges.",
                "members": [
                    {
                        "name": "Development Team",
                        "role": "Full-Stack Development",
                        "description": "Built the matching algorithms and platform infrastructure"
                    },
                    {
                        "name": "Community Partners",
                        "role": "Shelter & Charity Network",
                        "description": "Local organizations helping us understand real needs"
                    }
                ]
            },
            "contact": {
                "title": "Get In Touch",
                "description": "Want to partner with us or learn more about our mission?",
                "email": "contact@giveandget.org",
                "social": {
                    "twitter": "@giveandget",
                    "linkedin": "give-and-get"
                }
            }
        }
        
    except Exception as e:
        # Return default content if there's an error
        return {
            "mission": {
                "title": "Our Mission",
                "description": "Give and Get connects people in need with shelters and charities, while efficiently matching donors with organizations that need their contributions.",
                "vision": "A community where no one goes without shelter or basic necessities."
            },
            "impact": {
                "title": "Our Impact",
                "metrics": {
                    "organizations_partnered": 0,
                    "beds_available": 0,
                    "items_needed": 0
                }
            }
        }


@app.get("/api/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "endpoints": {
            "root": "/",
            "people_matching": "/api/match-people",
            "supply_matching": "/api/match-supplies",
            "about_us": "/api/about",
            "health_check": "/api/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# ==================== NEW DATABASE ROUTES ====================

# ---------- USERS ----------
@app.post("/api/user/create")
def api_create_user(user: UserModel):
    """
    Create a new user (charity, shelter, or donor).
    The JSON body must follow the UserModel schema exactly as defined in MongoDB.
    """
    try:
        create_user(user.dict())
        return {
            "status": "success",
            "message": f"User '{user.name}' created successfully.",
            "user_id": user._id or "auto-assigned"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "user creation", "hint": f"Likely failing variable: {repr(e.args)}"},
        )


@app.put("/api/user/update")
def api_update_user(req: UpdateRequest):
    """
    Update an existing user's information.
    Input must include "_id" and "new_json".
    """
    try:
        update_user(req._id, req.new_json)
        return {
            "status": "success",
            "message": f"User {req._id} updated successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "user update"}
        )


@app.get("/api/user/{user_id}")
def api_get_user(user_id: str):
    """Retrieve a user document by _id."""
    try:
        user = collect_user(user_id)
        return {"status": "success", "data": user}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={"error": str(e), "context": "user fetch"}
        )


# ---------- ORGANIZATIONS ----------
@app.post("/api/org/create")
def api_create_org(org: OrganizationModel):
    """
    Create a new organization.
    The request body must match OrganizationModel structure.
    """
    try:
        create_organization(org.dict())
        return {
            "status": "success",
            "message": f"Organization '{org.name}' created successfully.",
            "org_id": org._id or "auto-assigned"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "organization creation"}
        )


@app.put("/api/org/update")
def api_update_org(req: UpdateRequest):
    """
    Update an existing organization by _id.
    Input must include "_id" and "new_json".
    """
    try:
        update_organization(req._id, req.new_json)
        return {
            "status": "success",
            "message": f"Organization {req._id} updated successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "organization update"}
        )


@app.get("/api/org/{org_id}")
def api_get_org(org_id: str):
    """Retrieve an organization by _id."""
    try:
        org = collect_organization(org_id)
        return {"status": "success", "data": org}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={"error": str(e), "context": "organization fetch"}
        )


# ---------- RADIUS SEARCH ----------
@app.post("/api/orgs/within_radius")
def api_get_orgs_within_radius(query: RadiusQuery):
    """
    Query organizations (charities/shelters) within a given radius (in miles)
    of the provided location coordinates.
    """
    try:
        org_type = query.org_type or {"shelter": True, "charity": True}
        results = get_orgs_within_radius(
            query.location.dict(),
            query.radius,
            org_type
        )

        formatted = [
            {
                "distance_miles": round(distance, 3),
                "organization": org
            }
            for distance, org in results
        ]
        return {
            "status": "success",
            "count": len(formatted),
            "results": formatted
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "context": "radius query"}
        )


# ---------- ACCOUNT LOGIN ----------
@app.post("/api/account/get_id")
def api_get_account_id(req: LoginRequest):
    """
    Authenticate a user by email/password and return their _id.
    Raises 401 if invalid credentials.
    """
    try:
        account_id = get_account_id(req.email, req.password)
        return {
            "status": "success",
            "account_id": account_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"error": str(e), "context": "login"}
        )

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Give and Get API...")
    print("="*60)
    print("📍 API available at: http://localhost:8000")
    print("📚 Interactive API docs: http://localhost:8000/docs")
    print("📖 Alternative docs: http://localhost:8000/redoc")
    print("\n" + "="*60)
    print("Available endpoints:")
    print("\n🏥 MATCHING ENDPOINTS:")
    print("  POST /api/match-people       - Match people to shelters/charities")
    print("  POST /api/match-supplies     - Match donors to organizations")
    print("\n🏢 ORGANIZATION MANAGEMENT:")
    print("  GET  /api/health             - Health check")
    print("  GET  /api/about              - About us & impact metrics")
    print("  POST /api/organizations      - Create organization")
    print("  GET  /api/organizations      - Get all organizations")
    print("  GET  /api/organizations/{id} - Get specific organization")
    print("\n👥 USER VERIFICATION:")
    print("  GET  /api/users/pending      - Get pending users")
    print("  POST /api/users/{id}/approve - Approve user")
    print("  POST /api/users/{id}/reject  - Reject user")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

"""
api.py

FastAPI endpoints for matching services
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os


# Add backend directory to path for imports
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Import matching functions
from matching.people_matcher import sort_shelters_by_score
from matching.supply_matcher import sort_organizations_by_need

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
    title="Give and Get Matching API",
    description="API for matching people to shelters/charities and donors to organizations",
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
    days_homeless: Optional[int] = Field(None, description="Number of days homeless (for urgency calculation)", ge=0)
    preferred_duration_days: Optional[int] = Field(30, description="Preferred stay duration in days", ge=1)
    
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
            "documentation": "/docs"
        }
    }


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
            detail={"error": str(e), "context": "user creation"}
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
    print("Starting Give and Get Matching API...")
    print("API Documentation available at: http://localhost:8000/docs")
    print("Alternative docs at: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


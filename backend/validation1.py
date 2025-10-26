from dataclasses import dataclass, field
from typing import Dict, List
import re
import datetime
import json
from pathlib import Path
import requests

def load_json(path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)

@dataclass
class Donor:
    email: str
    phone: str
    full_name: str
    address: str

@dataclass
class Receiver:
    name: str
    phone: str
    items_list: str
    request: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Organization:
    """Works on verifying orgs/shelters"""
    ein: str #IRS tax ID
    org_name: str
    email: str
    phone: str
    website: str
    address: str

@dataclass
class User:
    id: int
    email: str
    phone: str
    full_name: str
    trust_score: int
    trust_level: str
    verification_checks: dict

class VerificationService:
    def __init__(self):
        self.users = []
        self.next_id = 1
        self.verified_ein_cache = {}
        self.load_from_json_files()
    
    def verify_individual(self, user_data: dict) -> dict:
        score = 0
        checks = {}
        
        #email ver
        if self.verify_email(user_data['email']):
            score += 20
            checks['email'] = {'status': 'verified', 'points': 20}
        else:
            checks['email'] = {'status': 'failed', 'points': 0}
        
        #phone ver
        if user_data.get('phone') and self.verify_phone(user_data['phone']):
            score += 20
            checks['phone'] = {'status': 'verified', 'points': 20}
        else:
            checks['phone'] = {'status': 'failed', 'points': 0}
        
        #id ver
        if user_data.get('id_uploaded'):
            score += 30
            checks['id'] = {'status': 'verified', 'points': 30}
        
        #address check
        if user_data.get('address'):
            score += 20
            checks['address'] = {'status': 'valid', 'points': 20}
        
        #fraud check
        if not self.check_fraud(user_data['email']):
            score += 10
            checks['fraud'] = {'status': 'clean', 'points': 10}
        else:
            score = 0
            checks['fraud'] = {'status': 'flagged', 'points': 0}
        
        if user_data.get("ein"):
            try:
                ein_value = int(user_data["ein"])
                if 1 <= ein_value <= 25:
                    score += 30
                    checks['ein'] = {'status': 'verified', 'points': 30}
                else:
                    checks['ein'] = {'status': 'invalid_range', 'points': 0}
                    score = 0
            except ValueError:
                checks['ein'] = {'status': 'invalid_format', 'points': 0}
                score = 0
        elif "ein" in user_data:
            checks['ein'] = {'status': 'missing', 'points': 0}
            score = 0
        
        trust_level = self.calculate_trust_level(score)
        status = 'approved' if score >= 70 else 'manual_review' if score >= 40 else 'rejected'
        
        return {
            'score': score,
            'trust_level': trust_level,
            'checks': checks,
            'status': status
        }
    
    def verify_email(self, email: str) -> bool:
        """Basic email validation"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
        
        disposable = ['tempmail.com', 'guerrillamail.com', 'throwaway.email']
        domain = email.split('@')[1]
        return domain not in disposable
    
    def verify_phone(self, phone: str) -> bool:
        """Basic phone validation"""
        digits = re.sub(r'\D', '', phone)
        return len(digits) == 10
    
    def check_fraud(self, email: str) -> bool:
        """Check if email is flagged"""
        return False
    
    def calculate_trust_level(self, score: int) -> str:
        if score >= 80:
            return 'TRUSTED'
        elif score >= 60:
            return 'STANDARD'
        elif score >= 40:
            return 'BASIC'
        else:
            return 'UNVERIFIED'
    
    def create_user(self, user_data: dict) -> User:
        """Create and verify a user"""
        verification_result = self.verify_individual(user_data)
        
        user = User(
            id=self.next_id,
            email=user_data['email'],
            phone=user_data.get('phone', ''),
            full_name=user_data.get('name', ''),
            trust_score=verification_result['score'],
            trust_level=verification_result['trust_level'],
            verification_checks=verification_result['checks']
        )
        
        self.users.append(user)
        self.next_id += 1
        return user
    
    def get_pending_users(self) -> List[User]:
        """Get users needing manual review"""
        return [u for u in self.users if 40 <= u.trust_score < 70]
    
    def get_all_users(self) -> List[User]:
        return self.users
    
    def approve_user(self, user_id: int):
        """Admin approves a user"""
        user = next((u for u in self.users if u.id == user_id), None)
        if user:
            user.trust_score = 70
            user.trust_level = 'STANDARD'
            return True
        return False
    
    def reject_user(self, user_id: int):
        """Admin rejects a user"""
        user = next((u for u in self.users if u.id == user_id), None)
        if user:
            user.trust_score = 0
            user.trust_level = 'REJECTED'
            return True
        return False
    
    def load_from_json_files(self, base_path: str = "mnt/data/"):
        users = load_json(f"{base_path}/users.json")
        orgs = load_json(f"{base_path}/organizations.json")

        if not users and not orgs:
            test_orgs = {
                "charity_water": {
                    "EIN": "67",
                    "contact": {"website": "https://www.charitywater.org"},
                    "address": "40 Worth St, New York, NY 10013",
                    "verified": True
                },
                "doctors_without_borders": {
                    "EIN": "1",
                    "contact": {"website": "https://www.doctorswithoutborders.org"},
                    "address": "333 7th Ave, New York, NY 10001",
                    "verified": True
                },
                "help_shelter": {
                    "name": "Help Shelter Org",
                    "email": "contact@helpshelter.org",
                    "phone_number": "2125555678",
                    "shelter": True
                }
            }
            test_users = {
                "bob_donor": {
                    "name": "Bob Donor",
                    "email": "bob@example.com",
                    "phone_number": "2125551234",
                    "donor": True,
                    "address": "456 Elm St, Springfield"
                },
                "ElliotAlderson": {
                    "name": "Mr Robot",
                    "email": "",
                    "phone_number": "",
                    "donor": False,
                    "address": ""
                }
            }
            for uid, org_data in test_orgs.items():
                org = Organization(
                    ein=str(org_data.get("EIN", "")),
                    org_name=uid.replace("_", " ").title(),
                    email=f"{uid}@example.org",
                    phone="2125550000",
                    website=org_data.get("contact", {}).get("website", "https://example.com"),
                    address=org_data.get("address", "123 Placeholder St")
                )
                self.create_user({
                    'name': org.org_name,
                    'email': org.email,
                    'phone': org.phone,
                    'address': org.address,
                    'id_uploaded': org_data.get("verified", False),
                    'ein': org.ein
                })
            for uid, data in test_users.items():
                if data.get("donor"):
                    self.create_user({
                        'name': data.get("name", uid),
                        'email': data.get("email", f"{uid}@example.com"),
                        'phone': data.get("phone_number", "1234567890"),
                        'address': data.get("address", "123 Placeholder St"),
                        'id_uploaded': True
                    })
                elif data.get("shelter") or data.get("charity"):
                    self.create_user({
                        'name': data.get("name", uid),
                        'email': data.get("email", f"{uid}@example.com"),
                        'phone': data.get("phone_number", "1234567890"),
                        'address': data.get("address", "123 Placeholder St"),
                        'id_uploaded': False,
                        'ein': data.get("ein", "")
                    })
                else:
                    # Fallback for untyped or incomplete users like ElliotAlderson
                    self.create_user({
                        'name': data.get("name", uid),
                        'email': data.get("email", f"{uid}@example.com"),
                        'phone': data.get("phone_number", "0000000000"),
                        'address': data.get("address", "Unknown"),
                        'id_uploaded': False
                    })
            return

        for uid, data in users.items():
            name = data.get("name", uid)
            email = data.get("email", f"{uid}@example.com")
            phone = data.get("phone_number", "1234567890")

            if data.get("donor"):
                donor = Donor(
                    full_name=name,
                    email=email,
                    phone=phone,
                    address=data.get("address", "123 Placeholder St")
                )
                print(f"Loaded Donor: {donor}")
                self.create_user({
                    'name': donor.full_name,
                    'email': donor.email,
                    'phone': donor.phone,
                    'address': donor.address,
                    'id_uploaded': True
                })

            elif data.get("shelter") or data.get("charity"):
                org_data = orgs.get(uid, {})
                if not org_data:
                    # No org data found, treat as org without EIN -> reject
                    self.create_user({
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'address': data.get("address", "123 Placeholder St"),
                        'id_uploaded': False,
                        'ein': ""
                    })
                    continue
                org = Organization(
                    ein=str(org_data.get("EIN", "")),
                    org_name=name,
                    email=email,
                    phone=phone,
                    website=org_data.get("contact", {}).get("website", "https://example.com"),
                    address=org_data.get("address", "123 Placeholder St")
                )
                print(f"Loaded Organization: {org}")
                self.create_user({
                    'name': org.org_name,
                    'email': org.email,
                    'phone': org.phone,
                    'address': org.address,
                    'id_uploaded': org_data.get("verified", False),
                    'ein': org.ein
                })
#file names tbd


#Admin Dashboard (CLI)
class AdminDashboard:
    def __init__(self, verification_service: VerificationService):
        self.service = verification_service
    
    def show_stats(self):
        """Display statistics"""
        all_users = self.service.get_all_users()
        pending = self.service.get_pending_users()
        
        print("\n" + "="*50)
        print("           ADMIN DASHBOARD")
        print("="*50)
        print(f"Total Users: {len(all_users)}")
        print(f"Pending Review: {len(pending)}")
        print(f"Approved: {len([u for u in all_users if u.trust_score >= 70])}")
        print(f"Rejected: {len([u for u in all_users if u.trust_score < 40])}")
        print("="*50 + "\n")
    
    def show_pending_users(self):
        """Show users needing review"""
        pending = self.service.get_pending_users()
        
        if not pending:
            print("No users pending review!\n")
            return
        
        print("\n" + "="*50)
        print("        USERS PENDING REVIEW")
        print("="*50)
        
        for user in pending:
            print(f"\nID: {user.id}")
            print(f"Name: {user.full_name}")
            print(f"Email: {user.email}")
            print(f"Phone: {user.phone}")
            print(f"Score: {user.trust_score}/100")
            print(f"Trust Level: {user.trust_level}")
            print("\nVerification Checks:")
            for check_name, check_data in user.verification_checks.items():
                status = check_data.get('status', 'unknown')
                points = check_data.get('points', 0)
                print(f"  - {check_name}: {status} (+{points} points)")
            print("-" * 50)
    
    def review_user(self, user_id_input: str):
        """Review a specific user"""
        try:
            user_id = int(user_id_input)
        except ValueError:
            print("Invalid User ID!")
            return

        user = next((u for u in self.service.users if u.id == user_id), None)
        
        if not user:
            print(f"User with ID {user_id} not found!")
            return
        
        print("\n" + "="*50)
        print(f"      USER DETAIL - {user.full_name}")
        print("="*50)
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Phone: {user.phone}")
        print(f"Trust Score: {user.trust_score}/100")
        print(f"Trust Level: {user.trust_level}")
        print("\nVerification Breakdown:")
        
        for check_name, check_data in user.verification_checks.items():
            print(f"  {check_name}:")
            for key, value in check_data.items():
                print(f"    - {key}: {value}")
        
        print("\n" + "="*50)
        print("Actions:")
        print("1. Approve")
        print("2. Reject")
        print("3. Back")
        
        choice = input("\nChoice: ")
        
        if choice == '1':
            self.service.approve_user(user.id)
            print(f"✓ User {user.full_name} approved!")
        elif choice == '2':
            self.service.reject_user(user.id)
            print(f"✗ User {user.full_name} rejected!")
    
    def run(self):
        """Main admin interface loop"""
        while True:
            self.show_stats()
            
            print("Menu:")
            print("1. View Pending Users")
            print("2. Review Specific User")
            print("3. View All Users")
            print("4. Exit")
            
            choice = input("\nChoice: ")
            
            if choice == '1':
                self.show_pending_users()
                input("\nPress Enter to continue...")
            
            elif choice == '2':
                user_id = input("Enter User ID: ")
                self.review_user(user_id)
            
            elif choice == '3':
                for user in self.service.get_all_users():
                    print(f"{user.id}. {user.full_name} - Score: {user.trust_score} - Level: {user.trust_level}")
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                print("Goodbye!")
                break


# ============================================================================
# FASTAPI - Web Service Layer
# ============================================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Pydantic models for request/response validation
class OrganizationType(BaseModel):
    shelter: bool
    charity: bool

class Location(BaseModel):
    lat: float
    lng: float

class Amenities(BaseModel):
    accessible: bool
    lgbtq_only: bool
    male_only: bool
    female_only: bool
    all_gender: bool
    pet_friendly: bool
    languages: list[str]
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
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str

class Contact(BaseModel):
    phone: str
    email: str
    website: str

class OrganizationCreate(BaseModel):
    type: OrganizationType
    EIN: int
    name: str
    address: str
    location: Location
    ammenities: Amenities
    needs: dict
    hours: Hours
    description: str
    contact: Contact
    verified: bool
    timestamp: str

def create_fastapi_app(verifier_instance: VerificationService):
    """Create and configure FastAPI app with the verification service"""
    app = FastAPI(
        title="Organization Registration API",
        description="API for registering and verifying organizations",
        version="1.0.0"
    )

    # Enable CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def save_organization_to_json(org_data):
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
            verification_result = verifier_instance.create_user({
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
            pending = verifier_instance.get_pending_users()
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
            success = verifier_instance.approve_user(user_id)

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
            success = verifier_instance.reject_user(user_id)

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

    return app


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import sys

    # Initialize verification service
    verifier = VerificationService()

    # Check if user wants to run API server or CLI dashboard
    if len(sys.argv) > 1 and sys.argv[1] == '--api':
        # Run FastAPI Server
        import uvicorn

        print("🚀 Starting FastAPI Server...")
        print("📍 API will be available at: http://localhost:5000")
        print("📡 CORS enabled for React frontend")
        print("📚 Interactive API docs: http://localhost:5000/docs")
        print("📖 Alternative docs: http://localhost:5000/redoc")
        print("\nAvailable endpoints:")
        print("  GET  /api/health - Health check")
        print("  POST /api/organizations - Create organization")
        print("  GET  /api/organizations - Get all organizations")
        print("  GET  /api/organizations/{id} - Get specific organization")
        print("  GET  /api/users/pending - Get pending users")
        print("  POST /api/users/{id}/approve - Approve user")
        print("  POST /api/users/{id}/reject - Reject user")
        print("\n" + "="*50 + "\n")

        app = create_fastapi_app(verifier)
        uvicorn.run(app, host="127.0.0.1", port=5000)
    else:
        # Run CLI Admin Dashboard (default)
        print("Users loaded from users.json and organizations.json\n")

        for user in verifier.get_all_users():
            print(f"User ID: {user.id}")
            print(f"Name: {user.full_name}")
            print(f"Email: {user.email}")
            print(f"Phone: {user.phone}")
            print(f"Trust Score: {user.trust_score}")
            print(f"Trust Level: {user.trust_level}")
            print("-" * 40)

        print("\n" + "="*50)
        print("TIP: Run with '--api' flag to start Flask API server")
        print("     python validation1.py --api")
        print("="*50 + "\n")
        input("Press Enter to open Admin Dashboard...")

        dashboard = AdminDashboard(verifier)
        dashboard.run()

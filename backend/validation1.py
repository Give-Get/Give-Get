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


if __name__ == '__main__':
    verifier = VerificationService()
    

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
    input("Press Enter to open Admin Dashboard...")
    
    dashboard = AdminDashboard(verifier)
    dashboard.run()

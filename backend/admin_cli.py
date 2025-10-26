"""
admin_cli.py

CLI Admin Dashboard for user verification management.
Run this script to manage pending users from the terminal.
"""

from validation_service import VerificationService


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
# MAIN ENTRY POINT - CLI Admin Dashboard
# ============================================================================

if __name__ == '__main__':
    # Initialize verification service
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
    print("="*50 + "\n")
    input("Press Enter to open Admin Dashboard...")

    dashboard = AdminDashboard(verifier)
    dashboard.run()


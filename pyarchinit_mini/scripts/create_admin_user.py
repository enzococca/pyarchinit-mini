#!/usr/bin/env python3
"""
Create admin user for PyArchInit-Mini
"""

import os
import sys
from pathlib import Path
import getpass

# Add parent directory to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.user_service import UserService
from pyarchinit_mini.models.user import UserRole


def create_admin_user(interactive=True):
    """Create default admin user"""
    # Find the database
    import site
    site_packages = site.getsitepackages()
    
    possible_paths = [
        Path.home() / ".pyarchinit_mini" / "data" / "pyarchinit_mini.db",
    ]
    
    # Add site-packages paths
    for sp in site_packages:
        possible_paths.append(Path(sp) / "pyarchinit_mini" / "pyarchinit_mini.db")
    
    # Add local development path
    possible_paths.append(Path(__file__).parent.parent / "data" / "pyarchinit_mini.db")
    
    db_path = None
    for path in possible_paths:
        if Path(path).exists():
            db_path = str(path)
            print(f"Found database at: {db_path}")
            break
    
    if not db_path:
        print("Database not found. Please run pyarchinit-mini-setup first.")
        return False
    
    # Create database connection and manager
    from pyarchinit_mini.database.connection import DatabaseConnection
    
    db_url = f"sqlite:///{db_path}"
    connection = DatabaseConnection(db_url)
    db_manager = DatabaseManager(connection)
    
    # Create tables if they don't exist
    connection.initialize_database()
    
    # Create user service
    user_service = UserService(db_manager)
    
    # Check if admin already exists
    existing_admin = user_service.get_user_by_username("admin")
    if existing_admin:
        print("\n✓ Admin user already exists!")
        print(f"  Username: admin")
        print("  Use the existing password to login.")
        return True
    
    # Get admin credentials
    if interactive:
        print("\n" + "="*60)
        print("Create Admin User for PyArchInit-Mini")
        print("="*60)
        print("\nPlease provide admin credentials:")
        
        username = input("Username [admin]: ").strip() or "admin"
        email = input("Email [admin@pyarchinit.local]: ").strip() or "admin@pyarchinit.local"
        
        # Get password securely
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 4:
                print("Password must be at least 4 characters long.")
                continue
            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("Passwords don't match. Try again.")
                continue
            break
            
        full_name = input("Full name [Administrator]: ").strip() or "Administrator"
    else:
        # Non-interactive mode with defaults
        username = "admin"
        email = "admin@pyarchinit.local"
        password = "admin"
        full_name = "Administrator"
    
    # Create admin user
    try:
        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.ADMIN,
            is_superuser=True
        )
        print("\n✓ Admin user created successfully!")
        print(f"  Username: {username}")
        if not interactive:
            print(f"  Password: {password}")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
        else:
            print("\n✓ You can now login with your credentials.")
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False


def main():
    """Entry point for console script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize PyArchInit-Mini with admin user")
    parser.add_argument(
        "--non-interactive", 
        action="store_true", 
        help="Create admin user with default credentials (admin/admin)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("PyArchInit-Mini - Initial Setup")
    print("="*60)
    
    # First run setup if database doesn't exist
    from pyarchinit_mini.scripts.setup_user_env import main as setup_main
    setup_result = setup_main()
    
    if setup_result == 0:
        # Then create admin user
        success = create_admin_user(interactive=not args.non_interactive)
        return 0 if success else 1
    else:
        return setup_result


if __name__ == "__main__":
    sys.exit(main())
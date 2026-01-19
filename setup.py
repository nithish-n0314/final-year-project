#!/usr/bin/env python3
"""
Setup script for AI-Powered Personalized Finance Assistant
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required software is installed"""
    print("Checking prerequisites...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ is required")
        return False
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js {result.stdout.strip()}")
        else:
            print("✗ Node.js is not installed")
            return False
    except FileNotFoundError:
        print("✗ Node.js is not installed")
        return False
    
    # Check PostgreSQL
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PostgreSQL {result.stdout.strip()}")
        else:
            print("✗ PostgreSQL is not installed")
            return False
    except FileNotFoundError:
        print("✗ PostgreSQL is not installed")
        return False
    
    return True

def setup_backend():
    """Set up the Django backend"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # Create virtual environment
    if platform.system() == "Windows":
        venv_activate = os.path.join(backend_dir, 'venv', 'Scripts', 'activate')
        python_cmd = 'python'
    else:
        venv_activate = os.path.join(backend_dir, 'venv', 'bin', 'activate')
        python_cmd = 'python3'
    
    if not os.path.exists(os.path.join(backend_dir, 'venv')):
        if not run_command(f'{python_cmd} -m venv venv', cwd=backend_dir):
            return False
    
    # Install requirements
    if platform.system() == "Windows":
        pip_cmd = os.path.join(backend_dir, 'venv', 'Scripts', 'pip')
    else:
        pip_cmd = os.path.join(backend_dir, 'venv', 'bin', 'pip')
    
    if not run_command(f'{pip_cmd} install -r requirements.txt', cwd=backend_dir):
        return False
    
    # Create .env file if it doesn't exist
    env_file = os.path.join(backend_dir, '.env')
    if not os.path.exists(env_file):
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("""SECRET_KEY=django-insecure-change-this-in-production-12345
DEBUG=True
DB_NAME=finance_assistant
DB_USER=finance_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key-here
""")
        print("✓ Created .env file - Please update with your actual values")
    
    return True

def setup_frontend():
    """Set up the React frontend"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # Install npm dependencies
    if not run_command('npm install', cwd=frontend_dir):
        return False
    
    return True

def create_database_instructions():
    """Print database setup instructions"""
    print("\n📊 Database Setup Instructions:")
    print("Please run the following commands in PostgreSQL:")
    print("1. Connect to PostgreSQL as superuser:")
    print("   psql -U postgres")
    print("\n2. Create database and user:")
    print("   CREATE DATABASE finance_assistant;")
    print("   CREATE USER finance_user WITH PASSWORD 'your_password_here';")
    print("   GRANT ALL PRIVILEGES ON DATABASE finance_assistant TO finance_user;")
    print("   \\q")
    print("\n3. Update the .env file with your actual database password")

def run_migrations():
    """Run Django migrations"""
    print("\n🔄 Running database migrations...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    if platform.system() == "Windows":
        python_cmd = os.path.join(backend_dir, 'venv', 'Scripts', 'python')
    else:
        python_cmd = os.path.join(backend_dir, 'venv', 'bin', 'python')
    
    if not run_command(f'{python_cmd} manage.py makemigrations', cwd=backend_dir):
        return False
    
    if not run_command(f'{python_cmd} manage.py migrate', cwd=backend_dir):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 AI-Powered Personalized Finance Assistant Setup")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing software.")
        sys.exit(1)
    
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        sys.exit(1)
    
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    create_database_instructions()
    
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Set up PostgreSQL database (see instructions above)")
    print("2. Update backend/.env with your actual values")
    print("3. Run migrations: cd backend && python manage.py migrate")
    print("4. Start backend: cd backend && python manage.py runserver")
    print("5. Start frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()
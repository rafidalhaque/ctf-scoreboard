#!/usr/bin/env python3
"""
Database setup utility for CTF Scoreboard
This script helps you set up the Supabase database with the required schema
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def read_schema():
    """Read the schema.sql file"""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: schema.sql not found at {schema_path}")
        sys.exit(1)

def setup_database():
    """Setup the database with the schema"""
    print("=" * 60)
    print("CTF Scoreboard - Database Setup")
    print("=" * 60)
    print()
    
    # Check for required environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: Missing required environment variables")
        print("Please ensure SUPABASE_URL and SUPABASE_KEY are set in .env")
        sys.exit(1)
    
    print(f"Connecting to Supabase at: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Successfully connected to Supabase")
        
        print()
        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print()
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to: SQL Editor")
        print("3. Create a new query")
        print("4. Copy the contents of schema.sql")
        print("5. Paste and run the SQL")
        print()
        print("The schema.sql file is located at:")
        print(f"   {os.path.join(os.path.dirname(__file__), 'schema.sql')}")
        print()
        print("This will create:")
        print("  - scoreboard table with proper indexes")
        print("  - Row Level Security (RLS) policies")
        print("  - Automatic timestamp updates")
        print()
        print("After running the schema, you can start the application with:")
        print("   python app.py")
        print()
        
        # Try to query the table to check if it exists
        try:
            response = supabase.table('scoreboard').select('*').limit(1).execute()
            print("✓ Database table already exists and is accessible!")
            print()
            
            # Show current record count
            count_response = supabase.table('scoreboard').select('*', count='exact').execute()
            if hasattr(count_response, 'count'):
                print(f"Current records in database: {count_response.count}")
        except Exception as e:
            print("⚠ Table 'scoreboard' not found or not accessible")
            print("  Please run the schema.sql in Supabase SQL Editor")
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Supabase: {e}")
        print()
        print("Please check:")
        print("  1. SUPABASE_URL is correct")
        print("  2. SUPABASE_KEY is valid")
        print("  3. Your Supabase project is active")
        return False

def test_connection():
    """Test connection and display database info"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to count records
        response = supabase.table('scoreboard').select('*', count='exact').limit(0).execute()
        
        print()
        print("Database Connection Test: ✓ PASSED")
        if hasattr(response, 'count'):
            print(f"Records in scoreboard: {response.count}")
        return True
        
    except Exception as e:
        print()
        print("Database Connection Test: ✗ FAILED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Check if .env exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found")
        print("Please copy .env.example to .env and fill in your credentials")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    success = setup_database()
    
    if success:
        print()
        print("Would you like to test the database connection? (y/N): ", end='')
        response = input()
        if response.lower() == 'y':
            test_connection()
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)

#!/usr/bin/env python3
"""
Test script to validate the application setup without requiring actual credentials
"""
import sys
import os

# Set mock environment variables for testing
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_key'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import config
        print("✓ config module imported successfully")
        
        import database
        print("✓ database module imported successfully")
        
        import ctfd_client
        print("✓ ctfd_client module imported successfully")
        
        import app
        print("✓ app module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_config_class():
    """Test config class structure"""
    print("\nTesting config class...")
    try:
        from config import Config
        
        # Check required attributes
        required_attrs = [
            'CTFD_EVENT_NAME', 'CTFD_API_URL', 'CTFD_API_KEY',
            'REFRESH_INTERVAL', 'SECRET_KEY', 'ENV', 'HOST', 'PORT',
            'SUPABASE_URL', 'SUPABASE_KEY', 'TOP_TEAMS_COUNT'
        ]
        
        for attr in required_attrs:
            assert hasattr(Config, attr), f"Missing attribute: {attr}"
        
        print("✓ Config class has all required attributes")
        return True
    except Exception as e:
        print(f"✗ Config test error: {e}")
        return False

def test_flask_routes():
    """Test Flask routes are defined"""
    print("\nTesting Flask routes...")
    try:
        from app import app as flask_app
        
        # Get all routes
        routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
        
        required_routes = ['/', '/api/scoreboard', '/health']
        
        for route in required_routes:
            assert route in routes, f"Missing route: {route}"
            print(f"✓ Route {route} found")
        
        return True
    except Exception as e:
        print(f"✗ Flask routes test error: {e}")
        return False

def test_templates_exist():
    """Test that template files exist"""
    print("\nTesting templates...")
    try:
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        required_templates = ['base.html', 'index.html', 'error.html']
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            assert os.path.exists(template_path), f"Missing template: {template}"
            print(f"✓ Template {template} exists")
        
        return True
    except Exception as e:
        print(f"✗ Template test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CTF Scoreboard - Setup Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_class,
        test_flask_routes,
        test_templates_exist
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Application structure is valid.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

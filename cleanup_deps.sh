#!/bin/bash
# cleanup_deps.sh - Clean up deprecated dependencies and reinstall

set -e

echo "=================================================="
echo "CTF Scoreboard - Dependency Cleanup Script"
echo "=================================================="
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠  Warning: You are not in a virtual environment"
    echo "   It's recommended to use a virtual environment"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Step 1: Removing deprecated 'gotrue' package..."
pip uninstall gotrue -y 2>/dev/null || echo "  (gotrue not installed)"

echo ""
echo "Step 2: Upgrading pip..."
pip install --upgrade pip -q

echo ""
echo "Step 3: Installing/upgrading dependencies from requirements.txt..."
pip install -r requirements.txt --upgrade

echo ""
echo "Step 4: Verifying installation..."
echo ""

# Check for gotrue
if pip list | grep -q "^gotrue "; then
    echo "✗ ERROR: gotrue is still installed!"
    echo "  Please manually uninstall it: pip uninstall gotrue -y"
    exit 1
else
    echo "✓ gotrue is not installed (correct)"
fi

# Check for supabase-auth
if pip list | grep -q "^supabase-auth "; then
    echo "✓ supabase-auth is installed (correct)"
else
    echo "✗ ERROR: supabase-auth is not installed!"
    exit 1
fi

# Test import
python3 -c "from supabase import create_client; print('✓ Supabase client imports successfully')" || {
    echo "✗ ERROR: Failed to import supabase client"
    exit 1
}

echo ""
echo "=================================================="
echo "✓ Cleanup complete!"
echo "=================================================="
echo ""
echo "You can now run the application:"
echo "  python app.py"
echo ""

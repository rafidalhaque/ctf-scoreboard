# Upgrade Guide

## Upgrading from supabase 2.4.2 to 2.25.0

If you previously had supabase 2.4.2 installed, you need to remove the deprecated `gotrue` package before upgrading:

```bash
# Remove the old deprecated gotrue package
pip uninstall gotrue -y

# Install/upgrade to the new requirements
pip install -r requirements.txt --upgrade
```

### Why is this necessary?

The old supabase 2.4.2 depended on the deprecated `gotrue` package, which has a bug where `Client.__init__()` gets an unexpected keyword argument 'proxy'. 

The new supabase 2.25.0+ uses `supabase-auth` instead, which fixes this issue. However, if both packages are installed, there can be conflicts.

### Docker Users

If you're using Docker, this is handled automatically by rebuilding the image:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Quick Fix Script

Run this script to clean up and reinstall dependencies:

```bash
#!/bin/bash
# cleanup_and_upgrade.sh

echo "Removing deprecated gotrue package..."
pip uninstall gotrue -y 2>/dev/null || true

echo "Upgrading all dependencies..."
pip install -r requirements.txt --upgrade

echo "Verifying installation..."
python3 -c "from supabase import create_client; print('✓ Supabase client imports successfully')"

echo "✓ Upgrade complete!"
```

### Verifying the Fix

After upgrading, verify that only the correct packages are installed:

```bash
pip list | grep -E "(gotrue|supabase-auth)"
```

You should see:
- `supabase-auth` (correct) ✓
- NO `gotrue` ✗

If you still see `gotrue`, remove it manually:
```bash
pip uninstall gotrue -y
```

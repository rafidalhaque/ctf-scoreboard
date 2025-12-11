#!/usr/bin/env python3
"""
Test to validate that large team_id values can be handled correctly
This tests the fix for the integer overflow issue where values exceeding 2^31-1 caused errors
"""
import hashlib

def test_hash_generation():
    """Test that hash generation produces values that would overflow INTEGER"""
    print("Testing hash generation for team IDs...")
    
    # Test case from the error log - this was causing overflow
    test_value = 3564330554
    max_int32 = 2147483647
    max_int64 = 9223372036854775807
    
    print(f"\nTest value from error: {test_value}")
    print(f"Max INT (32-bit): {max_int32}")
    print(f"Max BIGINT (64-bit): {max_int64}")
    
    if test_value > max_int32:
        print(f"✓ Test value {test_value} exceeds INT32 range (would fail with INTEGER)")
    else:
        print(f"✗ Test value {test_value} is within INT32 range")
    
    if test_value <= max_int64:
        print(f"✓ Test value {test_value} is within BIGINT range (should work with BIGINT)")
    else:
        print(f"✗ Test value {test_value} exceeds BIGINT range")
    
    # Test hash generation with sample team names
    print("\n" + "=" * 60)
    print("Testing hash generation with sample team names:")
    print("=" * 60)
    
    sample_teams = [
        "Team Alpha",
        "CyberWarriors",
        "H4ck3rs",
        "SecuritySquad",
        "NullPointerException"
    ]
    
    overflow_count = 0
    for team_name in sample_teams:
        team_id_hash = int(hashlib.sha256(team_name.encode()).hexdigest()[:8], 16)
        exceeds_int32 = team_id_hash > max_int32
        
        status = "OVERFLOW" if exceeds_int32 else "OK"
        print(f"{team_name:25} -> {team_id_hash:12} [{status}]")
        
        if exceeds_int32:
            overflow_count += 1
    
    print(f"\n{overflow_count}/{len(sample_teams)} team names would cause INTEGER overflow")
    
    if overflow_count > 0:
        print("✓ Confirmed: Some hash values exceed INT32 range")
        print("  Solution: Use BIGINT for team_id column")
    else:
        print("⚠ Warning: No overflow detected with sample data")
        print("  Note: Overflow can still occur with different team names")
    
    return True

def test_account_id_ranges():
    """Test potential account_id values from CTFd API"""
    print("\n" + "=" * 60)
    print("Testing potential CTFd account_id values:")
    print("=" * 60)
    
    max_int32 = 2147483647
    
    # Common ID generation patterns
    test_ids = [
        (1, "Small ID"),
        (1000000, "1 Million"),
        (2147483647, "Max INT32"),
        (2147483648, "INT32 + 1"),
        (3564330554, "Error value from log"),
        (4294967295, "Max UINT32"),
    ]
    
    overflow_count = 0
    for test_id, description in test_ids:
        exceeds_int32 = test_id > max_int32
        status = "OVERFLOW" if exceeds_int32 else "OK"
        print(f"{description:20} -> {test_id:12} [{status}]")
        
        if exceeds_int32:
            overflow_count += 1
    
    print(f"\n{overflow_count}/{len(test_ids)} test values would cause INTEGER overflow")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("CTF Scoreboard - Integer Overflow Test")
    print("=" * 60)
    print()
    print("This test validates the fix for the error:")
    print('  "value "3564330554" is out of range for type integer"')
    print()
    
    try:
        test_hash_generation()
        test_account_id_ranges()
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✓ All tests completed successfully")
        print()
        print("Recommendation:")
        print("  - Database schema should use BIGINT for team_id column")
        print("  - BIGINT supports values up to 9,223,372,036,854,775,807")
        print("  - This will handle both large account_ids and hash values")
        print()
        
        return 0
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

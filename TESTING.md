# Testing Documentation

This document provides comprehensive information about the test suite for the CTF Scoreboard application.

## Overview

The test suite includes comprehensive tests for:
- **CTFd API Client** (`test_ctfd_api.py`) - Tests for API interactions and data fetching
- **Database Operations** (`test_database.py`) - Tests for Supabase integration and data upsertion
- **Integration Tests** (`test_integration.py`) - End-to-end tests for the complete application flow

## Test Structure

### Test Files

1. **`test_ctfd_api.py`** - CTFd API Client Tests
   - Client initialization
   - Scoreboard data fetching with various parameters
   - Error handling (401, 404, 500, timeout, connection errors)
   - Large team ID handling (> 2^31-1)
   - String and dictionary data formats
   - API endpoint construction
   - Authorization header validation

2. **`test_database.py`** - Database Operations Tests
   - Database initialization
   - Upserting with dictionary entries
   - Upserting with string entries
   - Upserting with mixed data types
   - Large team ID handling (BIGINT support)
   - Hash generation for string team names
   - Data retrieval with limits and ordering
   - Clear scoreboard functionality
   - Error handling and edge cases

3. **`test_integration.py`** - Integration Tests
   - End-to-end API to database flow
   - Flask API endpoints (`/health`, `/api/scoreboard`, `/`)
   - Security headers validation
   - Error handling throughout the stack
   - Data integrity through complete flow
   - Configuration validation

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

The test dependencies include:
- `pytest==8.3.4` - Testing framework
- `pytest-mock==3.14.0` - Mocking utilities
- `responses==0.25.3` - HTTP request mocking

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
# Run CTFd API tests only
pytest test_ctfd_api.py

# Run database tests only
pytest test_database.py

# Run integration tests only
pytest test_integration.py
```

### Run Specific Test Class

```bash
# Run only CTFdClient initialization tests
pytest test_ctfd_api.py::TestCTFdClientInitialization

# Run only database upsert tests
pytest test_database.py::TestUpsertScoreboard
```

### Run Specific Test

```bash
# Run a single test
pytest test_ctfd_api.py::TestGetScoreboard::test_get_scoreboard_with_count
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage (if pytest-cov is installed)

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "large_id" in the name
pytest -k large_id

# Run all tests with "error" in the name
pytest -k error
```

## Test Categories

Tests are organized into logical categories:

### Unit Tests
- Individual component testing
- Isolated functionality validation
- Mock external dependencies

### Integration Tests
- End-to-end flow testing
- Multiple component interaction
- Real-world scenario simulation

### API Tests
- HTTP request/response handling
- Authentication and authorization
- Error status codes
- Timeout and connection handling

### Database Tests
- CRUD operations
- Data transformation
- Hash generation
- Large integer handling (BIGINT)

## Key Test Scenarios

### Large Team ID Support
Tests validate that the application correctly handles team IDs exceeding 32-bit integer limits:

```python
# Example: Team ID that would overflow INT32
large_id = 3564330554  # > 2^31-1 (2,147,483,647)
```

These tests ensure:
- Large IDs from CTFd API are preserved
- Database uses BIGINT column type
- Hash generation for strings can produce large values
- Data integrity through entire flow

### Error Handling
Comprehensive error handling tests for:
- API connection failures
- Database query errors
- Invalid data formats
- Timeout scenarios
- HTTP error codes (401, 404, 500)

### Data Format Flexibility
Tests validate handling of different data formats:
- Dictionary entries: `{'account_id': 1, 'name': 'Team', 'score': 100}`
- String entries: `'Team Name'`
- Mixed formats in same dataset
- Empty data and None values

### Security
Tests validate:
- Security headers on all responses
- CSRF protection
- Content Security Policy
- XSS protection headers

## Mock Environment Variables

Tests use the following mock environment variables:

```python
os.environ['CTFD_API_URL'] = 'https://test.ctfd.io/api/v1'
os.environ['CTFD_API_KEY'] = 'test_api_key_12345'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test_supabase_key'
os.environ['FLASK_SECRET_KEY'] = 'test_secret'
```

No actual credentials are required to run tests.

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```bash
# Example CI command
pytest --tb=short --disable-warnings -v
```

## Test Data

### Sample Scoreboard Data

```python
# Dictionary format
[
    {'account_id': 1, 'name': 'Team Alpha', 'score': 1000},
    {'account_id': 2, 'name': 'Team Beta', 'score': 800},
    {'account_id': 3, 'name': 'Team Gamma', 'score': 600}
]

# String format
['Team Alpha', 'Team Beta', 'Team Gamma']
```

### Hash Generation for String Team Names

When team data is provided as strings, a deterministic hash is generated:

```python
import hashlib
team_id = int(hashlib.sha256(team_name.encode()).hexdigest()[:8], 16)
```

This ensures:
- Consistent team_id for same team name
- Unique IDs for different teams
- Support for large integers (BIGINT)

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running from the project root:

```bash
cd /path/to/ctf-scoreboard
pytest
```

### Mock Not Working

Ensure you're using the correct patch path:

```python
# Correct - patches where it's used
@patch('database.create_client')

# Incorrect - patches where it's defined
@patch('supabase.create_client')
```

### Test Database Isolation

Tests use mocks and don't connect to real databases. If you need to test against a real database:

1. Create a test Supabase project
2. Set test environment variables
3. Run specific integration tests

## Adding New Tests

When adding new tests:

1. Follow existing naming conventions
2. Use descriptive test names that explain what is being tested
3. Include docstrings explaining the test purpose
4. Group related tests in classes
5. Use appropriate fixtures for setup/teardown
6. Mock external dependencies (API calls, database operations)

### Example Test Template

```python
class TestNewFeature:
    """Test description of the new feature"""
    
    def test_specific_scenario(self, mock_dependency):
        """Test that specific scenario works correctly"""
        # Arrange
        # Setup test data and mocks
        
        # Act
        # Execute the code being tested
        
        # Assert
        # Verify expected behavior
```

## Test Coverage Goals

Target coverage areas:
- ✅ API client methods
- ✅ Database operations
- ✅ Data transformation logic
- ✅ Error handling
- ✅ Flask endpoints
- ✅ Security headers
- ✅ Configuration validation

## Performance Considerations

The test suite is designed to run quickly:
- Uses mocks to avoid network calls
- No real database connections
- Parallel execution support with pytest-xdist (optional)

To run tests in parallel:

```bash
pip install pytest-xdist
pytest -n auto
```

## Maintenance

Regular maintenance tasks:
1. Update tests when adding new features
2. Review and update mock data to match API changes
3. Add tests for bug fixes to prevent regression
4. Keep test dependencies updated
5. Monitor test execution time

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [responses Documentation](https://github.com/getsentry/responses)
- [CTFd API Documentation](https://docs.ctfd.io/)
- [Supabase Python Client Documentation](https://supabase.com/docs/reference/python/)

## Support

For questions or issues with tests:
1. Check this documentation
2. Review test output and error messages
3. Examine existing tests for examples
4. Open an issue on the repository

#!/bin/bash
# Quick test runner script for CTF Scoreboard

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CTF Scoreboard Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing dependencies...${NC}"
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
fi

# Parse command line arguments
case "${1:-all}" in
    api)
        echo -e "${BLUE}Running CTFd API tests...${NC}"
        pytest test_ctfd_api.py -v
        ;;
    database|db)
        echo -e "${BLUE}Running Database tests...${NC}"
        pytest test_database.py -v
        ;;
    integration|int)
        echo -e "${BLUE}Running Integration tests...${NC}"
        pytest test_integration.py -v
        ;;
    quick|q)
        echo -e "${BLUE}Running quick test (no verbose)...${NC}"
        pytest test_ctfd_api.py test_database.py test_integration.py -q
        ;;
    coverage|cov)
        echo -e "${BLUE}Running tests with coverage...${NC}"
        if ! command -v pytest-cov &> /dev/null; then
            echo -e "${YELLOW}Installing pytest-cov...${NC}"
            pip install pytest-cov -q
        fi
        pytest test_ctfd_api.py test_database.py test_integration.py --cov=. --cov-report=term --cov-report=html
        echo -e "${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    help|h)
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all          Run all tests (default)"
        echo "  api          Run CTFd API tests only"
        echo "  database|db  Run database tests only"
        echo "  integration|int  Run integration tests only"
        echo "  quick|q      Run all tests without verbose output"
        echo "  coverage|cov Run tests with coverage report"
        echo "  help|h       Show this help message"
        echo ""
        exit 0
        ;;
    *)
        echo -e "${BLUE}Running all tests...${NC}"
        pytest test_ctfd_api.py test_database.py test_integration.py -v
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Tests completed!${NC}"
echo -e "${GREEN}========================================${NC}"

#!/bin/bash

# Tamil Video Generator - Installation Verification Script
# This script verifies that all dependencies are properly installed

echo "=========================================="
echo "Tamil Video Generator - Installation Check"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ((FAILED++))
    fi
}

# Function to check Python module
check_python_module() {
    python3 -c "import $1" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Python module '$1' is installed"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Python module '$1' is NOT installed"
        ((FAILED++))
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File '$1' exists"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} File '$1' NOT found"
        ((FAILED++))
    fi
}

echo "1. System Dependencies"
echo "====================="
check_command "python3"
check_command "ffmpeg"
check_command "convert"  # ImageMagick

echo ""
echo "2. Python Modules"
echo "================="
check_python_module "moviepy"
check_python_module "pyttsx3"
check_python_module "PIL"
check_python_module "numpy"
check_python_module "requests"
check_python_module "apscheduler"
check_python_module "google"

echo ""
echo "3. Project Files"
echo "================"
check_file "main.py"
check_file "scheduler.py"
check_file "content_generator.py"
check_file "tts_generator.py"
check_file "video_creator.py"
check_file "youtube_uploader.py"
check_file "database.py"
check_file "config.json"
check_file "requirements.txt"
check_file "README.md"
check_file "SETUP.md"
check_file "API.md"

echo ""
echo "4. Optional Files"
echo "================="
if [ -f "credentials.json" ]; then
    echo -e "${GREEN}✓${NC} YouTube credentials found"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} YouTube credentials NOT found (needed for publishing)"
fi

if [ -f "token.pickle" ]; then
    echo -e "${GREEN}✓${NC} YouTube token found"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} YouTube token NOT found (will be created on first run)"
fi

echo ""
echo "5. Directories"
echo "=============="
if [ -d "audio_output" ]; then
    echo -e "${GREEN}✓${NC} audio_output directory exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} audio_output directory NOT found (will be created)"
fi

if [ -d "videos" ]; then
    echo -e "${GREEN}✓${NC} videos directory exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} videos directory NOT found (will be created)"
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Get YouTube credentials from Google Cloud Console"
    echo "2. Save as credentials.json"
    echo "3. Run: python main.py --mode generate"
    echo "4. Run: python main.py --mode start"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Install FFmpeg: brew install ffmpeg"
    echo "- Install ImageMagick: brew install imagemagick"
    echo "- Install Python modules: pip install -r requirements.txt"
    exit 1
fi

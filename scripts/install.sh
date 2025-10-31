#!/bin/bash

# Use Case Simulator Installation Script
# This script installs the Use Case Simulator and its dependencies

set -e  # Exit on any error

echo "========================================"
echo "  Use Case Simulator Installation"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $PYTHON_VERSION is not supported."
    echo "Please upgrade to Python $REQUIRED_VERSION or higher."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed."
    echo "Please install pip3 to continue."
    exit 1
fi

echo "✅ pip3 detected"

# Create virtual environment (optional)
read -p "Create a virtual environment? (recommended) [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv usecase_env
    source usecase_env/bin/activate
    echo "✅ Virtual environment created and activated"
    PIP_CMD="usecase_env/bin/pip"
else
    PIP_CMD="pip3"
fi

# Install the package
echo "📦 Installing Use Case Simulator..."
if [ -f "pyproject.toml" ]; then
    # Install in development mode if pyproject.toml exists (development install)
    $PIP_CMD install -e .
else
    # Install from PyPI
    $PIP_CMD install usecasesimulator
fi

echo "✅ Installation completed successfully!"

# Test the installation
echo
echo "🧪 Testing installation..."
python3 -c "
try:
    from modules.core.simulation_engine import SimulationEngine
    print('✅ Core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo
echo "🎉 Installation complete!"
echo
echo "To start playing:"
if [[ -d "usecase_env" ]]; then
    echo "  source usecase_env/bin/activate"
fi
echo "  python -m modules.ui.console_ui"
echo
echo "For help and documentation:"
echo "  Visit: https://github.com/ShadSafa/UseCaseSimulator"
echo "  Quick start: docs/quick_start.md"
echo "  Full tutorial: docs/tutorial.md"
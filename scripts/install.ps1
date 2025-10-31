# Use Case Simulator Installation Script for Windows
# This script installs the Use Case Simulator and its dependencies

param(
    [switch]$NoVirtualEnv,
    [switch]$Quiet
)

# Configuration
$MIN_PYTHON_VERSION = "3.8"
$PACKAGE_NAME = "usecasesimulator"
$VENV_NAME = "usecase_env"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Exit-WithError {
    param([string]$Message)
    Write-ColorOutput "❌ Error: $Message" "Red"
    exit 1
}

function Test-PythonVersion {
    try {
        $pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
        Write-ColorOutput "✅ Python $pythonVersion detected" "Green"

        # Compare versions
        $currentVersion = [version]$pythonVersion
        $requiredVersion = [version]$MIN_PYTHON_VERSION

        if ($currentVersion -lt $requiredVersion) {
            Exit-WithError "Python $pythonVersion is not supported. Please upgrade to Python $MIN_PYTHON_VERSION or higher."
        }
    }
    catch {
        Exit-WithError "Python is not installed or not in PATH. Please install Python $MIN_PYTHON_VERSION or higher from https://python.org"
    }
}

function Test-Pip {
    try {
        $pipVersion = pip --version 2>$null
        Write-ColorOutput "✅ pip detected" "Green"
    }
    catch {
        Exit-WithError "pip is not installed. Please install pip to continue."
    }
}

function Create-VirtualEnvironment {
    if (-not $NoVirtualEnv) {
        Write-ColorOutput "📦 Creating virtual environment..." "Yellow"
        python -m venv $VENV_NAME

        if (Test-Path "$VENV_NAME\Scripts\activate") {
            Write-ColorOutput "✅ Virtual environment created" "Green"
            return $true
        } else {
            Write-ColorOutput "⚠️ Virtual environment creation failed, continuing with system Python" "Yellow"
            return $false
        }
    }
    return $false
}

function Install-Package {
    param([bool]$UseVenv)

    Write-ColorOutput "📦 Installing Use Case Simulator..." "Yellow"

    if ($UseVenv) {
        & "$VENV_NAME\Scripts\python.exe" -m pip install --upgrade pip
        if (Test-Path "pyproject.toml") {
            # Development install
            & "$VENV_NAME\Scripts\python.exe" -m pip install -e .
        } else {
            # Install from PyPI
            & "$VENV_NAME\Scripts\python.exe" -m pip install $PACKAGE_NAME
        }
    } else {
        python -m pip install --upgrade pip
        if (Test-Path "pyproject.toml") {
            # Development install
            python -m pip install -e .
        } else {
            # Install from PyPI
            python -m pip install $PACKAGE_NAME
        }
    }

    Write-ColorOutput "✅ Installation completed successfully!" "Green"
}

function Test-Installation {
    Write-ColorOutput "🧪 Testing installation..." "Yellow"

    $testScript = @"
try:
    from modules.core.simulation_engine import SimulationEngine
    print('SUCCESS: Core modules imported successfully')
except ImportError as e:
    print(f'ERROR: {e}')
    exit(1)
"@

    if ($UseVenv) {
        $result = & "$VENV_NAME\Scripts\python.exe" -c $testScript
    } else {
        $result = python -c $testScript
    }

    if ($result -match "SUCCESS") {
        Write-ColorOutput "✅ Core modules imported successfully" "Green"
    } else {
        Write-ColorOutput "❌ Import test failed" "Red"
        exit 1
    }
}

# Main installation process
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "  Use Case Simulator Installation" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

# Pre-installation checks
Test-PythonVersion
Test-Pip

# Virtual environment setup
$useVenv = Create-VirtualEnvironment

# Package installation
Install-Package -UseVenv $useVenv

# Installation testing
Test-Installation

# Success message
Write-ColorOutput "" "White"
Write-ColorOutput "🎉 Installation complete!" "Green"
Write-ColorOutput "" "White"
Write-ColorOutput "To start playing:" "White"
if ($useVenv) {
    Write-ColorOutput "  $VENV_NAME\Scripts\activate" "Yellow"
}
Write-ColorOutput "  python -m modules.ui.console_ui" "White"
Write-ColorOutput "" "White"
Write-ColorOutput "For help and documentation:" "White"
Write-ColorOutput "  Visit: https://github.com/ShadSafa/UseCaseSimulator" "Blue"
Write-ColorOutput "  Quick start: docs\quick_start.md" "Blue"
Write-ColorOutput "  Full tutorial: docs\tutorial.md" "Blue"
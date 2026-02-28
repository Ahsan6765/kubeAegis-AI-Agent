#!/bin/bash
# kubeAegis AI Agent - Setup and Activation Script
# This script sets up and activates the development environment

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         kubeAegis AI Agent - Environment Setup             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✓ Virtual environment activated"

echo ""
echo "📚 Installing dependencies..."
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -q -r "$REQUIREMENTS_FILE"
    echo "✓ Dependencies installed successfully"
else
    echo "⚠️  requirements.txt not found!"
    exit 1
fi

echo ""
echo "✨ Testing installation..."
python -c "import yaml, click; print('✓ All imports successful')"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║               Environment Ready to Use!                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Available commands:"
echo "  python cli.py validate <file>    - Validate a manifest"
echo "  python cli.py analyze <file>     - Analyze a manifest"
echo "  python cli.py health             - Check agent health"
echo "  python cli.py config             - View configuration"
echo "  python cli.py --help             - Show all commands"
echo ""
echo "Example:"
echo "  python cli.py validate pod.yaml"
echo ""

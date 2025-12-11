echo "✅ Activating virtual environment..."
echo "📥 Installing dependencies..."
echo ""
echo "✅ Development environment ready!"
echo ""
echo "🚀 To run the crawler locally:"
echo "   cd crawler"
echo "   scrapy crawl universal -a sector=Energy_Venezuela"
echo ""
echo "📝 To test with local Scrapy shell:"
echo "   cd crawler"
echo "   scrapy shell https://example.com"
echo ""
#!/bin/bash
# Development script for local crawler testing

set -e
echo "🧪 Setting up development environment..."

# Detect available Python executable
PYTHON_CMD=""
for cmd in python3.11 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3.11+ not found. Please install Python 3.11 or newer and re-run."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment using $PYTHON_CMD..."
    "$PYTHON_CMD" -m venv venv
fi

# Activate virtual environment (cross-platform)
echo "✅ Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    # Unix-like
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
else
    echo "⚠️  Virtual environment created at ./venv but activation script not found."
    echo "Please activate manually and re-run:"
    echo "  On macOS/Linux: source venv/bin/activate"
    echo "  On Windows (Git Bash): source venv/Scripts/activate"
    exit 1
fi

# Upgrade pip and install dependencies
echo "📥 Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r crawler/requirements.txt

echo ""
echo "✅ Development environment ready!"
echo ""
echo "🚀 To run the crawler locally:"
echo "   cd crawler"
echo "   scrapy crawl universal -a sector=Energy_Venezuela"
echo ""
echo "📝 To test with local Scrapy shell:"
echo "   cd crawler"
echo "   scrapy shell https://example.com"
echo ""

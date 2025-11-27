#!/bin/bash

echo "🚀 Setting up Motif React App..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js first:"
    echo "  brew install node"
    echo "  or visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create public/data directory if it doesn't exist
mkdir -p public/data

# Copy data files
echo "📁 Copying data files..."
if [ -d "../data" ]; then
    cp ../data/*.json public/data/ 2>/dev/null || echo "⚠️  Some JSON files not found"
    cp ../facebook_weighted_filtered.csv public/ 2>/dev/null || echo "⚠️  CSV file not found"
    echo "✅ Data files copied"
else
    echo "⚠️  ../data directory not found. Please copy data files manually to public/data/"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The app will be available at: http://localhost:3000"

#!/bin/bash

# Fix SSL Certificate Issues on macOS
# This script installs SSL certificates for Python

echo "🔧 Fixing SSL Certificate Issues..."
echo ""

# Method 1: Try to run Python's built-in certificate installer
if [ -d "/Applications/Python 3.11" ]; then
    echo "Found Python 3.11, running certificate installer..."
    "/Applications/Python 3.11/Install Certificates.command" 2>/dev/null && echo "✅ System certificates installed"
fi

# Method 2: Ensure certifi is installed in venv
echo ""
echo "Installing certifi in virtual environment..."
source venv/bin/activate
pip install --upgrade certifi
echo "✅ Certifi installed"

# Method 3: Create symbolic link (fallback)
echo ""
echo "Creating SSL certificate symlink..."
CERT_PATH=$(python -c "import certifi; print(certifi.where())")
PYTHON_SSL_CERT="/Library/Frameworks/Python.framework/Versions/3.11/etc/openssl/cert.pem"

if [ -f "$CERT_PATH" ]; then
    echo "Certifi certificates found at: $CERT_PATH"

    # Create directory if it doesn't exist
    sudo mkdir -p "$(dirname "$PYTHON_SSL_CERT")" 2>/dev/null || mkdir -p "$(dirname "$PYTHON_SSL_CERT")"

    # Create symlink
    if sudo ln -sf "$CERT_PATH" "$PYTHON_SSL_CERT" 2>/dev/null; then
        echo "✅ Certificate symlink created"
    else
        echo "⚠️  Could not create symlink (may need sudo)"
    fi
fi

echo ""
echo "========================================"
echo "✅ SSL certificate fix complete!"
echo ""
echo "Now try running the bot:"
echo "  ./run.sh"
echo "========================================"

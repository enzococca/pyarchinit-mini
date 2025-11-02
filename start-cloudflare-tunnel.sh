#!/bin/bash
# Start Cloudflare Tunnel for PyArchInit-Mini Web Interface
# This creates a quick tunnel with an auto-generated .trycloudflare.com URL

# Check if web interface is running on port 5001
if ! lsof -i :5001 > /dev/null 2>&1; then
    echo "⚠️  Web interface not running on port 5001!"
    echo "Start it first with: DATABASE_URL=\"sqlite:///data/pyarchinit_tutorial.db\" pyarchinit-mini-web"
    exit 1
fi

echo "🚀 Starting Cloudflare Tunnel for PyArchInit-Mini..."
echo "📍 Local service: http://localhost:5001"
echo ""

# Start tunnel (URL will be displayed in output)
cloudflared tunnel --url http://localhost:5001

# Note: The tunnel will generate a different .trycloudflare.com URL each time
# For a permanent URL, configure a named tunnel with a Cloudflare domain

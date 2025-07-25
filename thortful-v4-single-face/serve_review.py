#!/usr/bin/env python3
"""
Simple HTTP Server for Thortful Test Results Review
Serves the HTML review page and associated files
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def start_server(port=8080):
    """Start the HTTP server for the review page"""
    
    # Change to the current directory to serve files
    os.chdir(Path(__file__).parent)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌐 Starting Thortful Review Server")
            print(f"📊 Review page: http://localhost:{port}/thortful_review.html")
            print(f"🔗 Opening in browser...")
            print(f"📁 Serving files from: {Path.cwd()}")
            print("   - source-images/")
            print("   - target-images/") 
            print("   - results/")
            print("   - logs/")
            print(f"🛑 Press Ctrl+C to stop server")
            print("=" * 60)
            
            # Open browser automatically
            webbrowser.open(f'http://localhost:{port}/thortful_review.html')
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Usage: python serve_review.py [port_number]")
            sys.exit(1)
    
    start_server(port)
#!/usr/bin/env python3
"""
Simple HTTP server to serve the persistence diagram visualizer
"""
import http.server
import socketserver
import webbrowser
import os
import sys

def serve_files(port=8080):
    """Start a simple HTTP server to serve the persistence visualizer"""
    
    # Change to the current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Serving persistence visualizer at http://localhost:{port}")
            print(f"Open http://localhost:{port}/persistence_visualizer.html in your browser")
            print("Press Ctrl+C to stop the server")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}/persistence_visualizer.html')
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is already in use. Trying port {port + 1}...")
            serve_files(port + 1)
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    serve_files()
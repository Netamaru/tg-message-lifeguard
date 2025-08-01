#!/usr/bin/env python3
"""
Simple HTTP server to serve the Telegram message viewer.
This is needed because browsers don't allow loading local JSON files directly.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json
from pathlib import Path
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("⚠️  config.json not found. Using default credentials.")
        return {"username": "admin", "password": "default"}
    except json.JSONDecodeError:
        print("⚠️  Invalid config.json format. Using default credentials.")
        return {"username": "admin", "password": "default"}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Message Viewer Server')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode (no browser auto-open)')
    parser.add_argument('--host', default='localhost', help='Host to bind to (use 0.0.0.0 for all interfaces)')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
    args = parser.parse_args()
    
    PORT = args.port
    HOST = args.host
    
    # Change to the directory containing the viewer
    viewer_dir = Path(__file__).parent
    os.chdir(viewer_dir)
    
    print(f"🚀 Starting Telegram Message Viewer...")
    print(f"📁 Serving from: {viewer_dir}")
    if args.headless:
        print(f"🖥️  Running in headless mode")
    print(f"🌐 Server will be available at: http://{HOST}:{PORT}")
    
    # Check if backup folder exists
    backup_path = viewer_dir / "backup"
    if backup_path.exists():
        print(f"✅ Backup folder found: {backup_path}")
        
        # List available groups and threads
        groups = [d for d in backup_path.iterdir() if d.is_dir()]
        if groups:
            print(f"📂 Available groups:")
            for group in groups:
                print(f"   - Group {group.name}")
                threads = [d for d in group.iterdir() if d.is_dir() and d.name.startswith('thread_')]
                if threads:
                    print(f"     Threads: {', '.join([t.name.replace('thread_', '') for t in threads])}")
        else:
            print("⚠️  No backup groups found in backup folder")
    else:
        print(f"⚠️  Backup folder not found: {backup_path}")
        print("   Make sure you've run the backup script first!")
    
    print(f"\n{'='*50}")
    print(f"Instructions:")
    print(f"1. The browser will open automatically")
    print(f"2. Enter your Group ID (e.g., 1002074491972)")
    print(f"3. Select a Thread ID from the dropdown")
    print(f"4. Click 'Load Messages'")
    print(f"5. Use Ctrl+C to stop the server")
    print(f"{'='*50}\n")

    # Load config once at startup
    config = load_config()
    
    class AuthHandler(SimpleHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()
            
        def do_AUTHHEAD(self):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Telegram Viewer"')
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            # Block access to config files
            if self.path.endswith('/config.json') or self.path.endswith('/users.json'):
                self.send_error(403, "Access denied")
                return
            
            # Check for authorization header
            if self.headers.get('Authorization') is None:
                self.do_AUTHHEAD()
                self.wfile.write(b'Authentication required')
                return
            
            # Decode and verify credentials
            auth_header = self.headers.get('Authorization')
            if not self.verify_credentials(auth_header):
                self.do_AUTHHEAD()
                self.wfile.write(b'Invalid credentials')
                return
                
            # Continue with normal file serving
            super().do_GET()
        
        def verify_credentials(self, auth_header):
            # Extract base64 encoded credentials
            encoded_creds = auth_header.split(' ')[1]
            decoded_creds = base64.b64decode(encoded_creds).decode('utf-8')
            username, password = decoded_creds.split(':')
            
            # Check against credentials from config.json
            return username == config.get("username", "admin") and password == config.get("password", "default")

    try:
        with socketserver.TCPServer((HOST, PORT), AuthHandler) as httpd:
            print(f"🎉 Server started successfully!")
            
            if not args.headless:
                # Open browser automatically only if not headless
                try:
                    webbrowser.open(f'http://{HOST}:{PORT}/index.html')
                    print(f"🌐 Opening browser...")
                except Exception as e:
                    print(f"⚠️  Could not open browser automatically: {e}")
                    print(f"   Please open http://{HOST}:{PORT}/index.html manually")
            else:
                print(f"🌐 Access the viewer at: http://{HOST}:{PORT}/index.html")
                if HOST == "0.0.0.0":
                    print(f"   Or use your server's IP address: http://YOUR_SERVER_IP:{PORT}/index.html")
                print(f"📝 Credentials loaded from config.json: username='{config.get('username', 'admin')}'")
            
            print(f"\n⏳ Server running... Press Ctrl+C to stop")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print(f"   Try closing other applications or use a different port")
            print(f"   You can also try: python -m http.server 8001")
        else:
            print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
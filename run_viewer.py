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
from pathlib import Path

def main():
    PORT = 8000
    
    # Change to the directory containing the viewer
    viewer_dir = Path(__file__).parent
    os.chdir(viewer_dir)
    
    print(f"🚀 Starting Telegram Message Viewer...")
    print(f"📁 Serving from: {viewer_dir}")
    print(f"🌐 Server will be available at: http://localhost:{PORT}")
    
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

    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow local file access
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def log_message(self, format, *args):
            # Custom logging to show what's being accessed
            if not self.path.endswith(('.ico', '.css', '.js')):
                print(f"📥 {self.command} {self.path}")

    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🎉 Server started successfully!")
            
            # Open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}/telegram_viewer.html')
                print(f"🌐 Opening browser...")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please open http://localhost:{PORT}/telegram_viewer.html manually")
            
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
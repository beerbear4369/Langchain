#!/usr/bin/env python3
"""
Startup script for Kuku Coach API
Usage: python start_api.py [--port PORT] [--reload]
"""
import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Start Kuku Coach API server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("--reload", "-r", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    # Check if required dependencies are installed
    try:
        import fastapi
        import uvicorn
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if config is available
    if not os.path.exists("config.py"):
        print("Warning: config.py not found. Make sure your OpenAI API key is configured.")
    
    # Build uvicorn command
    cmd = [
        "uvicorn", 
        "app:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    print(f"Starting Kuku Coach API on {args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/docs")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
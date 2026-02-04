"""
Run local FastAPI server for testing
This simulates your Vercel deployment locally
"""
import uvicorn
import sys
import os

# Set environment variables for local testing
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["API_KEY"] = "scamshield_2026_secure_key"

print("=" * 70)
print("STARTING LOCAL SERVER FOR TESTING")
print("=" * 70)
print()
print("Server will run at: http://localhost:8000")
print("API endpoint: http://localhost:8000/api/honeypot")
print("API Key: scamshield_2026_secure_key")
print()
print("To test:")
print("1. Keep this server running")
print("2. Open another terminal")
print("3. Run: python test_local_debug.py")
print()
print("Press Ctrl+C to stop the server")
print("=" * 70)
print()

if __name__ == "__main__":
    try:
        # Import the FastAPI app from main.py
        from main import app
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError starting server: {str(e)}")
        print("\nMake sure you have installed dependencies:")
        print("pip install -r requirements.txt")

"""
Vercel entrypoint for the GenAI Data Analytics Platform.
This file serves as the entrypoint for Vercel's Python runtime.
"""

# Import the FastAPI app from backend
from backend.main import app

# For Vercel serverless, we need to export 'app'
# The app is already defined in main.py

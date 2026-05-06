"""
Vercel Serverless Function Handler for FastAPI
This provides a handler for Vercel's serverless runtime.
"""

import os

# For local development, we can run the app directly
if os.environ.get("VERCEL_ENV") is None:
    import uvicorn
    from main import app

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# Vercel deployment uses the FastAPI app from main
from main import app

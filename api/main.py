import sys
import os

# Add the BackEND directory to the Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'BackEND')
sys.path.insert(0, backend_path)

# Import the FastAPI app
from main import app

# Vercel serverless function handler
handler = app


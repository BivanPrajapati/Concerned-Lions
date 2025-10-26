from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import Logic as lg  # Your Logic.py module

app = FastAPI()

# --- Enable CORS for frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Path to save PNGs ---
frontend_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FrontEnd", "src"))
os.makedirs(frontend_src_dir, exist_ok=True)

# --- Serve static files ---
app.mount("/static", StaticFiles(directory=frontend_src_dir), name="static")
from fastapi.responses import StreamingResponse

@app.post("/generate-tree")
async def generate_tree(course_name: str = Form(...)):
    try:
        # Generate PNG in memory
        buf = lg.visualize_full_prereq_tree(course_name, return_buffer=True)

        # Return buffer as image/png
        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        print("❌ Error generating tree:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

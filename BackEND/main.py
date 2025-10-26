# === main.py ===

from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import Logic as lg  # Your logic module that generates PNGs

app = FastAPI()

# --- CORS for frontend development ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static files ---
frontend_static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FrontEnd", "src"))
app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")

# --- Serve frontend HTML ---
@app.get("/")
async def root():
    html_path = os.path.join(frontend_static_dir, "index.html")
    if not os.path.exists(html_path):
        return JSONResponse({"error": "index.html not found in static folder"}, status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

# --- Generate prerequisite tree PNG ---
@app.post("/generate-tree")
async def generate_tree(course_name: str = Form(...)):
    try:
        # Unique filename per course
        safe_name = course_name.replace(" ", "_").upper()
        output_path = os.path.join(frontend_static_dir, f"prereq_tree_{safe_name}.png")

        # Generate the PNG
        lg.visualize_full_prereq_tree(course_name, save_path=output_path)

        # Wait until PNG exists and is non-empty (max 60 seconds)
        timeout = 60  # seconds
        interval = 0.5
        waited = 0
        while not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            time.sleep(interval)
            waited += interval
            if waited >= timeout:
                return JSONResponse({
                    "success": False,
                    "error": f"PNG for {course_name} not ready after {timeout} seconds"
                }, status_code=500)

        # Return the fully ready PNG
        return FileResponse(output_path, media_type="image/png")

    except Exception as e:
        print("❌ Error generating tree:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

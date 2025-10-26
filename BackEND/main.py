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

# --- Generate prerequisite tree and return PNG directly ---
@app.post("/generate-tree")
async def generate_tree(course_name: str = Form(...)):
    try:
        safe_name = course_name.replace(" ", "_").upper()
        output_filename = f"{safe_name}_prereq_tree.png"
        output_path = os.path.join(frontend_src_dir, output_filename)

        # Generate the PNG
        lg.visualize_full_prereq_tree(course_name, save_path=output_path)

        # Wait until file exists and is non-empty
        timeout = 10
        interval = 0.2
        waited = 0
        while not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            time.sleep(interval)
            waited += interval
            if waited >= timeout:
                return JSONResponse({"success": False, "error": "PNG generation timeout"}, status_code=500)

        # Return PNG directly
        return FileResponse(
            output_path,
            media_type="image/png",
            filename=output_filename,
            headers={"Cache-Control": "no-store"}  # prevent caching
        )

    except Exception as e:
        print("Error:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

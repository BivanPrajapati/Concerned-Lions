from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import Logic as lg  # Your module to generate the PNG

app = FastAPI()

# --- CORS for frontend dev ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths ---
FRONTEND_SRC = os.path.join(os.path.dirname(__file__), "frontend", "src")
PNG_NAME = "prereq_tree.png"
PNG_PATH = os.path.join(FRONTEND_SRC, PNG_NAME)

# --- Generate tree ---
@app.post("/generate-tree")
async def generate_tree(course_name: str = Form(...)):
    try:
        lg.visualize_full_prereq_tree(course_name, save_path=PNG_PATH)
        # Return URL for JS to open
        return {"url": "/prereq-tree-file"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- Serve the PNG ---
@app.get("/prereq-tree-file")
async def serve_prereq_tree():
    if not os.path.exists(PNG_PATH):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(PNG_PATH, media_type="image/png")

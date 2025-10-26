from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import Logic as lg

app = FastAPI(title="BU Course Info API", version="1.0")

# --- Path to FrontEnd/src relative to main.py ---
FRONTEND_SRC = os.path.join(os.path.dirname(__file__), "..", "FrontEnd", "src")

# Serve static files (PNG)
app.mount("/static", StaticFiles(directory=FRONTEND_SRC), name="static")

@app.post("/generate-tree")
def generate_tree(course_name: str = Form(...)):
    try:
        save_path = os.path.join(FRONTEND_SRC, "prereq_tree.png")
        lg.visualize_full_prereq_tree(course_name, return_buffer=False, save_path=save_path)
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tree: {str(e)}")


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
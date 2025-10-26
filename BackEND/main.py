from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import Web_Scraping as ws
import Logic as lg

app = FastAPI(title="BU Course Info API", version="1.0")

class CourseRequest(BaseModel):
    course_name: str

@app.post("/course-tree")
def course_tree(request: CourseRequest):
    try:
        course_name = request.course_name
        img_buf = lg.visualize_full_prereq_tree(course_name)
        return StreamingResponse(img_buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tree: {str(e)}")

@app.get("/course-tree")
def course_tree_get(course_name: str):
    try:
        img_buf = lg.visualize_full_prereq_tree(course_name)
        return StreamingResponse(img_buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tree: {str(e)}")

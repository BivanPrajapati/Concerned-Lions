from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import Web_Scraping as ws
import Logic as lg
from fastapi.middleware.cors import CORSMiddleware

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
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/course-info")
def course_info(request: CourseRequest):
    return get_course_data(request.course_name)


@app.get("/course-info")
def course_info_get(course_name: str):
    return get_course_data(course_name)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


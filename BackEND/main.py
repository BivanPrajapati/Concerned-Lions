from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import Web_Scraping as ws
import Logic as lg
app = FastAPI(title="BU Course Info API", version="1.0")


class CourseRequest(BaseModel):
    course_name: str


def get_course_data(course_name: str):
    """
    Fetch course info, prerequisites, and Hub areas in clean string format.
    """
    try:
        normalized = ws.normalize_course(course_name)
        if not normalized:
            raise HTTPException(status_code=400, detail=f"Cannot normalize course '{course_name}'")

        prereqs_str = lg.classes_used(course_name)  # returns string of prereqs
        hubs_str = lg.hubs_used(course_name)        # returns string of Hub areas

        return {
            "course_name": normalized,
            "prerequisites": prereqs_str if prereqs_str else "No prerequisites",
            "hub_areas": hubs_str if hubs_str else "No Hub requirement"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/course-info")
def course_info(request: CourseRequest):
    return get_course_data(request.course_name)


@app.get("/course-info")
def course_info_get(course_name: str):
    return get_course_data(course_name)

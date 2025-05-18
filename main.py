from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import metrics.evaluation as evaluation

app = FastAPI()

class EvaluationRequest(BaseModel):
    course_text: str
    reference_text: Optional[str] = None
    thresholds: Optional[dict] = None 

@app.post("/evaluate")
def evaluate_course_endpoint(request: EvaluationRequest):
    try:
        result = evaluation.evaluate_course(request.course_text, request.reference_text)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from backend.app.matching.scorer import score_match
from backend.app.parsing.resume_parser import extract_text_from_pdf

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "resume matcher API is running"}

class MatchRequest(BaseModel):
    resume_text: str
    jd_text: str

@app.post("/match")
def match(request: MatchRequest):
    result = score_match(request.resume_text, request.jd_text)
    return result

@app.post("/match-pdf")
async def match_pdf(jd_text: str = Form(...), resume_file: UploadFile = File(...)):
    file_bytes = await resume_file.read()
    resume_text = extract_text_from_pdf(file_bytes)
    result = score_match(resume_text, jd_text)
    result["extracted_resume_text"] = resume_text  # helpful for debugging, remove later
    return result
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.matching.scorer import score_match
from backend.app.parsing.resume_parser import extract_text_from_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return result
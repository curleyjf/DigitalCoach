from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    jobs,
    create_answer,
    big_five,
    star_feedback,
    audio_analysis,
)


api_description = """
This API provides a simple interface to the various ML models used in Digital Coach. 
## Video Transcript 
AssemblyAI provides the simple transcription service. 
## Feedback
Provided feedback is Big Five Scores, Star Scores, competency scores, and statistical feedback.  
"""

app = FastAPI(
    title="MLAPI",
    description=api_description,
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Digital Coach API, please see `/docs` for more information."
    }


# Add routes here
app.include_router(jobs.router)
app.include_router(create_answer.router)
app.include_router(big_five.router)
app.include_router(star_feedback.router)
app.include_router(audio_analysis.router)

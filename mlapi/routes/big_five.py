from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from utils.logger_config import get_logger
from tasks.bigfivescore import big_five_feedback

logger = get_logger(__name__)

router = APIRouter(prefix="/api/big_five", tags=["big_five"])


class BigFiveRequest(BaseModel):
    """
    Request model for Big Five scores
    """

    o: float  # Openness
    c: float  # Conscientiousness
    e: float  # Extraversion
    a: float  # Agreeableness
    n: float  # Neuroticism


class BigFiveResponse(BaseModel):
    """
    Response model for Big Five scores with feedback
    """

    feedback: List[str]


@router.post("/feedback", response_model=BigFiveResponse)
async def get_big_five_feedback(request: BigFiveRequest):
    """
    Generate feedback based on Big Five personality test scores

    - **o**: Openness score (typically 0-7)
    - **c**: Conscientiousness score (typically 0-7)
    - **e**: Extraversion score (typically 0-7)
    - **a**: Agreeableness score (typically 0-7)
    - **n**: Neuroticism score (typically 0-7)

    Returns personalized feedback based on Big Five personality traits.
    """
    try:
        scores = {
            "o": request.o,
            "c": request.c,
            "e": request.e,
            "a": request.a,
            "n": request.n,
        }

        feedback = big_five_feedback(scores)
        return {"feedback": feedback}
    except Exception as e:
        logger.error(f"Error generating Big Five feedback: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Big Five feedback: {str(e)}"
        )

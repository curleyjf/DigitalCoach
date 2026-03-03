from fastapi import APIRouter, HTTPException
from schemas import BigFiveResponse, BigFiveRequest
from utils.logger_config import get_logger
from tasks.bigfivescore import big_five_feedback

logger = get_logger(__name__)

router = APIRouter(prefix="/api/big_five", tags=["big_five"])

# POST /api/big_five/feedback
@router.post("/feedback", response_model=BigFiveResponse)
async def get_big_five_feedback(request: BigFiveRequest):
    """
    Generate feedback based on Big Five personality test scores

    - **o**: Openness score (typically 0-100)
    - **c**: Conscientiousness score (typically 0-100)
    - **e**: Extraversion score (typically 0-100)
    - **a**: Agreeableness score (typically 0-100)
    - **n**: Neuroticism score (typically 0-100)

    Returns personalized feedback based on Big Five personality traits.
    """
    # Extract scores from the request
    scores = {
        "o": request.o,
        "c": request.c,
        "e": request.e,
        "a": request.a,
        "n": request.n,
    }

    try:
        # Generate feedback using the Big ive scores
        feedback = big_five_feedback(scores)
        # Return the feedback as a response model
        return BigFiveResponse(feedback=feedback)
    
    except Exception as e:
        logger.error(f"Error generating Big Five feedback:{str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate Big Five feedback: {str(e)}"
        )

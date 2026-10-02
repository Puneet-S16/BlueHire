from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User
from schemas.recommendation import RecommendationListResponse
from repositories.recommendation_repository import RecommendationRepository
from repositories.worker_repository import WorkerRepository
from services.recommendation_service import RecommendationService
from core.exceptions import InvalidWorkerRoleError, WorkerNotFoundError

from api.routes.auth import get_current_user

router = APIRouter()

def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(
        RecommendationRepository(db),
        WorkerRepository(db)
    )

@router.get("/jobs", response_model=RecommendationListResponse, summary="Get recommended jobs")
def get_recommended_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
) -> Any:
    """
    Get recommended jobs for the authenticated worker based on skill/category, city, and experience matching.
    """
    try:
        total, results = recommendation_service.calculate_recommendations(current_user, page, page_size)
        return RecommendationListResponse(
            total=total,
            page=page,
            page_size=page_size,
            results=results
        )
    except InvalidWorkerRoleError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except WorkerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

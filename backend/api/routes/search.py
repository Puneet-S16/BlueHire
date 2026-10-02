from typing import Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.search import SearchJobsRequest, SearchJobsResponse
from repositories.search_repository import SearchRepository
from services.search_service import SearchService

router = APIRouter()

def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    return SearchService(SearchRepository(db))

@router.get("/jobs", response_model=SearchJobsResponse, summary="Search active jobs")
def search_jobs(
    request: SearchJobsRequest = Depends(),
    search_service: SearchService = Depends(get_search_service)
) -> Any:
    """
    Public endpoint to search and discover active jobs in the marketplace.
    """
    try:
        total, results = search_service.search_jobs(request)
        return SearchJobsResponse(
            total=total,
            page=request.page,
            page_size=request.page_size,
            results=results
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

from typing import Tuple, List
from schemas.search import SearchJobsRequest
from models.job import Job
from repositories.search_repository import SearchRepository

class SearchService:
    def __init__(self, search_repo: SearchRepository):
        self.search_repo = search_repo

    def search_jobs(self, request: SearchJobsRequest) -> Tuple[int, List[Job]]:
        # Normalize and prepare filters
        filters = request.model_dump(exclude_unset=True)
        
        # Keyword normalization (strip extra whitespace if string)
        if filters.get("keyword"):
            filters["keyword"] = filters["keyword"].strip()

        # Validate salary ranges if both are provided
        if filters.get("min_salary") is not None and filters.get("max_salary") is not None:
            if filters["min_salary"] > filters["max_salary"]:
                raise ValueError("min_salary cannot be greater than max_salary")
                
        # Call repository (it handles ACTIVE status internally)
        return self.search_repo.search_jobs(filters)

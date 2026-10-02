from typing import Dict, Any, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, desc, asc
from models.job import Job
from models.enums import JobStatusEnum

class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_jobs(self, filters: Dict[str, Any]) -> Tuple[int, List[Job]]:
        query = select(Job).where(Job.status == JobStatusEnum.ACTIVE)

        # Keyword filtering
        keyword = filters.get("keyword")
        if keyword:
            keyword_term = f"%{keyword}%"
            query = query.where(
                or_(
                    Job.title.ilike(keyword_term),
                    Job.description.ilike(keyword_term)
                )
            )

        # Exact match filters
        if filters.get("category_id") is not None:
            query = query.where(Job.category_id == filters["category_id"])
            
        if filters.get("company_id") is not None:
            query = query.where(Job.company_id == filters["company_id"])
            
        if filters.get("city"):
            query = query.where(Job.city.ilike(f"%{filters['city']}%"))
            
        if filters.get("state"):
            query = query.where(Job.state.ilike(f"%{filters['state']}%"))
            
        if filters.get("job_type") is not None:
            query = query.where(Job.job_type == filters["job_type"])
            
        if filters.get("min_salary") is not None:
            # We assume pay_max >= min_salary or pay_min >= min_salary
            query = query.where(
                or_(
                    Job.pay_min >= filters["min_salary"],
                    Job.pay_max >= filters["min_salary"]
                )
            )
            
        if filters.get("max_salary") is not None:
            query = query.where(
                or_(
                    Job.pay_min <= filters["max_salary"],
                    Job.pay_max <= filters["max_salary"]
                )
            )
            
        if filters.get("experience_required_years") is not None:
            query = query.where(Job.experience_required_years <= filters["experience_required_years"])

        # Note: is_remote is ignored because the Job model does not track it natively 
        # (avoiding unauthorized model modification).

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        # Sorting
        sort_by = filters.get("sort_by", "newest")
        if sort_by == "newest":
            query = query.order_by(desc(Job.created_at))
        elif sort_by == "oldest":
            query = query.order_by(asc(Job.created_at))
        elif sort_by == "salary_high":
            query = query.order_by(desc(Job.pay_max), desc(Job.pay_min))
        elif sort_by == "salary_low":
            query = query.order_by(asc(Job.pay_min), asc(Job.pay_max))

        # Pagination
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)
        skip = (page - 1) * page_size
        
        query = query.offset(skip).limit(page_size)
        
        records = list(self.db.execute(query).scalars().all())
        
        return total, records

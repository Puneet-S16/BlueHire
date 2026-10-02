import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, exists
from models.worker import Worker
from models.job import Job
from models.skill import Skill, WorkerSkill
from models.application import Application
from models.saved_job import SavedJob
from models.enums import JobStatusEnum

class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_recommended_jobs(self, worker: Worker, page: int = 1, page_size: int = 20) -> Tuple[int, List[dict]]:
        # Exclusions
        applied_exists = select(1).select_from(Application).where(
            Application.job_id == Job.id, 
            Application.worker_id == worker.user_id
        ).exists()
        
        saved_exists = select(1).select_from(SavedJob).where(
            SavedJob.job_id == Job.id, 
            SavedJob.worker_id == worker.user_id
        ).exists()
        
        # Scoring components
        has_category = select(1).select_from(WorkerSkill).join(Skill, Skill.id == WorkerSkill.skill_id).where(
            WorkerSkill.worker_id == worker.user_id,
            Skill.category_id == Job.category_id
        ).exists()

        score_expr = (
            case((has_category, 5), else_=0) +
            case(
                (Job.city.isnot(None) & (func.lower(Job.city) == func.lower(worker.city if worker.city else "")), 3),
                else_=0
            ) +
            case(
                (Job.experience_required_years <= (worker.total_experience_years or 0), 2),
                else_=0
            )
        ).label("match_score")

        # Base query
        query = (
            select(Job, score_expr)
            .where(
                Job.status == JobStatusEnum.ACTIVE,
                Job.posted_by_id != worker.user_id,
                ~applied_exists,
                ~saved_exists,
                score_expr > 0  # Only return jobs that have at least some match
            )
        )

        # Count total matches
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        # Sort by match score and pagination
        query = query.order_by(score_expr.desc(), Job.created_at.desc())
        
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)

        records = self.db.execute(query).all()
        
        # Map to dict containing the job and match score
        results = [
            {"job": row.Job, "match_score": row.match_score}
            for row in records
        ]
        
        return total, results

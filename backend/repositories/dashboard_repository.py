import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.application import Application
from models.job import Job
from models.enums import ApplicationStatusEnum, JobStatusEnum

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_worker_dashboard_stats(self, worker_id: uuid.UUID) -> Dict[str, Any]:
        # Aggregate query for application statuses
        status_counts = dict(
            self.db.execute(
                select(Application.status, func.count(Application.id))
                .where(Application.worker_id == worker_id)
                .group_by(Application.status)
            ).all()
        )

        total_apps = sum(status_counts.values())
        
        # Consider PENDING and IN_REVIEW as active
        active_apps = status_counts.get(ApplicationStatusEnum.PENDING, 0) + status_counts.get(ApplicationStatusEnum.IN_REVIEW, 0)
        shortlisted = status_counts.get(ApplicationStatusEnum.SHORTLISTED, 0)
        rejected = status_counts.get(ApplicationStatusEnum.REJECTED, 0)

        # Recent applications
        recent_apps = list(
            self.db.execute(
                select(Application)
                .where(Application.worker_id == worker_id)
                .order_by(Application.created_at.desc())
                .limit(5)
            ).scalars().all()
        )

        return {
            "total_applications": total_apps,
            "active_applications": active_apps,
            "shortlisted_count": shortlisted,
            "rejected_count": rejected,
            "recent_applications": recent_apps
        }

    def get_employer_dashboard_stats(self, company_id: uuid.UUID) -> Dict[str, Any]:
        # Aggregate jobs
        job_status_counts = dict(
            self.db.execute(
                select(Job.status, func.count(Job.id))
                .where(Job.company_id == company_id)
                .group_by(Job.status)
            ).all()
        )
        total_jobs = sum(job_status_counts.values())
        active_jobs = job_status_counts.get(JobStatusEnum.ACTIVE, 0)

        # Total applications received for this company's jobs
        total_apps = self.db.execute(
            select(func.count(Application.id))
            .join(Job, Job.id == Application.job_id)
            .where(Job.company_id == company_id)
        ).scalar() or 0

        # Recent jobs
        recent_jobs = list(
            self.db.execute(
                select(Job)
                .where(Job.company_id == company_id)
                .order_by(Job.created_at.desc())
                .limit(5)
            ).scalars().all()
        )

        # Recent applications
        recent_apps = list(
            self.db.execute(
                select(Application)
                .join(Job, Job.id == Application.job_id)
                .where(Job.company_id == company_id)
                .order_by(Application.created_at.desc())
                .limit(5)
            ).scalars().all()
        )

        return {
            "total_jobs_posted": total_jobs,
            "active_jobs": active_jobs,
            "total_applications_received": total_apps,
            "recent_applications": recent_apps,
            "recent_jobs": recent_jobs
        }

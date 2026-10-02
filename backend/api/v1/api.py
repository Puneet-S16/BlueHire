from fastapi import APIRouter
from api.v1.endpoints import health
from api.routes import auth, company, employer, worker, job, application, document, skill, education, experience, category, search, notification, dashboard, saved_job, recommendation

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(employer.router, prefix="/employers", tags=["employers"])
api_router.include_router(worker.router, prefix="/workers", tags=["workers"])
api_router.include_router(job.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(application.router, prefix="/applications", tags=["applications"])
api_router.include_router(document.router, prefix="/documents", tags=["documents"])
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(skill.router, prefix="/skills", tags=["skills"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(experience.router, prefix="/experience", tags=["experience"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(saved_job.router, prefix="/saved-jobs", tags=["saved-jobs"])
api_router.include_router(recommendation.router, prefix="/recommendations", tags=["recommendations"])

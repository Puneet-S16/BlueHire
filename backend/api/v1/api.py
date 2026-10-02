from fastapi import APIRouter
from api.v1.endpoints import health
from api.routes import auth, company, employer, worker, job, application, document, skill, education, experience

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(company.router, prefix="/companies", tags=["companies"])
api_router.include_router(employer.router, prefix="/employers", tags=["employers"])
api_router.include_router(worker.router, prefix="/workers", tags=["workers"])
api_router.include_router(job.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(application.router, prefix="/applications", tags=["applications"])
api_router.include_router(document.router, prefix="/documents", tags=["documents"])
api_router.include_router(skill.router, prefix="/skills", tags=["skills"])
api_router.include_router(education.router, prefix="/education", tags=["education"])
api_router.include_router(experience.router, prefix="/experience", tags=["experience"])

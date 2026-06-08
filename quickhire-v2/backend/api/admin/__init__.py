from fastapi import APIRouter
from .dashboard import router as dashboard_router
from .users import router as users_router
from .resumes import router as resumes_router
from .logs import router as logs_router
from .analytics import router as analytics_router
from .content import router as content_router
from .packages import router as packages_router
from .system import router as system_router

admin_router = APIRouter()

admin_router.include_router(dashboard_router, prefix="/dashboard", tags=["Admin - Dashboard"])
admin_router.include_router(users_router, prefix="/users", tags=["Admin - Users"])
admin_router.include_router(resumes_router, prefix="/resumes", tags=["Admin - Resumes"])
admin_router.include_router(logs_router, prefix="/logs", tags=["Admin - Logs"])
admin_router.include_router(analytics_router, prefix="/analytics", tags=["Admin - Analytics"])
admin_router.include_router(content_router, prefix="/content", tags=["Admin - Content"])
admin_router.include_router(packages_router, prefix="/packages", tags=["Admin - Packages"])
admin_router.include_router(system_router, prefix="/system", tags=["Admin - System"])

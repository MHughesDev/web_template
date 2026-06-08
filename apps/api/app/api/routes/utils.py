from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.api.routes._health import DependencyStatus, probe_dependencies
from app.core.config import settings
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get(
    "/health/dependencies/",
    dependencies=[Depends(get_current_active_superuser)],
)
async def health_dependencies() -> dict[str, DependencyStatus]:
    """
    Probe the external dependencies this deployment has configured
    (database, SMTP, Sentry, and any HEALTH_CHECK_URLS) and report
    read-only reachability status for each. Never returns secret values.

    Gated by settings.HEALTH_DEPENDENCIES_ENABLED — superuser-only since
    it reveals infrastructure topology (hosts/ports).
    """
    if not settings.HEALTH_DEPENDENCIES_ENABLED:
        raise HTTPException(status_code=404, detail="Not Found")
    return await probe_dependencies(settings)

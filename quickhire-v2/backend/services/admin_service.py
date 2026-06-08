from datetime import datetime
from database import SessionLocal
from models import ApiCallLog


def log_api_call(
    user_id: int | None = None,
    endpoint: str = "",
    model: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int = 0,
    status: str = "success",
    error_message: str | None = None,
    cost: float = 0.0,
):
    """Write an API call log entry. Creates its own DB session so it can be called from anywhere."""
    session = SessionLocal()
    try:
        log = ApiCallLog(
            user_id=user_id,
            endpoint=endpoint,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            cost=cost,
        )
        session.add(log)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

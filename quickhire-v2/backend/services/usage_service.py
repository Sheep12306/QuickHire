from datetime import date
from sqlalchemy.orm import Session
from models import DailyUsage

DAILY_FREE_LIMIT = 2


class UsageError(Exception):
    pass


class UsageService:

    @staticmethod
    def _get_today(db: Session, user_id: int) -> DailyUsage:
        today = date.today().isoformat()
        record = (
            db.query(DailyUsage)
            .filter(DailyUsage.user_id == user_id, DailyUsage.usage_date == today)
            .first()
        )
        if not record:
            record = DailyUsage(user_id=user_id, usage_date=today)
            db.add(record)
            db.flush()
        return record

    @staticmethod
    def check_and_increment(
        db: Session,
        user_id: int,
        action: str,
        has_own_api_key: bool = False,
    ):
        """Raise UsageError if free limit exceeded. Always OK if user has own API key."""
        if has_own_api_key:
            return  # unlimited

        today = UsageService._get_today(db, user_id)

        if action == "optimize":
            if today.optimize_count >= DAILY_FREE_LIMIT:
                raise UsageError(
                    f"每日免费{action_text(action)}次数已用完（{DAILY_FREE_LIMIT}次/天），"
                    "请明天再试或配置自己的 API Key 解除限制"
                )
            today.optimize_count += 1
        elif action == "diagnose":
            if today.diagnose_count >= DAILY_FREE_LIMIT:
                raise UsageError(
                    f"每日免费{action_text(action)}次数已用完（{DAILY_FREE_LIMIT}次/天），"
                    "请明天再试或配置自己的 API Key 解除限制"
                )
            today.diagnose_count += 1

        db.commit()

    @staticmethod
    def get_remaining(
        db: Session,
        user_id: int,
        has_own_api_key: bool = False,
    ) -> dict:
        if has_own_api_key:
            return {
                "unlimited": True,
                "optimize_remaining": -1,
                "diagnose_remaining": -1,
            }
        today = UsageService._get_today(db, user_id)
        return {
            "unlimited": False,
            "optimize_remaining": max(0, DAILY_FREE_LIMIT - today.optimize_count),
            "diagnose_remaining": max(0, DAILY_FREE_LIMIT - today.diagnose_count),
            "daily_limit": DAILY_FREE_LIMIT,
        }


def action_text(action: str) -> str:
    return {"optimize": "简历优化", "diagnose": "AI深度分析"}.get(action, action)

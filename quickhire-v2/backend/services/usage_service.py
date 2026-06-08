from datetime import date
from sqlalchemy.orm import Session
from models import DailyUsage, SystemConfig

FALLBACK_LIMIT = 2


class UsageError(Exception):
    pass


def _get_free_config(db: Session) -> tuple[bool, int]:
    """Read free usage config from system_configs. Returns (is_unlimited, daily_limit)."""
    configs = (
        db.query(SystemConfig)
        .filter(SystemConfig.key.in_(["free_usage_unlimited", "free_usage_daily_limit"]))
        .all()
    )
    cfg_map = {c.key: c.value for c in configs}
    unlimited = cfg_map.get("free_usage_unlimited", "false") == "true"
    limit = int(cfg_map.get("free_usage_daily_limit", str(FALLBACK_LIMIT)))
    return unlimited, limit


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

        unlimited, daily_limit = _get_free_config(db)
        if unlimited:
            return  # admin set unlimited mode

        today = UsageService._get_today(db, user_id)

        if action == "optimize":
            if today.optimize_count >= daily_limit:
                raise UsageError(
                    f"每日免费{action_text(action)}次数已用完（{daily_limit}次/天），"
                    "请明天再试或配置自己的 API Key 解除限制"
                )
            today.optimize_count += 1
        elif action == "diagnose":
            if today.diagnose_count >= daily_limit:
                raise UsageError(
                    f"每日免费{action_text(action)}次数已用完（{daily_limit}次/天），"
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
        unlimited, daily_limit = _get_free_config(db)
        if unlimited:
            return {
                "unlimited": True,
                "optimize_remaining": -1,
                "diagnose_remaining": -1,
                "daily_limit": 0,
            }
        today = UsageService._get_today(db, user_id)
        return {
            "unlimited": False,
            "optimize_remaining": max(0, daily_limit - today.optimize_count),
            "diagnose_remaining": max(0, daily_limit - today.diagnose_count),
            "daily_limit": daily_limit,
        }


def action_text(action: str) -> str:
    return {"optimize": "简历优化", "diagnose": "AI深度分析"}.get(action, action)

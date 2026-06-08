from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import get_db, require_admin
from models import User, SystemConfig, AdminAuditLog
from schemas import (
    AdminConfigItem, IpWhitelistRequest, RolePermission, MessageResponse,
)

router = APIRouter()


# ── System Config ─────────────────────────────────────────────

@router.get("/config")
def get_system_config(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    configs = db.query(SystemConfig).all()
    return {"items": [
        AdminConfigItem(key=c.key, value=c.value, description=c.description or "").model_dump()
        for c in configs
    ]}


@router.put("/config")
def update_system_config(
    items: list[AdminConfigItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    for item in items:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == item.key).first()
        if cfg:
            cfg.value = item.value
            cfg.description = item.description or cfg.description
        else:
            db.add(SystemConfig(key=item.key, value=item.value, description=item.description or ""))
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_system_config",
                         target_type="system_config", detail=f"更新 {len(items)} 项配置"))
    db.commit()
    return MessageResponse(message="配置已更新")


# ── Roles ─────────────────────────────────────────────────────

@router.get("/roles")
def get_roles(
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    """Return available roles and their permissions."""
    roles = [
        RolePermission(role="super_admin", label="超级管理员", permissions=[
            "dashboard:view", "users:manage", "users:view",
            "resumes:manage", "resumes:view", "logs:view",
            "analytics:view", "content:manage", "content:view",
            "packages:manage", "packages:view", "system:manage",
        ]),
        RolePermission(role="operator", label="运营管理员", permissions=[
            "dashboard:view", "users:manage", "users:view",
            "resumes:manage", "resumes:view", "logs:view",
            "analytics:view", "content:manage", "content:view",
            "packages:view",
        ]),
        RolePermission(role="viewer", label="只读查看者", permissions=[
            "dashboard:view", "users:view", "resumes:view",
            "logs:view", "analytics:view", "content:view",
            "packages:view",
        ]),
    ]
    return {"items": [r.model_dump() for r in roles]}


# ── IP Whitelist ──────────────────────────────────────────────

@router.get("/ip-whitelist")
def get_ip_whitelist(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    cfg = db.query(SystemConfig).filter(SystemConfig.key == "ip_whitelist").first()
    ips = cfg.value.split(",") if cfg and cfg.value else []
    enabled = False
    enabled_cfg = db.query(SystemConfig).filter(SystemConfig.key == "ip_whitelist_enabled").first()
    if enabled_cfg:
        enabled = enabled_cfg.value == "true"
    return {"ips": [ip.strip() for ip in ips if ip.strip()], "enabled": enabled}


@router.put("/ip-whitelist")
def update_ip_whitelist(
    req: IpWhitelistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    for key, value in [
        ("ip_whitelist", ",".join(req.ips)),
        ("ip_whitelist_enabled", str(req.enabled).lower()),
    ]:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if cfg:
            cfg.value = value
        else:
            db.add(SystemConfig(key=key, value=value))
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_ip_whitelist",
                         target_type="system_config", detail="更新IP白名单"))
    db.commit()
    return MessageResponse(message="IP白名单已更新")


# ── Audit Log ─────────────────────────────────────────────────

@router.get("/audit-log")
def get_audit_log(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    admin_id: int = Query(None),
    action: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    q = db.query(AdminAuditLog)
    if admin_id:
        q = q.filter(AdminAuditLog.admin_user_id == admin_id)
    if action:
        q = q.filter(AdminAuditLog.action.like(f"%{action}%"))

    total = q.count()
    logs = q.order_by(AdminAuditLog.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = [{
        "id": log.id,
        "admin_user_id": log.admin_user_id,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "detail": log.detail,
        "ip_address": log.ip_address,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    } for log in logs]

    return {"total": total, "page": page, "size": size, "items": items}

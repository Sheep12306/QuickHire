from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies import get_db, require_admin
from models import User, SystemConfig, AdminAuditLog
from schemas import (
    AdminConfigItem, AdminApiConfigRequest, IpWhitelistRequest,
    RolePermission, MessageResponse,
)
from utils.encryption import encrypt, decrypt, mask_key
from utils.api_client import test_api_connection

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


# ── System API Key Config ──────────────────────────────────────

SYSTEM_API_KEYS = ("system_api_key", "system_api_model", "system_api_base_url")


@router.get("/api-config")
def get_system_api_config(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    """Return the system-wide API key config (key is masked)."""
    cfgs = db.query(SystemConfig).filter(SystemConfig.key.in_(SYSTEM_API_KEYS)).all()
    result = {}
    for c in cfgs:
        if c.key == "system_api_key":
            decrypted = decrypt(c.value) if c.value else ""
            result["api_key"] = mask_key(decrypted) if decrypted else ""
            result["api_key_configured"] = bool(decrypted)
        elif c.key == "system_api_model":
            result["api_model"] = c.value or ""
        elif c.key == "system_api_base_url":
            result["api_base_url"] = c.value or ""
    result.setdefault("api_key", "")
    result.setdefault("api_key_configured", False)
    result.setdefault("api_model", "")
    result.setdefault("api_base_url", "")
    return result


@router.put("/api-config")
def save_system_api_config(
    req: AdminApiConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    """Save system-wide API key config. Key is encrypted before storage."""
    updates = []
    if req.api_model:
        updates.append(("system_api_model", req.api_model, "系统默认API模型"))
    if req.api_base_url:
        updates.append(("system_api_base_url", req.api_base_url, "系统默认API地址"))

    # Only update api_key if a non-masked value is provided
    if req.api_key and not req.api_key.endswith("...") and len(req.api_key) > 8:
        updates.append(("system_api_key", encrypt(req.api_key), "系统默认API密钥（加密存储）"))

    for key, value, desc in updates:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if cfg:
            cfg.value = value
            cfg.description = desc
        else:
            db.add(SystemConfig(key=key, value=value, description=desc))

    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_system_api_config",
                         target_type="system_config", detail="更新系统API配置"))
    db.commit()
    return MessageResponse(message="系统API配置已保存")


@router.post("/test-api")
def test_system_api(
    req: AdminApiConfigRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin(["super_admin"])),
):
    """Test system API connection using provided or stored credentials."""
    if req.api_key and not req.api_key.endswith("...") and len(req.api_key) > 8:
        key = req.api_key
    else:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_key").first()
        key = decrypt(cfg.value) if cfg and cfg.value else ""

    model = req.api_model
    if not model:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_model").first()
        model = cfg.value if cfg else ""

    url = req.api_base_url
    if not url:
        cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_base_url").first()
        url = cfg.value if cfg else ""

    return test_api_connection(api_key=key, api_model=model, api_base_url=url)

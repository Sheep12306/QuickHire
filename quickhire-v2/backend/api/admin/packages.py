from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from dependencies import get_db, require_admin
from models import User, Package, Order, AdminAuditLog
from schemas import PackageRequest, OrderRefundRequest, MessageResponse

router = APIRouter()


# ── Packages ──────────────────────────────────────────────────

@router.get("/plans")
def list_packages(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    packages = db.query(Package).order_by(Package.sort_order.asc()).all()
    return {"items": [{
        "id": p.id, "name": p.name, "description": p.description,
        "price": p.price, "duration_days": p.duration_days,
        "optimize_limit": p.optimize_limit, "diagnose_limit": p.diagnose_limit,
        "is_active": p.is_active, "sort_order": p.sort_order,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    } for p in packages]}


@router.post("/plans")
def create_package(
    req: PackageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    p = Package(**req.model_dump())
    db.add(p)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="create_package",
                         target_type="package", detail=f"创建套餐: {req.name}"))
    db.commit()
    db.refresh(p)
    return MessageResponse(message="套餐已创建")


@router.put("/plans/{package_id}")
def update_package(
    package_id: int,
    req: PackageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    p = db.query(Package).filter(Package.id == package_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="套餐不存在")
    for k, v in req.model_dump().items():
        setattr(p, k, v)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="update_package",
                         target_type="package", target_id=package_id))
    db.commit()
    return MessageResponse(message="套餐已更新")


@router.delete("/plans/{package_id}")
def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    p = db.query(Package).filter(Package.id == package_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="套餐不存在")
    db.delete(p)
    db.add(AdminAuditLog(admin_user_id=current_user.id, action="delete_package",
                         target_type="package", target_id=package_id))
    db.commit()
    return MessageResponse(message="套餐已删除")


# ── Orders ────────────────────────────────────────────────────

@router.get("/orders")
def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int = Query(None),
    status: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(Order)
    if user_id:
        q = q.filter(Order.user_id == user_id)
    if status:
        q = q.filter(Order.status == status)

    total = q.count()
    orders = q.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size).all()

    items = []
    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        pkg = db.query(Package).filter(Package.id == o.package_id).first()
        items.append({
            "id": o.id,
            "user_id": o.user_id,
            "user_email": user.email if user else "",
            "user_name": user.display_name if user else "",
            "package_id": o.package_id,
            "package_name": pkg.name if pkg else "",
            "amount": o.amount,
            "status": o.status,
            "payment_method": o.payment_method,
            "transaction_id": o.transaction_id,
            "notes": o.notes,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        })

    return {"total": total, "page": page, "size": size, "items": items}


@router.post("/orders/{order_id}/refund")
def refund_order(
    order_id: int,
    req: OrderRefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="订单不存在")
    if o.status == "refunded":
        raise HTTPException(status_code=400, detail="订单已退款")

    o.status = "refunded"
    o.notes = (o.notes or "") + f"\n退款原因: {req.reason}"

    # Revoke user membership
    user = db.query(User).filter(User.id == o.user_id).first()
    if user:
        user.membership_type = "free"
        user.membership_expires_at = None

    db.add(AdminAuditLog(admin_user_id=current_user.id, action="refund_order",
                         target_type="order", target_id=order_id, detail=f"退订: {req.reason}"))
    db.commit()
    return MessageResponse(message="退款成功")


# ── Memberships ───────────────────────────────────────────────

@router.get("/memberships")
def list_memberships(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    membership_type: str = Query(""),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin()),
):
    q = db.query(User).filter(User.membership_type != "free")
    if membership_type:
        q = q.filter(User.membership_type == membership_type)
    total = q.count()
    users = q.order_by(User.membership_expires_at.desc().nullslast()).offset(
        (page - 1) * size).limit(size).all()

    items = [{
        "id": u.id, "email": u.email, "display_name": u.display_name,
        "membership_type": u.membership_type,
        "membership_expires_at": u.membership_expires_at.isoformat() if u.membership_expires_at else None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]

    return {"total": total, "page": page, "size": size, "items": items}


@router.post("/memberships/{user_id}/extend")
def extend_membership(
    user_id: int,
    days: int = Query(30, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    if u.membership_expires_at and u.membership_expires_at > datetime.utcnow():
        u.membership_expires_at = u.membership_expires_at + timedelta(days=days)
    else:
        u.membership_expires_at = datetime.utcnow() + timedelta(days=days)
    u.membership_type = "premium"

    db.add(AdminAuditLog(admin_user_id=current_user.id, action="extend_membership",
                         target_type="user", target_id=user_id, detail=f"延长会员 {days} 天"))
    db.commit()
    return MessageResponse(message=f"会员已延长 {days} 天")


@router.post("/memberships/{user_id}/cancel")
def cancel_membership(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin(["super_admin"])),
):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")

    u.membership_type = "free"
    u.membership_expires_at = None

    db.add(AdminAuditLog(admin_user_id=current_user.id, action="cancel_membership",
                         target_type="user", target_id=user_id, detail="取消会员"))
    db.commit()
    return MessageResponse(message="会员已取消")

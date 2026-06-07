import asyncio, json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from models import PracticeQuestion, QuestionFavorite, User
from dependencies import get_db, get_current_user, get_optional_user
from utils.api_client import call_qwen_api_with_retry, safe_json_parse
from utils.prompt_builder import build_position_question_prompt

router = APIRouter()


class GenerateRequest(BaseModel):
    target_position: str
    difficulty: str = "中等"
    question_types: list[str] = ["简答题", "场景面试题"]
    question_count: int = 5


class SaveRequest(BaseModel):
    position: str
    questions: list[dict]


@router.post("/generate")
async def generate_questions(
    req: GenerateRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    prompt = build_position_question_prompt(
        target_position=req.target_position,
        difficulty=req.difficulty,
        question_types=req.question_types,
        question_count=req.question_count,
    )
    api_key = api_model = api_base_url = None
    if current_user:
        from services.user_settings_service import UserSettingsService
        prefs = UserSettingsService.get_preferences(db, current_user.id)
        api_key = prefs.get("api_key")
        api_model = prefs.get("api_model")
        api_base_url = prefs.get("api_base_url")

    raw = await asyncio.to_thread(
        call_qwen_api_with_retry, prompt, api_key=api_key, api_model=api_model, api_base_url=api_base_url
    )
    result = safe_json_parse(raw)
    questions = result.get("questions", []) if isinstance(result, dict) else []
    return {"questions": questions, "position": req.target_position}


@router.post("/save")
def save_questions(
    req: SaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved = []
    for q in req.questions:
        pq = PracticeQuestion(
            position=req.position,
            question=q.get("question", ""),
            answer=q.get("answer", ""),
            answer_guide=q.get("answer_guide", ""),
            question_type=q.get("type", ""),
            difficulty=q.get("difficulty", ""),
            tags=",".join(q.get("tags", [])),
        )
        db.add(pq)
        db.flush()
        saved.append({"id": pq.id, "question": pq.question})
    db.commit()
    return {"saved_count": len(saved), "questions": saved}


@router.get("/browse")
def browse_questions(
    position: str = Query(None),
    difficulty: str = Query(None),
    question_type: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    q = db.query(PracticeQuestion)
    if position:
        q = q.filter(PracticeQuestion.position.ilike(f"%{position}%"))
    if difficulty:
        q = q.filter(PracticeQuestion.difficulty == difficulty)
    if question_type:
        q = q.filter(PracticeQuestion.question_type == question_type)

    total = q.count()
    questions = (
        q.order_by(desc(PracticeQuestion.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Check favorites for current user
    fav_ids = set()
    if current_user:
        favs = (
            db.query(QuestionFavorite.question_id)
            .filter(QuestionFavorite.user_id == current_user.id)
            .all()
        )
        fav_ids = {f[0] for f in favs}

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "questions": [
            {
                "id": q.id,
                "position": q.position,
                "question": q.question,
                "answer": q.answer,
                "answer_guide": q.answer_guide,
                "type": q.question_type,
                "difficulty": q.difficulty,
                "tags": q.tags.split(",") if q.tags else [],
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "favorited": q.id in fav_ids,
            }
            for q in questions
        ],
    }


@router.post("/{question_id}/favorite")
def toggle_favorite(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(QuestionFavorite)
        .filter(
            QuestionFavorite.user_id == current_user.id,
            QuestionFavorite.question_id == question_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()
        return {"favorited": False}
    else:
        fav = QuestionFavorite(user_id=current_user.id, question_id=question_id)
        db.add(fav)
        db.commit()
        return {"favorited": True}


@router.get("/favorites")
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favs = (
        db.query(QuestionFavorite)
        .filter(QuestionFavorite.user_id == current_user.id)
        .order_by(desc(QuestionFavorite.created_at))
        .all()
    )
    if not favs:
        return {"questions": []}

    q_ids = [f.question_id for f in favs]
    questions = (
        db.query(PracticeQuestion)
        .filter(PracticeQuestion.id.in_(q_ids))
        .all()
    )
    q_map = {q.id: q for q in questions}
    return {
        "questions": [
            {
                "id": q_map[f.question_id].id,
                "position": q_map[f.question_id].position,
                "question": q_map[f.question_id].question,
                "answer": q_map[f.question_id].answer,
                "answer_guide": q_map[f.question_id].answer_guide,
                "type": q_map[f.question_id].question_type,
                "difficulty": q_map[f.question_id].difficulty,
                "tags": q_map[f.question_id].tags.split(",") if q_map[f.question_id].tags else [],
                "favorited": True,
                "favorited_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in favs
            if f.question_id in q_map
        ]
    }


@router.get("/positions")
def list_positions(db: Session = Depends(get_db)):
    positions = (
        db.query(PracticeQuestion.position)
        .distinct()
        .order_by(PracticeQuestion.position)
        .all()
    )
    return {"positions": [p[0] for p in positions]}

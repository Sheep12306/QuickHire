import json
from collections import defaultdict
from data_service import ResumeService, InterviewService, ApplicationService


class AnalyticsEngine:

    @staticmethod
    def resume_improvement_timeline(user_id: int) -> list:
        history = ResumeService.get_resume_history(user_id)
        timeline = []
        for h in reversed(history):
            score = None
            match_pct = None
            if h.get("analysis_result"):
                try:
                    data = json.loads(h["analysis_result"])
                    score = data.get("overall_score")
                    match_pct = data.get("diagnosis", {}).get("keyword_match", {}).get("score")
                except (json.JSONDecodeError, TypeError, KeyError):
                    pass
            timeline.append({
                "date": (h.get("created_at") or "")[:10],
                "version": h["version_number"],
                "score": score,
                "match_pct": match_pct,
            })
        return timeline

    @staticmethod
    def skill_radar_data(user_id: int) -> dict:
        latest = ResumeService.get_latest_resume(user_id)
        if not latest or not latest.get("analysis_result"):
            return {}
        try:
            data = json.loads(latest["analysis_result"])
            diag = data.get("diagnosis", {})
            return {
                "completeness": diag.get("completeness", {}).get("score", 0),
                "keyword_match": diag.get("keyword_match", {}).get("score", 0),
                "quantification": diag.get("quantification", {}).get("score", 0),
                "structure": diag.get("structure", {}).get("score", 0),
                "language": diag.get("language", {}).get("score", 0),
                "competitiveness": diag.get("competitiveness", {}).get("score", 0),
            }
        except (json.JSONDecodeError, TypeError, KeyError):
            return {}

    @staticmethod
    def interview_score_history(user_id: int) -> list:
        answers = InterviewService.get_answers(user_id)
        return [
            {
                "date": (a.get("created_at") or "")[:10],
                "score": a.get("ai_score"),
            }
            for a in reversed(answers)
            if a.get("ai_score") is not None
        ]

    @staticmethod
    def interview_dimension_trends(user_id: int) -> dict:
        answers = InterviewService.get_answers(user_id)
        dims = defaultdict(list)
        for a in reversed(answers):
            date = (a.get("created_at") or "")[:10]
            if a.get("ai_feedback"):
                try:
                    fb = json.loads(a["ai_feedback"])
                    for d_name, d_data in fb.get("dimensions", {}).items():
                        dims[d_name].append({
                            "date": date,
                            "score": d_data.get("score", 0),
                        })
                except (json.JSONDecodeError, TypeError):
                    pass
        return dict(dims)

    @staticmethod
    def weak_area_improvement(user_id: int) -> list:
        answers = InterviewService.get_answers(user_id)
        dim_pairs = defaultdict(list)
        for a in sorted(answers, key=lambda x: x.get("created_at", "")):
            if a.get("ai_feedback"):
                try:
                    fb = json.loads(a["ai_feedback"])
                    for d_name, d_data in fb.get("dimensions", {}).items():
                        dim_pairs[d_name].append(d_data.get("score", 0))
                except (json.JSONDecodeError, TypeError):
                    pass

        result = []
        for d_name, scores in dim_pairs.items():
            if len(scores) >= 2:
                first = scores[0]
                latest = scores[-1]
                improvement = round(latest - first, 1)
                result.append({
                    "dimension": d_name,
                    "first_score": first,
                    "latest_score": latest,
                    "improvement": improvement,
                    "sessions": len(scores),
                })
        result.sort(key=lambda x: x["improvement"])
        return result

    @staticmethod
    def application_funnel(user_id: int) -> dict:
        return ApplicationService.get_stats(user_id)

    @staticmethod
    def question_type_performance(user_id: int) -> dict:
        answers = InterviewService.get_answers(user_id)
        type_scores = defaultdict(list)
        for a in answers:
            if a.get("ai_feedback"):
                try:
                    fb = json.loads(a["ai_feedback"])
                    q_type = fb.get("question_type", "未分类")
                    type_scores[q_type].append(a.get("ai_score") or 0)
                except (json.JSONDecodeError, TypeError):
                    pass
        return {
            t: round(sum(s) / len(s), 1) if s else 0
            for t, s in type_scores.items()
        }

    @staticmethod
    def difficulty_performance(user_id: int) -> dict:
        answers = InterviewService.get_answers(user_id)
        diff_scores = defaultdict(list)
        for a in answers:
            if a.get("ai_feedback"):
                try:
                    fb = json.loads(a["ai_feedback"])
                    diff = fb.get("difficulty", "未分类")
                    diff_scores[diff].append(a.get("ai_score") or 0)
                except (json.JSONDecodeError, TypeError):
                    pass
        return {
            d: round(sum(s) / len(s), 1) if s else 0
            for d, s in diff_scores.items()
        }

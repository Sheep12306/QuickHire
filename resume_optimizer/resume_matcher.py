import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import re


class ResumeMatcher:
    def __init__(self, nlp_extractor, ml_trainer):
        self.nlp_extractor = nlp_extractor
        self.ml_trainer = ml_trainer
        self.job_descriptions = []
        self.job_vectors = []

    def add_job_description(self, job_title, job_content):
        self.job_descriptions.append({
            'title': job_title,
            'content': job_content
        })
        vector = self.nlp_extractor.get_word2vec_vector(job_content)
        self.job_vectors.append(vector)

    def match_resume_to_jobs(self, resume_text, top_n=3):
        resume_vector = self.nlp_extractor.get_word2vec_vector(resume_text)

        similarities = []
        for i, job in enumerate(self.job_descriptions):
            job_vector = self.job_vectors[i]
            similarity = cosine_similarity([resume_vector], [job_vector])[0][0]
            similarities.append({
                'job_title': job['title'],
                'similarity': float(similarity),
                'match_percentage': round(similarity * 100, 2)
            })

        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_n]

    def calculate_overall_match_score(self, resume_text, target_job_content):
        similarity = self.nlp_extractor.calculate_cosine_similarity(resume_text, target_job_content)
        return round(similarity * 100, 2)

    def analyze_keyword_match(self, resume_text, target_keywords):
        resume_keywords = [kw[0] for kw in self.nlp_extractor.extract_keywords(resume_text, top_n=20)]
        matched_keywords = []
        missing_keywords = []

        for keyword in target_keywords:
            if any(keyword.lower() in rk.lower() for rk in resume_keywords):
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        match_rate = len(matched_keywords) / len(target_keywords) if target_keywords else 0
        return {
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'match_rate': round(match_rate * 100, 2),
            'resume_keywords': resume_keywords
        }


class ResumeScorer:
    def __init__(self, nlp_extractor, ml_trainer):
        self.nlp_extractor = nlp_extractor
        self.ml_trainer = ml_trainer
        self.score_weights = {
            'completeness': 0.25,
            'keyword_match': 0.30,
            'quantification': 0.20,
            'structure': 0.15,
            'language_quality': 0.10
        }

    def score_completeness(self, resume_text):
        completeness_score = 0
        checks = [
            (r'[\u4e00-\u9fa5]{2,4}', '姓名', 10),
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '邮箱', 10),
            (r'1[3-9]\d{9}', '电话', 10),
            (r'(教育经历|学历背景|毕业院校)', '教育经历', 15),
            (r'(工作经历|项目经验|实习经历)', '工作/项目经历', 20),
            (r'(技能特长|专业技能|技术栈)', '技能', 15),
            (r'(项目经验|项目经历)', '项目经验', 15),
            (r'(自我评价|个人优势)', '自我评价', 5)
        ]

        for pattern, field, points in checks:
            if len(re.findall(pattern, resume_text)) > 0:
                completeness_score += points

        return min(completeness_score, 100)

    def score_quantification(self, resume_text):
        quant_patterns = [
            r'\d+[%％]',
            r'\d+[万千万亿]',
            r'\d+[\u4e00-\u9fa5]{1,2}',
            r'\d+\+',
            r'\d+/\d+',
            r'第[一二三四五]',
            r'([同|全][城|国|球])',
            r'(领先|优秀|突出)'
        ]

        matches = sum(len(re.findall(pattern, resume_text)) for pattern in quant_patterns)
        score = min(matches * 5, 100)
        return score

    def score_structure(self, resume_text):
        lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
        if len(lines) < 5:
            return 20

        section_count = len([l for l in lines if len(l) <= 10 and l[-1] in ['：', ':', '、']])
        bullet_points = len([l for l in lines if l.startswith(('-', '•', '*', '·', '1.', '2.', '3.', '一', '二', '三'))])

        structure_score = min(section_count * 10 + min(bullet_points * 2, 50), 100)
        return structure_score

    def score_language_quality(self, resume_text):
        words = self.nlp_extractor.tokenize(resume_text)
        if len(words) < 50:
            return 30

        professional_terms = ['负责', '参与', '主导', '设计', '开发', '优化', '实现', '完成', '提升', '解决', '构建', '架构']
        term_count = sum(1 for word in words if word in professional_terms)

        score = min(30 + term_count * 3, 100)
        return score

    def calculate_overall_score(self, resume_text, target_keywords=None):
        scores = {}

        scores['completeness'] = self.score_completeness(resume_text)
        scores['quantification'] = self.score_quantification(resume_text)
        scores['structure'] = self.score_structure(resume_text)
        scores['language_quality'] = self.score_language_quality(resume_text)

        if target_keywords:
            keyword_analysis = self.nlp_extractor.extract_keywords(resume_text, top_n=30)
            resume_keywords = [kw[0] for kw in keyword_analysis]
            matched = sum(1 for kw in target_keywords if any(kw.lower() in rk.lower() for rk in resume_keywords))
            scores['keyword_match'] = round((matched / len(target_keywords)) * 100, 2)
        else:
            scores['keyword_match'] = 50

        overall_score = sum(
            scores[key] * self.score_weights.get(key, 0)
            for key in scores
        )

        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': scores,
            'grade': self._get_grade(overall_score)
        }

    def _get_grade(self, score):
        if score >= 90:
            return 'S'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'

    def get_score_breakdown(self, resume_text, target_keywords=None):
        result = self.calculate_overall_score(resume_text, target_keywords)

        recommendations = []
        scores = result['detailed_scores']

        if scores['completeness'] < 70:
            recommendations.append("建议补充完整的个人信息，包括联系方式、教育背景、工作经历等")

        if scores['quantification'] < 60:
            recommendations.append("建议使用量化数据描述成果，如'提升效率30%'、'处理100+用户请求'")

        if scores['structure'] < 70:
            recommendations.append("建议优化简历结构，使用清晰的标题和项目符号")

        if scores['language_quality'] < 60:
            recommendations.append("建议使用更专业的术语和动词，如'负责'、'主导'、'优化'")

        if 'keyword_match' in scores and scores['keyword_match'] < 70 and target_keywords:
            recommendations.append(f"建议增加以下关键词：{', '.join(target_keywords[:5])}")

        result['recommendations'] = recommendations
        return result
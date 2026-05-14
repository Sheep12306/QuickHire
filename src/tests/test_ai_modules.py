import pytest
import sys
import numpy as np
sys.path.insert(0, '..')

from nlp_feature_extractor import NLPFeatureExtractor
from ml_model_trainer import MLModelTrainer
from resume_matcher import ResumeMatcher, ResumeScorer
from defect_detector import ResumeDefectDetector
from sample_data import sample_resumes


class TestNLPFeatureExtractor:
    def test_tokenize(self):
        extractor = NLPFeatureExtractor()
        text = "Python开发工程师负责后端API开发"
        tokens = extractor.tokenize(text)
        assert isinstance(tokens, list)
        assert "Python" in tokens

    def test_extract_tfidf_features(self):
        extractor = NLPFeatureExtractor()
        documents = ["Python开发", "Java开发", "前端开发"]
        features = extractor.extract_tfidf_features(documents)
        assert features.shape[0] == 3

    def test_train_word2vec(self):
        extractor = NLPFeatureExtractor()
        documents = ["Python开发工程师", "机器学习工程师", "前端开发"]
        model = extractor.train_word2vec(documents)
        assert model is not None

    def test_calculate_similarity(self):
        extractor = NLPFeatureExtractor()
        documents = ["Python开发", "Python编程", "Java开发"]
        extractor.train_word2vec(documents)
        similarity = extractor.calculate_cosine_similarity("Python开发", "Python编程")
        assert similarity > 0.3

    def test_extract_keywords(self):
        extractor = NLPFeatureExtractor()
        documents = ["Python开发工程师使用Django框架"]
        extractor.extract_tfidf_features(documents)
        keywords = extractor.extract_keywords("Python开发工程师", top_n=5)
        assert isinstance(keywords, list)


class TestMLModelTrainer:
    def test_train_logistic_regression(self):
        import numpy as np
        trainer = MLModelTrainer()
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        model = trainer.train_logistic_regression(X, y)
        assert 'logistic_regression' in trainer.models

    def test_train_knn(self):
        import numpy as np
        trainer = MLModelTrainer()
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        model = trainer.train_knn(X, y)
        assert 'knn' in trainer.models

    def test_predict(self):
        import numpy as np
        trainer = MLModelTrainer()
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        trainer.train_logistic_regression(X, y)
        prediction = trainer.predict('logistic_regression', np.array([[2, 3]]))
        assert prediction is not None


class TestResumeMatcher:
    def test_match_resume_to_jobs(self):
        nlp = NLPFeatureExtractor()
        ml = MLModelTrainer()
        matcher = ResumeMatcher(nlp, ml)
        
        sample_docs = ["Python开发工程师", "机器学习工程师"]
        nlp.train_word2vec(sample_docs)
        
        matcher.add_job_description("Python开发", "Python开发工程师")
        matcher.add_job_description("机器学习", "机器学习工程师")
        
        result = matcher.match_resume_to_jobs("Python后端开发", top_n=2)
        assert isinstance(result, list)
        assert len(result) <= 2

    def test_calculate_overall_match_score(self):
        nlp = NLPFeatureExtractor()
        ml = MLModelTrainer()
        matcher = ResumeMatcher(nlp, ml)
        
        sample_docs = ["Python开发工程师使用Django"]
        nlp.train_word2vec(sample_docs)
        
        score = matcher.calculate_overall_match_score("Python开发", "Python开发工程师")
        assert isinstance(score, (float, np.floating))
        assert 0 <= score <= 100


class TestResumeScorer:
    def test_score_completeness(self):
        nlp = NLPFeatureExtractor()
        ml = MLModelTrainer()
        scorer = ResumeScorer(nlp, ml)
        
        resume = """姓名：张三
邮箱：test@example.com
电话：13800138000
教育经历：XX大学
工作经历：XX公司"""
        
        score = scorer.score_completeness(resume)
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_score_quantification(self):
        nlp = NLPFeatureExtractor()
        ml = MLModelTrainer()
        scorer = ResumeScorer(nlp, ml)
        
        resume = "优化性能提升30%，处理100+用户请求"
        score = scorer.score_quantification(resume)
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_calculate_overall_score(self):
        nlp = NLPFeatureExtractor()
        ml = MLModelTrainer()
        scorer = ResumeScorer(nlp, ml)
        
        result = scorer.calculate_overall_score(sample_resumes[0]["content"])
        assert "overall_score" in result
        assert "grade" in result
        assert 0 <= result["overall_score"] <= 100


class TestDefectDetector:
    def test_detect_vague_descriptions(self):
        detector = ResumeDefectDetector()
        defects = detector.detect_vague_descriptions("负责相关工作，有一定的经验")
        assert isinstance(defects, list)

    def test_detect_empty_phrases(self):
        detector = ResumeDefectDetector()
        defects = detector.detect_empty_phrases("认真负责，团队合作能力强")
        assert isinstance(defects, list)

    def test_analyze_quantification(self):
        detector = ResumeDefectDetector()
        defects = detector.analyze_quantification("负责项目开发")
        assert isinstance(defects, list)

    def test_generate_optimization_suggestions(self):
        detector = ResumeDefectDetector()
        result = detector.generate_optimization_suggestions("负责相关工作")
        assert "suggestions" in result
        assert "defects" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
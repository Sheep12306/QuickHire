import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import re
import os


class NLPFeatureExtractor:
    def __init__(self):
        self.stopwords = self._load_stopwords()
        self.tfidf_vectorizer = None
        self.word2vec_model = None

    def _load_stopwords(self):
        stopwords = set()
        try:
            import pkgutil
            data = pkgutil.get_data('jieba', 'analyse/stop_words.txt')
            if data:
                stopwords = set(data.decode('utf-8').split())
        except:
            pass
        custom_stopwords = ['的', '了', '和', '是', '就', '都', '而', '及', '与', '着', '或', '一个', '没有', '我们', '你们', '他们', '它', '这', '那', '这些', '那些']
        stopwords.update(custom_stopwords)
        return stopwords

    def tokenize(self, text):
        text = re.sub(r'[^\w\s]', '', text)
        words = jieba.cut(text)
        words = [w for w in words if w not in self.stopwords and len(w) > 1]
        return words

    def extract_tfidf_features(self, documents, fit=True):
        if fit or self.tfidf_vectorizer is None:
            self.tfidf_vectorizer = TfidfVectorizer(
                tokenizer=self.tokenize,
                max_features=5000,
                ngram_range=(1, 2)
            )
            features = self.tfidf_vectorizer.fit_transform(documents)
        else:
            features = self.tfidf_vectorizer.transform(documents)
        return features

    def train_word2vec(self, documents, vector_size=100, window=5, min_count=1):
        tokenized_docs = [self.tokenize(doc) for doc in documents]
        self.word2vec_model = Word2Vec(
            sentences=tokenized_docs,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=4,
            epochs=5
        )
        return self.word2vec_model

    def get_word2vec_vector(self, text):
        if self.word2vec_model is None:
            raise ValueError("Word2Vec模型未训练")

        words = self.tokenize(text)
        vectors = []
        for word in words:
            if word in self.word2vec_model.wv:
                vectors.append(self.word2vec_model.wv[word])

        if not vectors:
            return np.zeros(self.word2vec_model.vector_size)

        return np.mean(vectors, axis=0)

    def calculate_cosine_similarity(self, text1, text2):
        vec1 = self.get_word2vec_vector(text1)
        vec2 = self.get_word2vec_vector(text2)
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return cosine_similarity([vec1], [vec2])[0][0]

    def extract_keywords(self, text, top_n=10):
        if self.tfidf_vectorizer is None:
            raise ValueError("TF-IDF模型未训练")

        tfidf_matrix = self.tfidf_vectorizer.transform([text])
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]

        keyword_indices = tfidf_scores.argsort()[-top_n:][::-1]
        keywords = [(feature_names[i], tfidf_scores[i]) for i in keyword_indices if tfidf_scores[i] > 0]

        return keywords

    def save_models(self, tfidf_path, word2vec_path):
        import pickle
        with open(tfidf_path, 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        if self.word2vec_model:
            self.word2vec_model.save(word2vec_path)

    def load_models(self, tfidf_path, word2vec_path):
        import pickle
        if os.path.exists(tfidf_path):
            with open(tfidf_path, 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
        if os.path.exists(word2vec_path):
            self.word2vec_model = Word2Vec.load(word2vec_path)
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
from sklearn.preprocessing import StandardScaler
import pickle
import os


class MLModelTrainer:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []

    def train_logistic_regression(self, X, y, **kwargs):
        model = LogisticRegression(**kwargs)
        model.fit(X, y)
        self.models['logistic_regression'] = model
        return model

    def train_knn(self, X, y, n_neighbors=5, **kwargs):
        X_scaled = self.scaler.fit_transform(X)
        model = KNeighborsClassifier(n_neighbors=n_neighbors, **kwargs)
        model.fit(X_scaled, y)
        self.models['knn'] = model
        return model

    def train_naive_bayes(self, X, y, **kwargs):
        model = MultinomialNB(**kwargs)
        model.fit(X, y)
        self.models['naive_bayes'] = model
        return model

    def predict(self, model_name, X):
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")

        X_input = X
        if model_name == 'knn' and hasattr(self.scaler, 'mean_'):
            X_input = self.scaler.transform(X)

        return self.models[model_name].predict(X_input)

    def predict_proba(self, model_name, X):
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")

        X_input = X
        if model_name == 'knn':
            X_input = self.scaler.transform(X)

        return self.models[model_name].predict_proba(X_input)

    def evaluate(self, model_name, X_test, y_test):
        predictions = self.predict(model_name, X_test)

        if len(np.unique(y_test)) > 2:
            accuracy = accuracy_score(y_test, predictions)
            report = classification_report(y_test, predictions)
            return {
                'accuracy': accuracy,
                'classification_report': report
            }
        else:
            accuracy = accuracy_score(y_test, predictions)
            report = classification_report(y_test, predictions)
            return {
                'accuracy': accuracy,
                'classification_report': report
            }

    def cross_validation(self, model_name, X, y, cv=5):
        if model_name not in self.models:
            raise ValueError(f"模型 {model_name} 不存在")

        scores = cross_val_score(self.models[model_name], X, y, cv=cv)
        return {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'scores': scores
        }

    def save_models(self, directory):
        os.makedirs(directory, exist_ok=True)

        for name, model in self.models.items():
            model_path = os.path.join(directory, f'{name}.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

        scaler_path = os.path.join(directory, 'scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        metadata = {
            'feature_names': self.feature_names,
            'model_names': list(self.models.keys())
        }
        metadata_path = os.path.join(directory, 'metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

    def load_models(self, directory):
        model_files = [f for f in os.listdir(directory) if f.endswith('.pkl') and f != 'scaler.pkl' and f != 'metadata.pkl']

        for model_file in model_files:
            model_name = model_file.replace('.pkl', '')
            model_path = os.path.join(directory, model_file)
            with open(model_path, 'rb') as f:
                self.models[model_name] = pickle.load(f)

        scaler_path = os.path.join(directory, 'scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

        metadata_path = os.path.join(directory, 'metadata.pkl')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.feature_names = metadata.get('feature_names', [])

    def set_feature_names(self, feature_names):
        self.feature_names = feature_names
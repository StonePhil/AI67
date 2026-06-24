import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

class ShieldPreprocessor:
    def __init__(self):
        self.num_features = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count']
        self.cat_features = ['protocol_type', 'service', 'flag']
        self.pipeline = None

    def fit(self, df):
        self.pipeline = ColumnTransformer([
            ('num', StandardScaler(), self.num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), self.cat_features)
        ])
        return self.pipeline.fit(df[self.num_features + self.cat_features])

    def transform(self, data_dict):
        df = pd.DataFrame([data_dict])
        return self.pipeline.transform(df)

    def save(self, path):
        joblib.dump(self, path)

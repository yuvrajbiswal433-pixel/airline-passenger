import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder,OneHotEncoder

cols2=['id']
class dropper(BaseEstimator,TransformerMixin):
    def fit(self,x,y=None):
        return self
    def transform(self,x):
        x=x.drop(cols2,axis=1)
        return x

cols = ["Arrival Delay in Minutes"]
class NumericalImputer(BaseEstimator, TransformerMixin):
    def __init__(self, strategy="median"):
        self.strategy = strategy
    def fit(self, X, y=None):
        if self.strategy == "median":
            self.fill_value_ = np.nanmedian(X, axis=0)
        elif self.strategy == "mean":
            self.fill_value_ = np.nanmean(X, axis=0)
        else:
            raise ValueError("Use 'mean' or 'median'")
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=float).copy()
        missing_rows, missing_cols = np.where(np.isnan(X))
        X[missing_rows, missing_cols] = self.fill_value_[missing_cols]
        return X

cust_type_order=['disloyal Customer','Loyal Customer']
travel_order=['Personal Travel','Business travel']
class_order=['Eco','Eco Plus','Business']
cols3=['Customer Type','Type of Travel','Class']
class ordinalencoder(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        self.oe = OrdinalEncoder(
            categories=[
                cust_type_order,
                travel_order,
                class_order
            ]
        )
        self.oe.fit(x[cols3])
        return self
    def transform(self, x):
        x[cols3] = self.oe.transform(x[cols3])
        return x

ohe_cols = ['Gender']
class OHEEncoder(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        self.encoder = OneHotEncoder(
            drop='first',
            sparse_output=False,
            handle_unknown='ignore'
        )
        self.encoder.fit(x[ohe_cols])
        return self
    def transform(self, x):
        encoded = self.encoder.transform(x[ohe_cols])
        encoded_df = pd.DataFrame(
            encoded,
            columns=self.encoder.get_feature_names_out(ohe_cols),
            index=x.index
        )
        x = x.drop(ohe_cols, axis=1)
        x = pd.concat([x, encoded_df], axis=1)
        return x
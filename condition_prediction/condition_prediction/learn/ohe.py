import typing

import sklearn
import pandas as pd


class GetDummies(sklearn.base.TransformerMixin):
    """Fast one-hot-encoder that makes use of pandas.get_dummies() safely
    on train/test splits.
    Taken from: https://dantegates.github.io/2018/05/04/a-fast-one-hot-encoder-with-sklearn-and-pandas.html
    """

    def __init__(self, dtypes=None):
        self.input_columns = None
        self.final_columns = None
        if dtypes is None:
            dtypes = [object, "category"]
        self.dtypes = dtypes

    def fit(self, X, y=None, dummy_na=False, **kwargs):
        self.input_columns = list(X.select_dtypes(self.dtypes).columns)
        X = pd.get_dummies(X, columns=self.input_columns, dummy_na=dummy_na)
        self.final_columns = X.columns
        return self

    def transform(self, X, y=None, **kwargs):
        X = pd.get_dummies(X, columns=self.input_columns)
        X_columns = X.columns
        # if columns in X had values not in the data set used during
        # fit add them and set to 0
        missing = set(self.final_columns) - set(X_columns)
        for c in missing:
            X[c] = False

        # If all values in a row are false, then set the column ending in _other to true (example column name: solvent_000_other)
        # This is to ensure that the model can handle unseen values
        X["all_false"] = X.apply(lambda row: row.sum() == 0, axis=1)

        # Set columns ending in _other to True where all values in the row are False
        other_columns = [col for col in X.columns if col.endswith("_other")]
        X.loc[X["all_false"], other_columns] = True

        # remove any new columns that may have resulted from values in
        # X that were not in the data set when fit
        return X[self.final_columns]

    def get_feature_names(self):
        return tuple(self.final_columns)


def apply_train_ohe_fit(df, train_idx, val_idx, test_idx=None, tensor_func=None):
    enc = GetDummies()
    _ = enc.fit(df.iloc[train_idx])
    _ohe = enc.transform(df)
    _tr, _val = _ohe.iloc[train_idx].values, _ohe.iloc[val_idx].values
    _tr, _val = _tr.astype("float32"), _val.astype("float32")
    if tensor_func is not None:
        _tr, _val = tensor_func(_tr), tensor_func(_val)

    if test_idx is not None:
        _test = _ohe.iloc[test_idx].values
        _test = _test.astype("float32")
        if tensor_func is not None:
            _test = tensor_func(_test)

    return _tr, _val, _test, enc

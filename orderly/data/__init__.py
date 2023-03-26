import typing
import io
import pathlib
import pkgutil

import pandas as pd


def get_solvents(path: typing.Optional[pathlib.Path] = None) -> pd.DataFrame:
    """reads the solvent csv data stored in the package"""
    if path is None:
        data = pkgutil.get_data("orderly.data", "solvents.csv")
        return pd.read_csv(io.BytesIO(data), index_col=0)

    return pd.read_csv(path, index_col=0)
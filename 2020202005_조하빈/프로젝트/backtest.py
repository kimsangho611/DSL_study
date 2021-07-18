import numpy as np
import pandas as pd


def mfi(data: pd.DataFrame, period: int = 14):
    if data.iloc[0, 'MFI'] <= 20:
        # buy
        pass
    elif data.iloc[0, 'MFI'] >= 80:
        # sell
        pass

import pandas as pd
import datetime as dt
import numpy as np

def convert_dates(df):
    date_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else ''
            if isinstance(sample, str) and any(char in sample for char in ['-', '/', '.', ':']):
                date_columns.append(col)
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

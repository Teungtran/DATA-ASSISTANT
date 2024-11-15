import pandas as pd
def detect_outliers(df):
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    outliers_summary = {}
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outliers_count = outliers.shape[0]
        if outliers_count > 0:
            outliers_summary[col] = outliers_count
        else:
            outliers_summary[col] = 0
    
    if len(outliers_summary) > 0:
        outliers_info = "\n".join([f"{col}: {count} outliers" for col, count in outliers_summary.items()])
    else:
        outliers_info = "No outliers detected."
    
    return outliers_info
def analyze_dataset(df):
    if not isinstance(df, pd.DataFrame):
        return "Input is not a valid DataFrame."
    
    # 1. Number of rows and columns
    num_rows, num_columns = df.shape
    dataset_info = f"Dataset Info:\n- Number of rows: {num_rows} : - Number of columns: {num_columns}\n\n"
    
    # 2. Data types of each column
    data_types = df.dtypes
    dataset_info += "Data Types of Columns:\n" + data_types.apply(lambda x: f": {x}").to_string() + "\n\n"
    
    # 3. Null Values
    null_values = df.isnull().sum()
    dataset_info += "Null Values per Column:\n" + null_values.apply(lambda x: f": {x}").to_string() + "\n\n"
    
    # 4. Detecting Outliers
    outliers_info = detect_outliers(df)
    dataset_info += f"\nOutliers Summary:\n{outliers_info}"
    
    return dataset_info

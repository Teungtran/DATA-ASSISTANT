import matplotlib.pyplot as plt
import seaborn as sns
import csv
import numpy as np
import chardet
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
import streamlit as st
import io
import pandas as pd

def generate_plot(df, x_column, y_column, plot_type):
    if plot_type == "📈 Line Plot":
        fig = px.line(df, x=x_column, y=y_column,
                    title=f"Line Plot: {y_column} vs {x_column}")
        
        # Set the trace name to the y-column name directly
        fig.data[0].name = y_column
        st.sidebar.info("💡 Line plots work best with continuous data or time series")
    elif plot_type == "📊 Bar Plot":
        fig = px.bar(df, x=x_column, y=y_column,
                    title=f"Bar Plot: {y_column} vs {x_column}")
        # Set the trace name to the y-column name directly
        fig.data[0].name = y_column
        st.sidebar.info("💡 Bar plots work best with categorical X-axis data")
    # Update layout
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        template="plotly_dark",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig
def histogram(df, x_column,plot_type):
    if plot_type == "📉 Histogram":
        fig = px.histogram(df, x=x_column, nbins=30, title=f"Histogram: {x_column}")
                        
        # Set the trace name to the y-column name directly
        fig.data[0].name = x_column
    fig.update_layout(
        xaxis_title=x_column,
        template="plotly_dark",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        )
    )
    return fig

def heat_map(df):
    plt.figure(figsize=(10, 8))
    try:
        plt.title("Correlation of the dataset")
        sns.heatmap(df.corr(), vmin=-1, vmax=1, center=0, annot=True, cmap='coolwarm', annot_kws={'fontsize': 8, 'fontweight': 'bold'}, cbar=False)
        buf_heat = io.BytesIO()
        plt.savefig(buf_heat, format='png')
        buf_heat.seek(0)
        plt.close()
        return buf_heat
    except Exception as e:
        return f"Error generating heatmap: {e}"

def pie_plot(df, x_column):
    try:
        # Calculate value counts for the column
        value_counts = df[x_column].value_counts()
        
        fig = px.pie(values=value_counts.values,
                    names=value_counts.index,
                    title=f"Distribution of {x_column}")
        
        # Update layout
        fig.update_layout(
            showlegend=True,
            width=700,
            height=700,
            legend=dict(
                title=x_column,
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02
            )
        )
        
        # Update hover template
        fig.update_traces(
            hovertemplate="%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )
        
        return fig
    except Exception as e:
        return f"Error generating pie chart: {e}"

# Data has categorical features
def get_dummies(df):
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols:
            if df[col].isin(['yes', 'no', 'True', 'False']).any():
                df[col] = df[col].map({'yes': 1, 'True': 1, 'no': 0, 'False': 0})
            else:
                df = pd.get_dummies(df, columns=[col], drop_first=True)
    return df
# ___________________________Function to generate various plot types using PLotly_____________________________
    # New function to generate a plot for the output
def save_response(response):
    try:
        if isinstance(response, pd.DataFrame):
            response.to_csv('response.csv', index=False)
            st.success("Response saved to response.csv")
        else:
            with open('response.csv', 'w') as f:
                f.write(str(response))
            st.success("Response saved to response.csv")
    except Exception as e:
        st.error(f"Error saving response: {e}")

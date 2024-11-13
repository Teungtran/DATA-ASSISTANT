import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import io
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
import csv
import numpy as np
import chardet
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
#streamlit run SQL.py
# API Keys 
GOOGLE_API_KEY = "AIzaSyBxLB3VTohn1tmfG2kMe_Is_XHkRIH7rZU"
# BUILD MODEL
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("Gemini Pro model loaded successfully.")
except Exception as e:
    st.error(f"Error loading Gemini Pro model: {e}")
    st.stop()

#________________________Custom ResponseParser to handle plot generation__________________________
class OutputParser(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_response(self, result):
        st.write(result["value"])
        return

# ___________________________Function to generate various plot types using PLotly_____________________________
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
def histogram(df, x_column):
    if plot_type == "📉 Histogram":
        fig = px.histogram(df, x=x_column, nbins=30, title=f"Histogram: {x_column}")
                        
        # Set the trace name to the y-column name directly
        fig.data[0].name = x_column
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
def generate_output_plot(output):
    try:
        if isinstance(output, pd.DataFrame):
            if len(output.columns) == 2:
                fig = px.bar(output, x=output.columns[0], y=output.columns[1])
                fig.data[0].name = output.columns[1]  # Use column name directly
            else:
                fig = px.bar(output)
                # Update trace names to use column names directly
                for i, trace in enumerate(fig.data):
                    trace.name = output.columns[i]
            
            fig.update_layout(
                title="Output Visualization",
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=1.02
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        elif isinstance(output, pd.Series):
            fig = px.line(output)
            fig.data[0].name = output.name if output.name else "Value"
            
            fig.update_layout(
                title="Output Visualization",
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=1.02
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.write("Output is not a DataFrame or Series, cannot generate plot")
            
    except Exception as e:
        st.error(f"Error generating output plot: {e}")
    # function to save response as CSV filefile
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

# _____________________________Set up the Streamlit interface_____________________________________
st.set_page_config(page_title="YOUR DATA ANALYST ASSISTANT", layout="wide")
st.title("DATA ANALYST ASSISTANT🤖💾")
st.divider()
st.sidebar.header('INSTRUCTION')
st.sidebar.info('WRITE YOUR  QUESTION IN ENGLISH THEN Let THE AI DO THE REST!')
st.sidebar.info('THE MODEL USES GEN_AI using Gemini API AND IT WILL GIVE OUT EXPLANATION AS WELL')

# ___________________________________File uploader_______________________________________________
# Text area for input
input_text = st.text_area("ENTER YOUR QUESTION:")
option  = st.sidebar.selectbox("Select an option", ["Chat with uploaded file","Chat with SQL querry"])
if option == "Chat with uploaded file":
    uploaded_file = st.file_uploader("Upload your csv or xlsx file (optional)", type=['csv', 'xlsx'])
    # read file csv or xlsx
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                # Detect the separator
                result = chardet.detect(uploaded_file.getvalue())
                charenc = result['encoding']
                dialect = csv.Sniffer().sniff(uploaded_file.getvalue().decode(charenc)[:1024], delimiters=[',', ';'])
                delimiter = dialect.delimiter

                try:
                    df = pd.read_csv(uploaded_file, encoding=charenc, delimiter=delimiter, low_memory=False)
                except Exception as e:
                    st.error(f"Error reading CSV file: {e}")
                    df = None
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                df = None
        else:
            df = None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        df = None
#______________________________Generate answer and plot______________________________________
    if df is not None:
        with st.expander("Data Preview"):
            st.dataframe(df.head(100))
        if st.button("Convert Categorical data to Numeric"):
            df_converted = get_dummies(df)
            st.write("Data after getting dummies:")
            st.dataframe(df_converted.head(100))

        # Initialize SmartDataFrame
        llm = GoogleGemini(api_key=GOOGLE_API_KEY)
        sdf = SmartDataframe(df, config={"llm": llm, "response_parser": OutputParser})
        response = sdf.chat(input_text)
        # Generate SQL query for the responded question
        sql_query_prompt = f"Generate the SQL code for the following question: '{input_text}'"
        sql_response = model.generate_content(sql_query_prompt)
        st.subheader("RESULT & Code")
        # Display response
        st.write(response)
        st.code(sql_response.text)
        st.success("Thank you for using our assistant. Have a great day!")
# Dropdowns for selecting x and y columns for plotting
st.sidebar.subheader("Select Columns and Plot Type")
st.divider()
# Create column selectors only if dataframe exists
df = None
if df is not None:
    # Get numeric columns for plotting
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    all_columns = df.columns.tolist()

    # Plot type selector (moved to top)
    plot_type = st.sidebar.selectbox(
        "Select Plot Type",
        [
            "📈 Line Plot",
            "📊 Bar Plot",
            "📉 Histogram",
            "🥧 Pie Chart",
            "🌡️ Heatmap"
        ]
    )

    # Column selectors based on plot type
    if plot_type in ["🥧 Pie Chart", "📉 Histogram"]:
        # Only show X-axis selection for pie chart and heatmap
        x_column = st.sidebar.selectbox("Select column", all_columns)
        y_column = None  # Not needed for these plot types
    elif plot_type == "🌡️ Heatmap":
        x_column = None
        y_column = None
    else:
        # Show both X and Y axis selection for other plot types
        x_column = st.sidebar.selectbox("Select X-axis column", all_columns)
        y_column = st.sidebar.selectbox("Select Y-axis column", all_columns)

    # Generate plot button
    if st.sidebar.button("Generate Plot From The Dataset"):
        with st.spinner("Generating Plot..."):
            try:
                if plot_type in ["📈 Line Plot", "📊 Bar Plot"]:
                    fig = generate_plot(df, x_column, y_column, plot_type)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif plot_type == "📉 Histogram":
                    fig = histogram(df, x_column)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif plot_type == "🥧 Pie Chart":
                    fig = pie_plot(df, x_column)
                    if isinstance(fig, str):  # If there's an error
                        st.error(fig)
                    else:
                        st.plotly_chart(fig, use_container_width=True)
                
                elif plot_type == "🌡️ Heatmap":
                    # Convert categorical columns to numeric for heatmap
                    df_numeric = get_dummies(df.copy())
                    heatmap_buffer = heat_map(df_numeric)
                    if isinstance(heatmap_buffer, str):  # If there's an error
                        st.error(heatmap_buffer)
                    else:
                        st.image(heatmap_buffer)
                
                st.success("Plot generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating plot: {e}")
                st.info("Please make sure you've selected appropriate columns for the chosen plot type.")
    
    elif st.sidebar.button("Generate Output Plot"):
        with st.spinner("Generating Output Plot..."):
            generate_output_plot(response)
        st.success("Thank you for using our assistant. Have a great day!")
else:
    st.sidebar.warning("Please upload a dataset first to create plots.")
    if st.button("Save Response"):
        save_response(response)
# ________________________________Button to generate SQL query without dataset_____________________________________
st.divider()
if st.button("GENERATE SQL QUERY"):
    if input_text.strip():
        try:
            respond = model.generate_content(input_text)
            result = respond.text
            st.subheader('RESULT!')
            st.write(result)
            output_example = f"What is the output for this query?\n\n{result}"
            output_example = model.generate_content(output_example)
            st.code(output_example.text)
            st.success("SQL query generated successfully!")
        except Exception as e:
            st.error(f"Error generating SQL query: {e}")
    else:
        st.error("Please enter a query in the input box.")

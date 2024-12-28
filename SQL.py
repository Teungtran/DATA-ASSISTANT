import streamlit as st
import google.generativeai as genai
import io
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
import pandas as pd
import csv
import numpy as np
import chardet
import os
from data_analysis import analyze_dataset
from Visualization import *
from chat_logic import setup_chat_history, handle_chat_interface
# Streamlit run command: streamlit run SQL.py
# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Build model
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    print("Gemini Pro model loaded successfully.")
except Exception as e:
    st.error(f"Error loading Gemini Pro model: {e}")
    st.stop()

st.set_page_config(page_title="YOUR DATA ANALYST ASSISTANT", layout="wide")
st.title("DATA ANALYST ASSISTANT🤖💾")
st.divider()

st.sidebar.header('INSTRUCTION')
st.sidebar.info('WRITE YOUR QUESTION IN ENGLISH THEN LET THE AI DO THE REST!')
st.sidebar.info('THE MODEL USES GEN_AI USING GEMINI API AND WILL PROVIDE EXPLANATIONS AS WELL.')

# File uploader
option = st.sidebar.selectbox("Select an option", ["Chat with uploaded file", "Chat with SQL query"])

if option == "Chat with uploaded file":
    uploaded_file = st.file_uploader("Upload your CSV or XLSX file (optional)", type=['csv', 'xlsx'])
    df = None
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                result = chardet.detect(uploaded_file.getvalue())
                charenc = result['encoding']
                dialect = csv.Sniffer().sniff(uploaded_file.getvalue().decode(charenc)[:1024], delimiters=[',', ';'])
                delimiter = dialect.delimiter
                df = pd.read_csv(uploaded_file, encoding=charenc, delimiter=delimiter, low_memory=False)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error reading file: {e}")

    if df is not None:
        with st.expander("Data Preview"):
            st.dataframe(df.head(100))

        if st.button("Convert Categorical data to Numeric"):
            df_converted = get_dummies(df)
            st.write("Data after getting dummies:")
            st.dataframe(df_converted.head(100))

        if st.button("Analyze Dataset"):
            with st.spinner("Analyzing dataset..."):
                dataset_info = analyze_dataset(df)
                st.text_area("Dataset Analysis", dataset_info, height=400)
        # Chat interface
        setup_chat_history()
        if df is not None:
            handle_chat_interface(df, GOOGLE_API_KEY, model)

    # Dropdowns for selecting x and y columns for plotting
    st.sidebar.subheader("Select Columns and Plot Type")
    if df is not None:
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        all_columns = df.columns.tolist()

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

        if plot_type in ["🥧 Pie Chart", "📉 Histogram"]:
            x_column = st.sidebar.selectbox("Select column", all_columns)
            y_column = None
        elif plot_type == "🌡️ Heatmap":
            x_column = None
            y_column = None
        else:
            x_column = st.sidebar.selectbox("Select X-axis column", all_columns)
            y_column = st.sidebar.selectbox("Select Y-axis column", all_columns)

        if st.sidebar.button("Generate Plot From The Dataset"):
            with st.spinner("Generating Plot..."):
                try:
                    if plot_type in ["📈 Line Plot", "📊 Bar Plot"]:
                        fig = generate_plot(df, x_column, y_column, plot_type)
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot_type == "📉 Histogram":
                        fig = histogram(df, x_column,plot_type)
                        st.plotly_chart(fig, use_container_width=True)

                    elif plot_type == "🥧 Pie Chart":
                        fig = pie_plot(df, x_column)
                        if isinstance(fig, str):
                            st.error(fig)
                        else:
                            st.plotly_chart(fig, use_container_width=True)

                    elif plot_type == "🌡️ Heatmap":
                        df_numeric = get_dummies(df.copy())
                        heatmap_buffer = heat_map(df_numeric)
                        if isinstance(heatmap_buffer, str):
                            st.error(heatmap_buffer)
                        else:
                            st.image(heatmap_buffer)

                    st.success("Plot generated successfully!")

                except Exception as e:
                    st.error(f"Error generating plot: {e}")
                    st.info("Please make sure you've selected appropriate columns for the chosen plot type.")
    else:
        st.sidebar.warning("Please upload a dataset first to create plots.")

elif option == "Chat with SQL query":
    st.title("Chat with SQL query")
    st.write("Enter your question and get the SQL query as the answer.")
    
    input_text = st.text_input("Enter your question:")
    if st.button("Get SQL query"):
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

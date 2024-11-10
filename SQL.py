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

# ___________________________Function to generate various plot types using Seaborn_____________________________
def generate_plot(df, x_column, y_column, plot_type):
    plt.figure(figsize=(10, 6))
    if plot_type == "Line Plot":
        sns.lineplot(data=df, x=x_column, y=y_column, marker='o')
    elif plot_type == "Bar Plot":
        sns.barplot(data=df, x=x_column, y=y_column)
    elif plot_type == "Histogram":
        sns.histplot(data=df, x=x_column, bins=20, kde=True)   
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'{plot_type}: {y_column} vs {x_column}')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def heat_map(df):
    plt.figure(figsize=(10, 8))
    try:
        sns.heatmap(df.corr(), vmin=-1, vmax=1, center=0, annot=True, cmap='coolwarm', annot_kws={'fontsize': 8, 'fontweight': 'bold'}, cbar=False)
        buf_heat = io.BytesIO()
        plt.savefig(buf_heat, format='png')
        buf_heat.seek(0)
        plt.close()
        return buf_heat
    except Exception as e:
        return f"Error generating heatmap: {e}"

def pie_plot(df, x_column):
    plt.figure(figsize=(10, 8))
    try:
        plt.pie(df[x_column].value_counts(), labels=df[x_column].value_counts().index, autopct='%1.1f%%')
        buf_pie = io.BytesIO()
        plt.savefig(buf_pie, format='png')
        buf_pie.seek(0)
        plt.close()
        return buf_pie
    except Exception as e:
        return f"Error generating pie chart: {e}"


# _____________________________Set up the Streamlit interface_____________________________________
st.set_page_config(page_title="YOUR DATA ANALYST ASSISTANT", layout="wide")
st.title("YOUR DATA ANALYST ASSISTANT")
st.divider()
st.sidebar.header('INSTRUCTION')
st.sidebar.info('WRITE YOUR  QUESTION IN ENGLISH THEN CLICK GENERATE BUTTON TO GET THE SQL QUERY')
st.sidebar.info('THE MODEL USES GEN_AI AND IT WILL GIVE OUT EXPLANATION AS WELL')

# ___________________________________File uploader_______________________________________________
uploaded_file = st.file_uploader("Upload your csv or xlsx file (optional)", type=['csv', 'xlsx'])

# Text area for input
input_text = st.text_area("ENTER YOUR QUESTION:")
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

    # Dropdowns for selecting x and y columns for plotting
    st.sidebar.subheader("Select Columns and Plot Type")
    plot_type = st.sidebar.selectbox("Select Plot Type", ["Line Plot", "Bar Plot", "Histogram","Heatmap","Pie"])

    if plot_type != "Heatmap":
        x_column = st.sidebar.selectbox("Select X column", df.columns)
        if plot_type != "Pie":
            y_column = st.sidebar.selectbox("Select Y column", df.columns)
        else:
            y_column = None
    else:
        x_column = None
        y_column = None


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
    
    # Plot button and handling
    if st.button("Generate Plot"):
        if plot_type == "Heatmap":
            heat_map_img = heat_map(df)
            if isinstance(heat_map_img, str): #check for error message
                st.error(heat_map_img)
            else:
                st.image(heat_map_img, caption=f"Correlation of the dataset")
        elif plot_type == "Pie":
            pie_plot_img = pie_plot(df, x_column)
            if isinstance(pie_plot_img, str): #check for error message
                st.error(pie_plot_img)
            else:
                st.image(pie_plot_img, caption=f"Pie chart of the attribute {x_column}")
        else:
            plot_img = generate_plot(df, x_column, y_column, plot_type)
            st.image(plot_img, caption=f"{plot_type}: {y_column} vs {x_column}")

# _______________________________Button to save response______________________________________
    if st.button("SAVE RESPONSE"):
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
else:
    st.write("No file uploaded")

# ________________________________Button to generate SQL query without dataset_____________________________________
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

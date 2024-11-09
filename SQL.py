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

# Custom ResponseParser to handle plot generation
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

# Function to generate various plot types using Seaborn
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

# Set up the Streamlit interface
st.set_page_config(page_title="YOUR DATA INSIGHT ASSISTANT", layout="wide")
st.title("YOUR DATA INSIGHT ASSISTANT")
st.divider()
st.sidebar.header('INSTRUCTION')
st.sidebar.info('WRITE YOUR SQL QUESTION IN ENGLISH THEN CLICK GENERATE BUTTON TO GET THE SQL QUERY')
st.sidebar.info('THE MODEL USES GEN_AI AND IT WILL GIVE OUT EXPLANATION AS WELL')

# File uploader
uploaded_file = st.file_uploader("Upload your csv or xlsx file (optional)", type=['csv', 'xlsx'])

# Text area for input
input_text = st.text_area("ENTER YOUR QUESTION:")

if uploaded_file is not None:
    try:
        # Load and display data preview
        df = pd.read_csv(uploaded_file, low_memory=False, delimiter=',')
        with st.expander("Data Preview"):
            st.dataframe(df.head(100))

        # Dropdowns for selecting x and y columns for plotting
        st.sidebar.subheader("Select Columns and Plot Type")
        x_column = st.sidebar.selectbox("Select X column", df.columns)
        y_column = st.sidebar.selectbox("Select Y column", df.columns)
        plot_type = st.sidebar.selectbox("Select Plot Type", ["Line Plot", "Bar Plot", "Histogram"])

        # Initialize SmartDataFrame
        llm = GoogleGemini(api_key=GOOGLE_API_KEY)
        sdf = SmartDataframe(df, config={"llm": llm, "response_parser": OutputParser})
        response = sdf.chat(input_text)
        # Generate SQL query for the responded question
        sql_query_prompt = f"Generate the SQL code for the following question: '{input_text}'"
        sql_response = model.generate_content(sql_query_prompt)
        st.subheader("SQL Code")
        # Display response
        st.write(response)
        st.code(sql_response.text)

        # Plot button and handling
        if st.button("Generate Plot"):
            plot_img = generate_plot(df, x_column, y_column, plot_type)
            st.image(plot_img, caption=f"{plot_type}: {y_column} vs {x_column}")

        # Button to save response
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
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")

else:
    st.write("No file uploaded")

# Button to generate SQL query
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

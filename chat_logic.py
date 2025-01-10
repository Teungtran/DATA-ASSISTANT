import streamlit as st
import google.generativeai as genai
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
from Visualization import *
from langchain.prompts import PromptTemplate
import time 
# Custom ResponseParser to handle output formatting
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

def initialize_gemini(api_key):
    genai.configure(api_key=api_key)
    # Initialize model with appropriate parameters
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    return model

def setup_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "previous_file" not in st.session_state:
        st.session_state.previous_file = None   

def clear_chat_history():
    st.session_state.chat_history = []

def save_chat_history():
    try:
        with open("chat_history.txt", "w") as file:
            for chat in st.session_state.chat_history:
                file.write(f"User: {chat['input']}\n")
                file.write(f"Assistant: {chat['response']}\n")
                if chat.get("sql_code"):
                    file.write(f"SQL Code:\n{chat['sql_code']}\n")
                file.write("\n")
        return True
    except Exception as e:
        return str(e)

def chat_with_csv(df, input_text, google_api_key, model):
    try:
        if model is None:
            model = initialize_gemini(google_api_key)
            
        llm = GoogleGemini(api_key=google_api_key)
        result = None
        sql_code = None
        
        analysis_prompt = """
        You are an advanced AI assistant named "Nexus" tasked with answering the user's query {question} based on the provided dataset's extracted {columns}. 
        You are capable of analyzing data from CSV/Excel files, reports, or databases and presenting the output in a DataFrame format.
        Use the following rules:
        - Always utilize all relevant context to generate a complete and accurate response.
        - Respond in the same language as the input question.
        - Identify and extract all mentioned columns in the user query and provide a DataFrame containing relevant data.
        - Ensure the final output is structured in a DataFrame format wherever applicable.
        Input Details:
        - columns: {columns}
        - Question: {question}
        Response Format:
        - Answer: A clear response to the query.
        - DataFrame Output: Present the result of your analysis in a structured DataFrame format, including relevant columns and data.
"""

        AI_prompt = PromptTemplate(input_variables=["question", "columns"], template=analysis_prompt)
        
        if df is not None:
            AI_analysis = AI_prompt.format(question=input_text, columns=df.columns)
            sdf = SmartDataframe(df, config={
                "llm": llm,
                "response_parser": OutputParser,
                "prompt_template": AI_analysis
            })            
            result = sdf.chat(input_text)
        else:   
            # For non-dataframe queries, use the Gemini model directly
            result = model.generate_content(input_text).text

        # Generate SQL code for the question
        sql_prompt = f"Generate the SQL code for the following question: '{input_text}'"
        sql_code = model.generate_content(sql_prompt).text
        
        return result, sql_code
    except Exception as e:
        raise Exception(f"Error in chat processing: {str(e)}")

def handle_chat_interface(df, google_api_key, model):
    st.markdown("### Chat Interface")
    setup_chat_history()

    # Initialize model if not already done
    if model is None:
        model = initialize_gemini(google_api_key)

    # Display existing chat history
    if "chat_history" in st.session_state:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["input"])
            with st.chat_message("assistant"):
                if isinstance(chat["response"], pd.DataFrame):
                    st.dataframe(chat["response"])
                else:
                    st.write(chat["response"])
                if chat.get("sql_code"):
                    with st.expander("Show SQL Code"):
                        st.code(chat["sql_code"], language="sql")

    # Input for new chat message
    if prompt := st.chat_input("Enter your question:"):
        with st.spinner("Analysing..."):
            time.sleep(1)
            with st.chat_message("user"):
                st.write(prompt)
            try:
                # Generate response
                result, sql_code = chat_with_csv(df, prompt, google_api_key, model)
                with st.spinner("Analysing..."):
                    time.sleep(1)
                    with st.chat_message("assistant"):
                        if isinstance(result, pd.DataFrame):  
                            st.dataframe(result)
                        else:
                            st.write(result)
                with st.expander("Show SQL Code"):
                    st.code(sql_code, language="sql")

                # Save to chat history
                st.session_state.chat_history.append({
                    "input": prompt,
                    "response": result,
                    "sql_code": sql_code,
                })
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.sidebar.button("Save Chat History"):
        save = save_chat_history()
        if save is True:
            st.sidebar.success("Chat history saved!")
        else:
            st.sidebar.error(f"Error saving chat history: {save}")
            
def visualize_data(df):
    if df is not None:

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
                        fig = histogram(df, x_column, plot_type)
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

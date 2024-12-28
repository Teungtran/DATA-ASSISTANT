import streamlit as st
import google.generativeai as genai
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
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

def setup_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "previous_file" not in st.session_state:
        st.session_state.previous_file = None

def clear_chat_history():
    st.session_state.chat_history = []
    


def display_chat_history():
    for chat in st.session_state.chat_history:
        st.markdown(f"**User:** {chat['input']}")
        st.markdown(f"**Assistant:** {chat['response']}")
        if chat.get("sql_code"):
            st.code(chat["sql_code"], language="sql")

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
        llm = GoogleGemini(api_key=google_api_key)
        response_text = None
        sql_code = None

        if df is not None:
            sdf = SmartDataframe(df, config={"llm": llm, "response_parser": OutputParser})
            response_text = sdf.chat(input_text)
        else:
            response_text = model.generate_content(input_text).text

        # Generate SQL code for the question
        sql_prompt = f"Generate the SQL code for the following question: '{input_text}'"
        sql_code = model.generate_content(sql_prompt).text

        return response_text, sql_code

    except Exception as e:
        raise Exception(f"Error in chat processing: {e}")

def handle_chat_interface(df, google_api_key, model, uploaded_file=None):
    st.markdown("### Chat Interface")
    # Add manual clear button
    if st.button("Clear Chat History"):
        clear_chat_history()
    # Display existing chat history
    display_chat_history()
    # Chat input
    input_text = st.text_input("Enter your question:")
    if st.button("Send") and input_text.strip():
        try:
            response_text, sql_code = chat_with_csv(df, input_text, google_api_key, model)
            
            # Add to chat history
            st.session_state.chat_history.append({
                "input": input_text,
                "response": response_text,
                "sql_code": sql_code
            })
        except Exception as e:
            st.error(f"An error occurred: {e}")
    # Save chat history button
    if st.sidebar.button("Save Chat History"):
        result = save_chat_history()
        if result is True:
            st.sidebar.success("Chat history saved!")
        else:
            st.sidebar.error(f"Error saving chat history: {result}")


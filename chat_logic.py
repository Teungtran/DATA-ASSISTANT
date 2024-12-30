import streamlit as st
import google.generativeai as genai
from pandasai import SmartDataframe
from pandasai.llm import GoogleGemini
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
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

def setup_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "previous_file" not in st.session_state:
        st.session_state.previous_file = None   
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
        result = None
        sql_code = None

        if df is not None:
            sdf = SmartDataframe(df, config={"llm": llm, "response_parser": OutputParser})
            result = sdf.chat(input_text)
        else:
            result = model.generate_content(input_text).text
        # Generate SQL code for the question
        sql_prompt = f"Generate the SQL code for the following question: '{input_text}'"
        sql_code = model.generate_content(sql_prompt).text
        return result, sql_code
    except Exception as e:
        raise Exception(f"Error in chat processing: {e}")

def handle_chat_interface(df, google_api_key, model):
    st.markdown("### Chat Interface")
    setup_chat_history()

    # Display existing chat history using st.chat_message
    if "chat_history" in st.session_state:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["input"])
            with st.chat_message("assistant"):
                if isinstance(chat["response"], pd.DataFrame):  # Check if it's a DataFrame
                    st.dataframe(chat["response"])
                else:
                    st.write(chat["response"])
                if chat.get("sql_code"):
                    st.code(chat["sql_code"], language="sql")
    # Input for new chat message
    if prompt := st.chat_input("Enter your question:"):
        with st.chat_message("user"):
            st.write(prompt)
        try:
            # Generate response
            result, sql_code = chat_with_csv(df, prompt, google_api_key, model)
            # Display response dynamically
            with st.chat_message("assistant"):
                if isinstance(result, pd.DataFrame):  
                        st.dataframe(result)
                else:
                        st.write(result)
            if st.button("sql_code"):
                st.code(sql_code, language="sql")

            # Save to chat history
            st.session_state.chat_history.append({
                "input": prompt,
                "response": result,
                "sql_code": sql_code,
            })
        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.sidebar.button("Save Chat History"):
        save = save_chat_history()
        if save is True:
            st.sidebar.success("Chat history saved!")
        else:
            st.sidebar.error(f"Error saving chat history: {save}")


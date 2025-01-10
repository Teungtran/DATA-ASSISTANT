from chat_pdf import process_pdf, llm_query
import streamlit as st
from chat_logic import *
from Visualization import *
import pandas as pd
import csv
import chardet
import os
import time     
from data_analysis import analyze_dataset, convert_dates
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
model = None
if GOOGLE_API_KEY:
    model = initialize_gemini(GOOGLE_API_KEY)
# Run command: streamlit run rag_app.py
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
# Page configuration
st.set_page_config(
    page_title="AI Decision-Making System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
    
# Header
st.title("🤖 AI Decision-Making System")
st.markdown("""
### 📊 **Unlock Insights, Automate Reports**
Empower your business with cutting-edge AI features:
- 💬 **Data Chatbots** for your questions.
- 🧠 **Customer Segmentation** to understand your audience better.
- 🌟 **Sentiment Analysis** for smarter decisions.
""")
st.sidebar.title("Our Features ⚙️ ")
option = st.sidebar.radio("Choose a page:", ["About our system", "Analyse Reports", "Extract Data from Database"])
# Divider for clarity
st.divider()
if option == "About our system":
    # Header
    st.subheader("About Our System💡")
    # Call to Action
    st.divider()
    st.markdown("**A welcome from Nexus!🧠**")
#__________________________ABOUT THE SYSTEM____________________________________________________________-________
    file_path = "AI.pdf"
    # Use the hardcoded file path      
    setup_chat_history()
    if "chat_history" in st.session_state:
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["input"])
            with st.chat_message("assistant"):
                st.write(chat["response"])
    if question:= st.chat_input("Enter your question:"):
        with st.chat_message("user"):
            st.write(question)
            with st.status("Thinking......💡"):
                time.sleep(1)
                vecorstore = process_pdf(file_path)
                answer = llm_query(vecorstore, question)
        with st.chat_message("assistant"):
            result = answer.get('result', 'No result found.')
            st.markdown(f"**Answer:** {result}")
            st.session_state.chat_history.append({"input": question,"response": result})
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []

#__________________________CHAT WITH UPLOADED FILE________________________
elif option == "Analyse Reports":
    st.subheader("Analyse Reports📊")
    st.markdown("**Explore your data in an _interactive_ way!**")
    st.divider()
    uploaded_file = st.file_uploader("Upload your CSV or XLSX report file", type=['csv', 'xlsx'])
    df = None
    result = None 
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
                df = convert_dates(df)
    except Exception as e:
        st.error(f"Error reading file: {e}")
    if df is not None:
        with st.expander("Data Preview"):
            st.dataframe(df.head(100))

        # Data preprocessing convert data to numeric
        if st.button("Convert Categorical data to Numeric"):
            df_converted = get_dummies(df)
            with st.expander("Data after getting dummies:"):
                st.dataframe(df_converted.head(100))
        # Analyze dataset
        if st.button("Analyze Dataset"):
            with st.spinner("Analyzing dataset..."):
                with st.expander("DDataset info"):
                    dataset_info = analyze_dataset(df)
                    st.text_area("Dataset Analysis", dataset_info, height=400)
        # Chat interface
        setup_chat_history()
        if df is not None:
                handle_chat_interface(df, GOOGLE_API_KEY, model)
        if st.sidebar.button("Clear Chat History"):
            clear_chat_history()
        # Save response
        # Dropdowns for selecting x and y columns for plotting
        st.sidebar.subheader("Select Columns and Plot Type")
        visualize_data(df)

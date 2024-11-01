import streamlit as st
import google.generativeai as genai

get_api_key = "AIzaSyBxLB3VTohn1tmfG2kMe_Is_XHkRIH7rZU"
genai.configure(api_key=get_api_key)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="THE SQL ASSISTANT",layout="wide")
st.title("THE SQL ASSISTANT")
st.divider()
st.sidebar.header('INSTRUCTION')
st.sidebar.info('WRITE YOUR SQL QUESTION IN ENGLISH THEN CLICK GENERATE BUTTON TO GET THE SQL QUERRY')
st.sidebar.info('THE MODEL USES MYSQL,GEN_AI AND IT WILL GIVE OUT EXPLAINATION AS WELL')

# GIVE INPUT BOX
input = st.text_area("ENTER YOUT SQL QUESTION IN ENGLISH:")

if st.button("GENERATE!"):
    if input.strip():  # Check if input is not empty
        respond = model.generate_content(input)
        result = respond.text
        st.subheader('RESULT!')
        st.write(result)
        output_example = """
            What is the ouput for this query?
            '''
            {result}
        """
        output_example_form = output_example.format(result=result)
        output_example = model.generate_content(output_example_form)
        output_example = output_example.text
        st.write(output_example)
        st.success("SQL query generated successfully!",icon="✅")
        
    else:
        st.error("Please enter a query in the input box.")
        
        #streamlit run SQL.py
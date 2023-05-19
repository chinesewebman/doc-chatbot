import os
import json
import pandas as pd
import streamlit as st
import pdfplumber

from modules.chatbot import Chatbot
from modules.embedder import Embedder

class Utilities:

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        if not hasattr(st.session_state, "api_key"):
            st.session_state.api_key = None
        #you can define your API key in .env directly
        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            user_api_key = os.environ["OPENAI_API_KEY"]
            #st.sidebar.success("API key loaded from .env", icon="🚀")
        else:
            if st.session_state.api_key is not None:
                user_api_key = st.session_state.api_key
                st.sidebar.success("API key loaded from previous input", icon="🚀")
            else:
                user_api_key = st.sidebar.text_input(
                    label="#### Your OpenAI API key 👇", placeholder="sk-...", type="password"
                )
                if user_api_key:
                    st.session_state.api_key = user_api_key

        return user_api_key

    
    @staticmethod
    def handle_upload(file_types):
        """
        Handles and display uploaded_file
        :param file_types: List of accepted file types, e.g., ["csv", "pdf", "txt"]
        """
        uploaded_file = st.sidebar.file_uploader("upload", type=file_types, label_visibility="collapsed")
        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Your CSV file :")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Your PDF file :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file:")
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8")
                file_container.write(content)
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()
            
            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            #if file_extension == ".csv" :
            #    show_csv_file(uploaded_file)
            if file_extension== ".pdf" : 
                show_pdf_file(uploaded_file)
            elif file_extension== ".txt" : 
                show_txt_file(uploaded_file)

            # srore the uploaded file in data directory
            if not os.path.exists(st.session_state['data_directory']):
                os.mkdir(st.session_state['data_directory'])
            full_file_path = os.path.join(st.session_state['data_directory'], uploaded_file.name)
            with open(full_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            #store embeddings for the uploaded file
            embeds = Embedder()
            embeds.storeDocEmbeds(uploaded_file.getbuffer(), uploaded_file.name)

        else:
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file

    @staticmethod
    def setup_chatbot(selected_file, model, temperature):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        full_file_path = os.path.join(st.session_state['data_directory'], selected_file)
        with open(full_file_path, 'rb') as loaded_file:
            # Read the contents of the file
            loaded_file.seek(0)
            file = loaded_file.read()
        embeds = Embedder()

        with st.spinner("处理中..."):
            
            # Get the document embeddings for the selected file
            vectors = embeds.getDocEmbeds(file, loaded_file.name)
            # Create a Chatbot instance with the specified model and temperature
            chatbot = Chatbot(model, temperature,vectors)
        st.session_state["ready"] = True

        return chatbot
    
    @staticmethod
    def load_dict(dict_file):
        # 读取JSON格式词典文件，并初始化用户不良回应次数
        if not hasattr(st.session_state, "bad_attitude_times"):
            st.session_state.bad_attitude_times = 0

        with open(dict_file, encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    @staticmethod
    def get_file_list(data_directory):
        filelist=[]
        for root, dirs, files in os.walk(data_directory):
              for file in files:
                     filelist.append(file) if not file.endswith('.pkl') else None
        return filelist

    

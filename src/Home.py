import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
import modules.embedder

#To be able to update the changes made to modules in localhost (press r)
def reload_module(module_name):
    import importlib
    import sys
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    return sys.modules[module_name]

history_module = reload_module('modules.history')
layout_module = reload_module('modules.layout')
utils_module = reload_module('modules.utils')
sidebar_module = reload_module('modules.sidebar')

ChatHistory = history_module.ChatHistory
Layout = layout_module.Layout
Utilities = utils_module.Utilities
Sidebar = sidebar_module.Sidebar

st.set_page_config(layout="wide", page_icon="💬", page_title="小维摩 | 聊天机器人 🤖")

# Instantiate the main components
layout, sidebar, utils = Layout(), Sidebar(), Utilities()

layout.show_header("PDF, TXT, CSV, DOCX, DOC")

user_api_key = utils.load_api_key()

if not user_api_key:
    layout.show_api_key_missing()
else:
    os.environ["OPENAI_API_KEY"] = user_api_key
    if 'data_directory' not in st.session_state:
        st.session_state['data_directory'] = 'data'

    uploaded_file = utils.handle_upload(["pdf", "docx","doc","txt", "csv"])
    
    if not os.path.exists(st.session_state['data_directory']):
            os.mkdir(st.session_state['data_directory'])
    
    # Configure the sidebar
      
    sidebar.show_options()
    sidebar.about()

    # 判断data目录中是否已有.pkl文件
    if utils.get_file_list(st.session_state['data_directory']):

        # Initialize chat history
        history = ChatHistory()
        # 加载词典并初始化不良回应数
        st.session_state['dict'] = utils.load_dict('user-dict.json')
        #st.sidebar.markdown("### 不良回应数:"+str(st.session_state['bad_attitude_times']))
        sidebar.show_file_selecotr(st.session_state['data_directory'],history)    
        try:
            chatbot = utils.setup_chatbot(
                st.session_state["selected_file"], st.session_state["model"], st.session_state["temperature"]
            )
            st.session_state["chatbot"] = chatbot

            if st.session_state["ready"]:
                # Create containers for chat responses and user prompts
                response_container, prompt_container = st.container(), st.container()
                with prompt_container:
                    # Display the prompt input box
                    is_ready, user_input = layout.prompt_input()
                    # Initialize the chat history
                    history.initialize(st.session_state["selected_file"])
                    # Reset the chat history if button clicked
                    if st.session_state["reset_chat"]:
                        history.reset(st.session_state["selected_file"])
                    if is_ready:
                        # Update the chat history and display the chat messages
                        history.append("user", user_input)
                        old_stdout = sys.stdout
                        sys.stdout = captured_output = StringIO()
                        # Generate the chatbot's response
                        output = st.session_state["chatbot"].check_chat(user_input)
                        sys.stdout = old_stdout
                        history.append("assistant", output)
                        # Clean up the agent's thoughts to remove unwanted characters
                        thoughts = captured_output.getvalue()
                        cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
                        cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)
                        # Display the agent's thoughts
                        with st.expander("显示 agent 的想法"):
                            st.write(cleaned_thoughts)
                history.generate_messages(response_container)
        except Exception as e:
            st.error(f"Error: {str(e)}")
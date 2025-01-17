import os
import streamlit as st
from streamlit_chat import message

class ChatHistory:
    
    def __init__(self):
        self.history = st.session_state.get("history", [])
        st.session_state["history"] = self.history

    def default_greeting(self):
        return "你好，小维摩! 👋"

    def default_prompt(self, topic):
        #return f"您好！很高兴为您服务，请问我关于 {topic} 的问题吧 🤗"
        return f"您好！很高兴为您服务，请问我关于所选文档的问题吧 🤗"
    
    def initialize_user_history(self):
        st.session_state["user"] = [self.default_greeting()]

    def initialize_assistant_history(self, selected_file):
        st.session_state["assistant"] = [self.default_prompt(selected_file)]

    def initialize(self, selected_file):
        if 'assistant' not in st.session_state:
            self.initialize_assistant_history(selected_file)
        if 'user' not in st.session_state:
            self.initialize_user_history()

    def reset(self, selected_file):
        st.balloons()
        st.session_state["history"] = []
        self.initialize_user_history()
        self.initialize_assistant_history(selected_file)
        st.session_state["reset_chat"] = False

    def append(self, mode, message):
        st.session_state[mode].append(message)

    def generate_messages(self, container):
        if st.session_state["assistant"]:
            with container:
                for i in range(len(st.session_state["assistant"])):
                    message(
                        st.session_state["user"][i],
                        is_user=True,
                        key=f"history_{i}_user",
                        avatar_style="avataaars-neutral",
                        seed=30
                    )
                    message(st.session_state["assistant"][i], key=str(i), avatar_style="fun-emoji")

    def load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = f.read().splitlines()

    def save(self):
        with open(self.history_file, "w") as f:
            f.write("\n".join(self.history))

import streamlit as st

class Layout:
    
    def show_header(self, types_files):
        """
        Displays the header of the app
        """
        st.markdown(
            f"""
            <h4 style='text-align: center;'> 从左侧选择一个文件或上传 {types_files} 类型文件然后提问吧 ! 😁 
            如果右上角显示“RUNNING”字样请耐心等待 😁 </h4>
            """,
            unsafe_allow_html=True,
        )

    def show_api_key_missing(self):
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API key</a> to start chatting</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def prompt_input(self):
        """
        Displays the prompt input box
        """
        st.write("---")
        user_input = st.text_input(
            "提问:",
            placeholder="请向我询问与文档相关的问题...",
            key="input",
            label_visibility="collapsed",
            autocomplete="on",
        )
        is_ready = len(user_input) > 0
        return is_ready, user_input
    

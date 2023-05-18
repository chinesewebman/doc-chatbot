import streamlit as st
import os

class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def about():
        about = st.sidebar.expander("🧠 关于净名小维摩 ")
        sections = [
            "#### 净名小维摩是带有会话记忆的聊天机器人，被设计来用于回答与佛法相关的问题 📄",
            "#### 它使用大语言模型来产生基于自然语言的互动. 🌐",
            "#### 目前支持 纯文本文件、Word文件、CSV 和 (可编辑的)PDF 文件，其它格式的支持很快就会上线...",
            "#### 采用的技术： [Langchain](https://github.com/hwchase17/langchain), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5) 和 [Streamlit](https://github.com/streamlit/streamlit) ⚡",
            "#### 源代码参考: [yvann-hub/Robby-chatbot](https://github.com/yvann-hub/Robby-chatbot)",
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def reset_chat_button():
        if st.button("重置聊天"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def delemiter_selector(self):
        text_delimiter = st.selectbox(
            label="文本分隔符",
            options=["###", "两个换行符", "一个换行符"],
            help="文本块之间的分隔符",
        )
        if text_delimiter == "两个换行符":
            text_delimiter = "\n\n"
        if text_delimiter == "一个换行符":
            text_delimiter = "\n"
        st.session_state["text_delimiter"] = text_delimiter

    def chunk_size_slider(self):
        chunk_size = st.slider(
            label="文本块大小",
            min_value=100,
            max_value=2500,
            value=1100,
            step=100,
            help="文本块的最大长度（当前单位为token数）。文档一般将被分成多个文本块。",
        )
        st.session_state["chunk_size_limit"] = chunk_size

    def top_k_slider(self):
        top_k = st.slider(
            label="Top k",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            help="每次语义查询匹配到的文本块最大数量，这个值设的越大，查询的速度就越慢。",
        )
        st.session_state["top_k"] = top_k

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
            help="用于控制语义查询的多样性，值越大，查询结果越多样化，但是也越不可预测。"
        )
        st.session_state["temperature"] = temperature

    def show_file_selecotr(self, data_directory, history):
        def reset_history():
            history.reset(st.session_state["selected_file"])
            history.initialize_assistant_history(st.session_state["selected_file"])
        filelist=[]
        for root, dirs, files in os.walk(data_directory):
              for file in files:
                     filelist.append(file) if not file.endswith('.pkl') else None
        st.session_state.selected_file = st.sidebar.selectbox("选择一个文件:", filelist, index=0, on_change=reset_history)
    
        
    def show_options(self):
        with st.sidebar.expander("🛠️ 小维摩的设置", expanded=True):

            self.reset_chat_button()
            self.chunk_size_slider()
            self.delemiter_selector()
            self.top_k_slider()
            self.model_selector()
            self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)
            st.session_state.setdefault("top_k", 3)
            st.session_state.setdefault("text_delimiter", "###")
            st.session_state.setdefault("chunk_size_limit", 1100)
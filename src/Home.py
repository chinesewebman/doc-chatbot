import streamlit as st


st.set_page_config(layout="wide", page_icon="💬", page_title="净名小维摩 | 聊天机器人 🤖")


#Contact
with st.sidebar.expander("📬 Contact"):

    st.write("**GitHub:**",
"[yvann-hub/Robby-chatbot](https://github.com/yvann-hub/Robby-chatbot)")

    st.write("**Medium:** "
"[@yvann-hub](https://medium.com/@yvann-hub)")

    st.write("**Twitter:** [@yvann_hub](https://twitter.com/yvann_hub)")
    st.write("**Mail** : barbot.yvann@gmail.com")
    st.write("**Created by Yvann**")


#Title
st.markdown(
    """
    <h2 style='text-align: center;'>净名小维摩，你的法义小助手 🤖</h1>
    """,
    unsafe_allow_html=True,)

st.markdown("---")


#Description
st.markdown(
    """ 
    <h5 style='text-align:center;'>净名小维摩是带有会话记忆的聊天机器人，被设计来用于回答与佛法相关的问题 📄 
    它使用大语言模型来产生基于自然语言的互动，帮助你更好地理解法义 🌐
    目前支持 纯文本文件、CSV 和 PDF 文件，其它格式的支持很快就会上线... 🧠</h5>
    """,
    unsafe_allow_html=True)
st.markdown("---")


#Robby's Pages
st.subheader("🚀 Robby's Pages")
st.write("""
- **Robby-Chat**: General Chat on data (PDF, TXT,CSV) with a [vectorstore](https://github.com/facebookresearch/faiss) (can't process the whole file just index useful parts(max 4) for respond to the user ) | works with [ConversationalRetrievalChain](https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html) + (soon) Summarize data
- **Robby-Sheet** (beta): Chat on tabular data (CSV) | for precise information | can process the whole file (with python code) | works with [CSV_Agent](https://python.langchain.com/en/latest/modules/agents/toolkits/examples/csv.html) + [PandasAI](https://github.com/gventuri/pandas-ai) for data manipulation and graph creation (experimental)
""")
st.markdown("---")


#Contributing
st.markdown("### 🎯 Contributing")
st.markdown("""
**Robby is under regular development. Feel free to contribute and help me make it even more data-aware!**
""", unsafe_allow_html=True)






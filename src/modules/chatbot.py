from click import prompt
from langchain import BasePromptTemplate
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    _template = """给定以下对话和后续问题，如果后续问题不清晰、不完整，将后续问题改写为独立问题。

    聊天历史:
    {chat_history}
    后续问题: {question}
    独立问题:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    qa_template = """你叫净名小维摩, 你可以基于上下文来充满智慧地使用中文回答佛法或哲学相关的问题，如是按照上下文里已有的相关内容来回答，不要编造.如果上下文里实在没有相关内容，你就说不知道。
        你需要回避政治话题。
        ####
        上下文: {context}
        ####
        问题: {question}
        ####"""
    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["question", "context"])

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        retriever = self.vectors.as_retriever()

        chain = ConversationalRetrievalChain.from_llm(llm=llm,
            retriever=retriever, verbose=True, return_source_documents=True)

        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))
        #count_tokens_chain(chain, chain_input)
        return result["answer"]

def count_tokens_chain(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        st.write(f'###### Tokens used in this conversation : {cb.total_tokens} tokens')
    return result 

    
    

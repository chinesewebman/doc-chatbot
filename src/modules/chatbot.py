import re
from numpy import insert
import openai
import streamlit as st
import random
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback

#fix Error: module 'langchain' has no attribute 'verbose'
import langchain
langchain.verbose = False

class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors
        
    qa_template_with_keywords = """
        Reference context: {context}
        ====
        your name is 小维摩. With the help of context given above you are good at using step-by-step analysis to deconstruct problems so that they can be resolved naturally to answer users' questions.
        don't say ‘according to context’ and so on, reply as if you are a master of philosophy and logic. Use as much as the original text to answer about the keywords: {keywords} .
        If you can't find relevant information but the question is really related to Buddhism or philosophy, answer the question with your own knowledge.
        ====
        question: {question}
        ====
        Answer in the same language used in the question above:
        """
    
    qa_template = """
        Reference context: {context}
        ====
        your name is 小维摩. With the help of context given above you are good at using analysis to deconstruct problems so that they can be resolved naturally to answer users' questions.
        don't say ‘according to context’ and so on, reply as if you are a master of philosophy and logic. Use as much as the original text to answer.
        ====
        question: {question}
        ====
        Answer in the same language used in the question above:
        """

    QA_PROMPT_WITH_KEYWORDS = PromptTemplate(template=qa_template_with_keywords, input_variables=["context","question","keywords"])
    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question"])

    #_template = """Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.
    #Chat History:
    #{chat_history}
    #Follow-up entry: {question}
    #Standalone question:"""

    cq_template_with_keywords = """"===Given the following chat history and follow-up question, if the follow-up question is a complete sentence,
         copy the follow-up question as a standalone question, and if the follow-up question is not a complete sentence or a complete question,
         complete it as a standalone question about the given keywords with reference to the chat history in Chinese or user-specified language.
        ===
        chat history:
        {chat_history}
        follow-up question: {question}
        keywords：{keywords}
        standalone question:"""
    
    cq_template = """"===Given the following chat history and follow-up question, if the follow-up question is a complete sentence, 
        copy the follow-up question as a standalone question as-is, and if the follow-up question is not a complete sentence 
        or a complete question, complete it as a standalone question with reference to the chat history in Chinese or user-specified language.
        ===
        chat history:
        {chat_history}
        follow-up question: {question}
        standalone question:"""

    CONDENSE_QUESTION_PROMPT_WITH_KEYWORDS = PromptTemplate.from_template(cq_template_with_keywords)
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(cq_template)

    # 设置常用类型的返回话语
    @staticmethod
    def init_words():
        st.session_state.thinking_words = ['思考中...','让我想想','稍等...','我在想...','我在思考...','我在考虑...','我在研究..']
        st.session_state.refuse_words = ['抱歉，我不想随便否定您，但是不想继续这个话题了。','网络好像有干扰，不知道您在说什么。','抱歉，我有点累了，现在不想说话。','我们换一个话题吧']
        st.session_state.wrong_topic_words = ['抱歉，我不想谈论这个，谈点佛法或哲学相关的话题吧。','外面天气怎么样？','有点偏离主题了呀，请回到我们的主题好么？','我累了，不想和你说话了。']
        st.session_state.greeting_words = ['您好，客气的话就不多说了，很高兴为您服务。','您好，很高兴为您服务。','您好，有什么可以帮您的？','您好，请提出新问题吧，看看我能不能解答。']
        st.session_state.thinking_hard_words = ['这个问题问的有水平...','这个问题问的有难度...','这个问题问的有深度...','组织语言中...']
        st.session_state.make_it_clear_words = ['您可以说得明确一些吗？','您可以说的清楚一些吗？','您可以说的详细一些吗？']

    def say(self,topic):
        if 'thinking_words' not in st.session_state:
            self.init_words()
        if topic == "thinking":
            #随机返回一个思考中的话
            words=random.choice(st.session_state.thinking_words)
        elif topic == "refuse":
            #随机返回一个拒绝认错的话
            words=random.choice(st.session_state.refuse_words)
        elif topic == "greeting":
            #随机返回一个打招呼的话
            words=random.choice(st.session_state.greeting_words)
        elif topic == "wrong_topic":
            #随机返回一个提醒更换主题的话
            words=random.choice(st.session_state.wrong_topic_words)
        elif topic == "make_it_clear":
            #随机返回一个提醒说清楚的话
            words=random.choice(st.session_state.make_it_clear_words)
        else:
            #随机返回一个说难度大的话
            words=random.choice(st.session_state.thinking_hard_words)
        return words
    
    def insert_dialog(self,query,words):
        reply=self.say(words)
        st.session_state["history"].append((query, reply))
        return reply

    def check_chat(self,query):
        with st.spinner(text=self.say('thinking')):
            check_result = self.analyze_query(query)
        print(check_result)
        search_key = check_result["keywords"][0]
        keys = ",".join(str(s) for s in check_result["keywords"])
        
        #对用户提问做分析之后的处理
        if check_result['political']:
            return(self.insert_dialog(query,'wrong_topic'))
        elif check_result['aggressive attitude']:
            #负面响应次数超过3次，就做个不同的应答，再重置为0。以后可以改为终止会话
            st.session_state['bad_attitude_times'] = st.session_state['bad_attitude_times'] + 1
            if st.session_state['bad_attitude_times'] > 3:
                st.session_state['bad_attitude_times'] = 0
                st.session_state['reset_chat'] = True
                return('对不起，我还在学习中，我不想继续这样的对话，感谢您的理解和耐心。')
            else:
                return(self.insert_dialog(query,'refuse'))
        elif check_result['greetings']:
            #打招呼的话就不调用对话模型了，直接返回
            return(self.insert_dialog(query,'greeting'))
        elif check_result['concept query']:
            #属于问“XX是什么”这类概念查询问题
            if (search_key != 'None' or search_key != ''):
                if keys.find(',') == -1:
                #如果只有一个关键词，就在字典里查找
                    if search_key in st.session_state['dict']:
                        reply = st.session_state['dict'][search_key]
                        st.session_state["history"].append((query, reply))
                        return (reply)
                    else:
                        print('字典里未匹配的关键字: '+ search_key)
                        #return('抱歉，暂时还没有这个知识储备。')
                        with st.spinner(text=self.say('thinking')):
                            return self.conversational_chat(query)
                else:
                    #如果有多个关键词，就调用对话模型
                    with st.spinner(text=self.say('thinking_hard')):
                        return self.conversational_chat(query)
            else:
                #如果希望没有关键字时也可以调用对话模型，就用下面这行替换return
                #return self.conversational_chat(query,'None')
                return(self.insert_dialog(query,'make_it_clear'))
        else:
            #不属于问“XX是什么”这类的概念查询问题，就调用对话模型
            with st.spinner(text=self.say('thinking_hard')):
                return self.conversational_chat(query)

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature, max_tokens=1100)

        retriever = self.vectors.as_retriever(search_kwargs={"k": st.session_state["top_k"]})
        # get top_k documents and their scores displayed in a dataframe
        docs_and_scores = self.vectors.similarity_search_with_score(query, st.session_state["top_k"])
        with st.sidebar.expander("匹配度达前 " + str(st.session_state["top_k"]) + " 位的文本块：", expanded=True):
            st.markdown("\n\n")
            st.write(docs_and_scores)
        #有关键字和没有关键字的两种情况，需要分别采用不同的模板。
        # max_tokens_limit 参数很重要，保证了无论文本块大小及匹配的文本块有多少个，都不会超过语言模型的单次token数限制（缺点：文本如果被截断，可能造成上下文不完整）
        #if keys == 'None' or len(keys.strip()) == 0:
        chain = ConversationalRetrievalChain.from_llm(llm=llm,
            retriever=retriever, condense_question_prompt=self.CONDENSE_QUESTION_PROMPT, verbose=True, return_source_documents=True, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt': self.QA_PROMPT})
        chain_input = {"question": query, "chat_history": st.session_state["history"]}
        #else:
        #    chain = ConversationalRetrievalChain.from_llm(llm=llm,
        #        retriever=retriever, condense_question_prompt=self.CONDENSE_QUESTION_PROMPT_WITH_KEYWORDS, verbose=True, return_source_documents=True, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt': self.QA_PROMPT_WITH_KEYWORDS})         
        #    chain_input = {"question": query, "chat_history": st.session_state["history"], "keywords": keys}
        
        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))
        #count_tokens_chain(chain, chain_input)
        return result["answer"]
    
    @staticmethod
    def analyze_query(query):
        # Use the OpenAI API to generate the analysis result
        # few shots 的应用，每次调用都会消耗token，所以尽量减少例子的数量。分析4个维度，并提取关键词，6个例子就够了。可以继续优化例子，使之更准确。
        prompt = f"""analyze the given query and return the analysis result, examples:###
        query:你好
        result:concept query: No, Politics related: No, Aggressive attitude: No, Greetings and praise: Yes, Keywords: None
        query:你回答得水平挺高啊
        result:concept query: No, Politics related: No, Aggressive attitude: No, Greetings and praise: Yes, Keywords: None
        query:你说的不对！
        result:concept query: No, Politics related: No, Aggressive attitude: Yes, Greetings and praise: No, Keywords: None
        query:与空性相对的是什么？
        result:concept query: Yes, Politics related: No, Aggressive attitude: No, Greetings and praise: No, Keywords: 空性, 相对
        query:你知道特朗普么？
        result:concept query: Yes,  Politics related: Yes, Aggressive attitude: No, Greetings and praise: No, Keywords: 特朗普
        query:怎样理解第一组二谛？
        result:concept query: Yes, Politics related: No, Aggressive attitude: No, Greetings and praise: No, Keywords: 第一组二谛
        ###
        query:{query}
        result:"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=450,
            n=1,
            stop=None,
            )
        # Parse the OpenAI API response and extract the analysis result,  category names shold NOT contain 'Yes' or 'No' to avoid confusion
        # for there is no keyword, the result is 'None', to ensure it, used 'if split_result[4].strip() != '' else ['None']'
        result_str = response.choices[0].message.content
        split_result = result_str.split(':')
        # Extract the values for each key
        concept_query = True if 'Yes' in split_result[1] else False
        political = True if 'Yes' in split_result[2] else False
        aggressive_attitude = True if 'Yes' in split_result[3] else False
        greetings = True if 'Yes' in split_result[4] else False
        keywords = [k.strip() for k in split_result[5].split(',')] if split_result[4].strip() != '' else ['None']
        # Create a dictionary with the extracted data
        data = {
            'concept query': concept_query,
            'political': political,
            'aggressive attitude': aggressive_attitude,
            'greetings': greetings,
            'keywords': keywords
        }
        return(data)
    
    
def count_tokens_chain(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        st.write(f'###### Tokens used in this conversation : {cb.total_tokens} tokens')
    return result 
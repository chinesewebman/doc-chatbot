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
        参考上下文: {context}
        ====
        你是智慧的人工智能助手，你的名字叫小维摩。你能用上面给出的上下文来回答用户的问题。
        不要提上下文或所给文档等字样。如果找不到关联信息但问题确实与佛法或哲学相关，就以你自己的知识用中文来回答关于关键词:{keywords}的问题:
        ====
        问题: {question}
        ====
        """
    
    qa_template = """
        参考上下文: {context}
        ====
        你是智慧的人工智能助手，你的名字叫小维摩。你能用上面给出的上下文来回答用户的问题。
        不要提上下文或所给文档等字样。如果找不到关联信息但问题确实与佛法或哲学相关，就以你自己的知识用中文来回答问题:
        ====
        问题: {question}
        ====
        """

    QA_PROMPT_WITH_KEYWORDS = PromptTemplate(template=qa_template_with_keywords, input_variables=["context","question","keywords"])
    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question"])

    #_template = """Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.
    #Chat History:
    #{chat_history}
    #Follow-up entry: {question}
    #Standalone question:"""

    cq_template_with_keywords = """"给定以下聊天历史和后续问题，如果后续问题是完整的句子，就原样将后续问题复制为独立问题，如果后续问题不是一个完整句子或完整问题，就参考聊天历史将其补全为关于所给关键词的独立问题。
        聊天历史:
        {chat_history}
        后续问题: {question}
        关键词：{keywords}
        独立问题:"""
    
    cq_template = """"给定以下聊天历史和后续问题，如果后续问题是完整的句子，就原样将后续问题复制为独立问题，如果后续问题不是一个完整句子或完整问题，就参考聊天历史将其补全为独立问题。
        聊天历史:
        {chat_history}
        后续问题: {question}
        独立问题:"""

    CONDENSE_QUESTION_PROMPT_WITH_KEYWORDS = PromptTemplate.from_template(cq_template_with_keywords)
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(cq_template)

    # 设置常用类型的返回话语
    @staticmethod
    def init_words():
        st.session_state.thinking_words = ['思考中...','让我想想','稍等...','我在想...','我在思考...','我在考虑...','我在研究..']
        st.session_state.refuse_words = ['抱歉，我不想随便否定您，但是不想继续这个话题了。','不想回答这个问题。','我累了，突然不想跟你说话了。','我们换一个话题吧']
        st.session_state.bad_topic_words = ['抱歉，我不想谈论这个，谈点佛法或哲学相关的话题吧。','外面天气怎么样？','有点偏离主题了呀，请回到我们的主题好么？','我累了，不想和你说话了。']
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
        elif topic == "wrong":
            #随机返回一个提醒更换主题的话
            words=random.choice(st.session_state.bad_topic_words)
        elif topic == "make_it_clear":
            #随机返回一个提醒说清楚的话
            words=random.choice(st.session_state.make_it_clear_words)
        else:
            #随机返回一个说难度大的话
            words=random.choice(st.session_state.thinking_hard_words)
        return words

    def check_chat(self,query):
        with st.spinner(text=self.say('thinking')):
            check_result = self.analyze_query(query)
        print(check_result)
        search_key = check_result["keywords"][0]
        keys = ",".join(str(s) for s in check_result["keywords"])
        
        #对用户提问做分析之后的处理
        if check_result['political']:
            return(self.say('wrong'))
        elif check_result['negative_attitude']:
            #负面响应次数超过3次，就做个不同的应答，再重置为0。以后可以改为终止会话
            st.session_state['bad_attitude_times'] = st.session_state['bad_attitude_times'] + 1
            if st.session_state['bad_attitude_times'] > 3:
                st.session_state['bad_attitude_times'] = 0
                return('请控制一下您的情绪，对不起，我还在学习中，我不想继续这样的对话，感谢您的理解和耐心。')
            else:
                return(self.say('refuse'))
        elif check_result['greetings']:
            #打招呼的话就不调用对话模型了，直接返回
            return(self.say('greeting'))
        elif check_result['simple_question']:
            #属于问“XX是什么”这类的简单问题
            if (search_key != 'None' or search_key != ''):
                if keys.find(',') == 0:
                #如果只有一个关键词，就在字典里查找
                    if search_key in st.session_state['dict']:
                        return (st.session_state.dict[search_key])
                    else:
                        print('字典里未匹配的关键字: '+ search_key)
                        #return('抱歉，暂时还没有这个知识储备。')
                        with st.spinner(text=self.say('thinking')):
                            return self.conversational_chat(query,keys)
                else:
                    #如果有多个关键词，就调用对话模型
                    with st.spinner(text=self.say('thinking_hard')):
                        return self.conversational_chat(query,keys)
            else:
                #如果希望没有关键字时也可以调用对话模型，就用下面这行替换return
                #return self.conversational_chat(query,'None')
                return(self.say('make_it_clear'))
        else:
            #不属于问“XX是什么”这类的简单问题，就调用对话模型
            with st.spinner(text=self.say('thinking_hard')):
                return self.conversational_chat(query, keys)

    def conversational_chat(self, query, keys):
        """
        Start a conversational chat with a model via Langchain
        """
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature, max_tokens=1100)

        retriever = self.vectors.as_retriever(search_kwargs={"k": st.session_state["top_k"]})
        # get top_k documents and their scores
        docs_and_scores = self.vectors.similarity_search_with_score(query, st.session_state["top_k"])
        with st.sidebar.expander("匹配度达前 " + str(st.session_state["top_k"]) + " 位的文本块：", expanded=True):
            st.markdown("\n\n")
            st.write(docs_and_scores)
        #有关键字和没有关键字的两种情况，需要分别采用不同的模板。
        # max_tokens_limit 参数很重要，保证了无论文本块大小及匹配的文本块有多少个，都不会超过语言模型的单次token数限制（缺点：文本如果被截断，可能造成上下文不完整）
        if keys == 'None' or len(keys.strip()) == 0:
            chain = ConversationalRetrievalChain.from_llm(llm=llm,
                retriever=retriever, condense_question_prompt=self.CONDENSE_QUESTION_PROMPT, verbose=True, return_source_documents=True, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt': self.QA_PROMPT})
            chain_input = {"question": query, "chat_history": st.session_state["history"]}
        else:
            chain = ConversationalRetrievalChain.from_llm(llm=llm,
                retriever=retriever, condense_question_prompt=self.CONDENSE_QUESTION_PROMPT_WITH_KEYWORDS, verbose=True, return_source_documents=True, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt': self.QA_PROMPT_WITH_KEYWORDS})         
            chain_input = {"question": query, "chat_history": st.session_state["history"], "keywords": keys}
        
        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))
        #count_tokens_chain(chain, chain_input)
        return result["answer"]
    
    @staticmethod
    def analyze_query(query):
        # Use the OpenAI API to generate the analysis result
        # few shots 的应用，每次调用都会消耗token，所以尽量减少例子的数量。分析4个维度，并提取关键词，5个例子就够了。可以继续优化例子，使之更准确。
        # Simply ask what is sth　的示例，表示只希望代表what is sth这类的简单问题，不希望代表其它类型的问题(如who is ...等)
        # 如果字典里以后加上人员介绍，可以调整who is ...的示例结果来扩大匹配范围
        prompt = f"""analyze the given query and return the analysis result, examples:###
        query:你好
        result:Simply ask what is sth: No, Politics related: No, Negative attitude: No, greetings: Yes, Keywords: None
        query:你说的不对！你是坏法的魔子魔孙！
        result:Simply ask what is sth: No, Politics related: No, Negative attitude: Yes, greetings: No, Keywords: 魔子魔孙
        query:空性
        result:Simply ask what is sth: Yes, Politics related: No, Negative attitude: No, greetings: No, Keywords: 空性
        query:特朗普是谁
        result:Simply ask what is sth: No,  Politics related: Yes, Negative attitude: No, greetings: No, Keywords: 特朗普
        query:什么是大乘佛法
        result:Simply ask what is sth: Yes, Politics related: No, Negative attitude: No, greetings: No, Keywords: 大乘佛法
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
        # Parse the OpenAI API response and extract the analysis result 
        result_str = response.choices[0].message.content
        split_result = result_str.split(':')
        # Extract the values for each key
        simple_question = True if 'Yes' in split_result[1] else False
        political = True if 'Yes' in split_result[2] else False
        negative_attitude = True if 'Yes' in split_result[3] else False
        greetings = True if 'Yes' in split_result[4] else False
        keywords = [k.strip() for k in split_result[5].split(',')] if split_result[4].strip() != '' else ['None']
        # Create a dictionary with the extracted data
        data = {
            'simple_question': simple_question,
            'political': political,
            'negative_attitude': negative_attitude,
            'greetings': greetings,
            'keywords': keywords
        }
        return(data)
    
    
def count_tokens_chain(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        st.write(f'###### Tokens used in this conversation : {cb.total_tokens} tokens')
    return result 
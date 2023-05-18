import os
import pickle
import tempfile
import streamlit as st
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders.word_document import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.text_splitter import NLTKTextSplitter
#from langchain.text_splitter import CharacterTextSplitter

class Embedder:

    def __init__(self):
        self.PATH = st.session_state['data_directory']
        self.createEmbeddingsDir()

    def createEmbeddingsDir(self):
        """
        Creates a directory to store the embeddings vectors
        """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    def storeDocEmbeds(self, file, original_filename):
        """
        Stores document embeddings using Langchain and FAISS
        """
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(file)
            tmp_file_path = tmp_file.name
            
        def get_file_extension(uploaded_file):
            file_extension =  os.path.splitext(uploaded_file)[1].lower()
            
            return file_extension
        
        #这个文本分割器效果可以的，能指定分隔符，会按分隔符在列表里的次序逐级试着做分割
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size = st.session_state.chunk_size_limit,
                chunk_overlap  = 20,
                separators = [st.session_state.text_delimiter,"\n", " ", ""])
        
        #这个文本分割器产生的索引会报chunk过大的错误，在查询时上下文是空白的
        #text_splitter = NLTKTextSplitter(
        #    chunk_size = st.session_state.chunk_size_limit,
        #    chunk_overlap  = 20,
        #    separator = st.session_state.text_delimiter,
        #)
        
        #这个文本分割器过于简单了，没有长度控制参数，轻易就会超过openai的限制
        #text_splitter = CharacterTextSplitter(
        #    separator = st.session_state.text_delimiter,  
        #)

        file_extension = get_file_extension(original_filename)

        if file_extension == ".csv":
            loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8",csv_args={
                'delimiter': ',',})
            data = loader.load()

        elif file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)  
            data = loader.load_and_split(text_splitter)
        
        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load_and_split(text_splitter)

        elif file_extension == ".docx" or file_extension == ".doc":
            loader = Docx2txtLoader(file_path=tmp_file_path)
            data = loader.load_and_split(text_splitter)
            
        embeddings = OpenAIEmbeddings()

        vectors = FAISS.from_documents(data, embeddings)
        os.remove(tmp_file_path)

        # Save the vectors to a pickle file
        print (f"保存向量索引文件：{self.PATH}/{original_filename}.pkl")
        with open(f"{self.PATH}/{original_filename}.pkl", "wb") as f:
            pickle.dump(vectors, f)

    def getDocEmbeds(self, file, original_filename):
        """
        Retrieves document embeddings
        """
        if not os.path.isfile(f"{original_filename}.pkl"):
            print (f"{original_filename}.pkl"+" not exist, try to storeDocEmbeds")
            self.storeDocEmbeds(file, os.path.basename(original_filename))

        # Load the vectors from the pickle file
        with open(f"{original_filename}.pkl", "rb") as f:
            vectors = pickle.load(f)
        
        return vectors
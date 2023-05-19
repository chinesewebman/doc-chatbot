# doc-chatbot 🤖

### An AI chatbot featuring conversational memory, designed to enable users to discuss their CSV, PDF, DOCX and TXT data in a more intuitive manner. plus, you can put a dictionary as a fixed local knowledge base📄
![Robby](robby-pic.png)
based on Robby the Robot from [Forbidden Planet](https://youtu.be/bflfQN_YsTM)

By integrating the strengths of Langchain and OpenAI, Robby employs large language models to provide users with seamless, 
context-aware natural language interactions for a better understanding of their data.🧠
#### For better understanding, see my medium article 🖖 : [Build a chat-bot over your CSV data](https://medium.com/@yvann-hub/build-a-chatbot-on-your-csv-data-with-langchain-and-openai-ed121f85f0cd)
## Quick Start 🚀

[![Robby-Chatbot](https://img.shields.io/static/v1?label=Robby-Chatbot&message=Visit%20Website&color=ffffff&labelColor=ADD8E6&style=for-the-badge)](https://robby-chatbot.com)

#### Based on Robby chatbot, more features added:
- multiple files supports, you can choose which file you want to ask about
- word files (.docx) supports
- local dictionary supports, if user query like "what is X", a local dict will be used in the first place to answer directly, this can avoid the hallucination of AI
- a custom moderation supports, it will analyze the altitude and topic, helps to maintain the converstaion in the way you specified
- some details tune: token exceeds limitation bug fix, random spin text displaying during waiting the response from chatgpt, custom chunk_size and chunk separator for text-splitter, custom top_k for retriever, custom prompt with or without keywords, chunk score display and so on...

#### removed feature:
- CSV agent, because I don't need it, you can find it in the original project: https://github.com/yvann-hub/Robby-chatbot

## TO-DO :
- [x] enable print tokens utilizations for the conversation
- [ ] Add free models like vicuna and free embeddings
- [ ] Replace chain of the chatbot by a custom agent for handling more features | memory + vectorstore + custom prompt

## Running Locally 💻
Follow these steps to set up and run the service locally :

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
Clone the repository :

`git clone https://github.com/chinesewebman/doc-chatbot.git`


Navigate to the project directory :

`cd doc-chatbot`


Create a virtual environment :
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

Install the required dependencies in the virtual environment :

`pip install -r requirements.txt`


Launch the chat service locally :

`streamlit run src/Home.py`

#### That's it! The service is now up and running locally. 🤗

## Contributing 🙌
Contributions are always welcome! If you want to contribute to this project, please open an issue, submit a pull request or contact the creator of Robby at barbot.yvann@gmail.com (: or me: chinesewebman@163.com



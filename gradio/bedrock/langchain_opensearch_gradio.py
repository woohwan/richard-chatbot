#!/usr/bin/env python
# coding: utf-8

# ### BedRcok Client 생성

# In[2]:


# create boto3 session for interacting with AWS
import boto3
session = boto3.Session(region_name='us-east-1')
# create bedrock client
br_client = session.client('bedrock-runtime')


# ### Cluade-v2 LLM Model 생성

# In[3]:


# Create LLM Model using claude-v2 model and langchain
from langchain.chat_models import BedrockChat
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# https://python.langchain.com/docs/integrations/chat/bedrock
chat_model = BedrockChat(
  model_id="anthropic.claude-v2",
  client=br_client,
  model_kwargs={
    "max_tokens_to_sample": 512,
    "temperature": 0.9,
    "top_p": 0.9,
    "top_k": 50,
  },
)


# ### OpenSearch RAG
# 임베딩은 embedding opensearch 참고

# #### OpenSearch 연결

# In[4]:


from opensearchpy import OpenSearch

#  opensearch info
host = 'localhost'
port = 9200
http_auth = ('admin', 'admin')
opensearch_endpoint = f'https://{host}:{port}'

# certs info: https://www.notion.so/Certificate-Password-8087893ff1b24dd0b71e66c9916fa55a
ca_cert = 'certs/root-ca.pem'
client_cert = 'certs/admin.pem'
client_key = 'certs/admin-key.pem'


# create client
os_client = OpenSearch(
    hosts=[opensearch_endpoint],
    http_auth=http_auth,
    ca_certs=ca_cert,
    client_cert=client_cert,
    client_key=client_key,
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

# verify connection
print(os_client.info())


# #### OpenSearch VectorStore DB

# In[5]:


# create a embeding model
from langchain.embeddings import BedrockEmbeddings

llm_emb = BedrockEmbeddings(
    model_id='amazon.titan-embed-text-v1',
    client=br_client,
    region_name='us-east-1'
)


# In[6]:


from langchain.vectorstores import OpenSearchVectorSearch
index_name = "constitution-with-nori"

vector_db = OpenSearchVectorSearch(
    opensearch_url=opensearch_endpoint,
    index_name=index_name,
    embedding_function=llm_emb,
    http_auth=http_auth,
    ca_certs=ca_cert,
    client_cert=client_cert,
    client_key=client_key,
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


# In[7]:


query="민주공화국"
docs = vector_db.similarity_search(query=query, k=3)
print(docs[0].page_content)


# In[8]:


# Reriever
retriever = vector_db.as_retriever()


# ### Gradio UI

# In[19]:


import gradio as gr
from operator import itemgetter
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

# https://python.langchain.com/docs/modules/data_connection/retrievers/
# define a prompt template
template= """Answer the question based only on the following context:

{context}

Qeustion: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
  context_docs = "\n\n".join([d.page_content for d in docs])
  print(context_docs)
  return context_docs

# Create conversation history
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

chain = (
        {"context": itemgetter("question")| retriever | format_docs, 
         "question": RunnablePassthrough()
        }
        | prompt
        | chat_model
        | StrOutputParser()
)

# chain.invoke("헌법 1조 2항은?")

def stream_response(input, history):
  if input is not None:
    partial_message = ""
    print(input)
    for response in chain.stream({"question": input}):
      partial_message += response
      yield partial_message

# https://www.gradio.app/docs/chatinterface
gr.ChatInterface(stream_response, title="Chat with Claude").queue().launch()


# In[ ]:





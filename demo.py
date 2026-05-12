import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace

from langchain_core.messages import HumanMessage

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

print("TOKEN:", HF_TOKEN)

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=HF_TOKEN,
    max_new_tokens=100,
)

chat_model = ChatHuggingFace(llm=llm)

response = chat_model.invoke([
    HumanMessage(content="Hello")
])

print(response.content)
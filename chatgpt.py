import streamlit as st
import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma
import unstructured_pytesseract
import tqdm
import constants

unstructured_pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True

@st.cache
def load_data():
    if PERSIST and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
        loader = CSVLoader(r"data/Attack/Data Manipulation (DM)/AS1.csv")
        test = loader.load()
    else:
        loader = DirectoryLoader("data/", show_progress=True)
        if PERSIST:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
        else:
            index = VectorstoreIndexCreator().from_loaders([loader])
    return index

def main():
    st.title("💬 Chatbot - Conversation with AI")
    st.write("🚀 A streamlit chatbot powered by OpenAI LLM")

    prompt = st.text_input("Enter Prompt:")
    if st.button("Submit"):
        index = load_data()
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-3.5-turbo"),
            retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
        )
        chat_history = []
        result = chain({"question": prompt, "chat_history": chat_history})
        st.write("AI's Response:")
        st.write(result['answer'])

if __name__ == "__main__":
    main()

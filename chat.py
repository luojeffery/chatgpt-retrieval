import os
import sys

import openai
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings
import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True

# Check if a query is passed as a command-line argument
if len(sys.argv) > 1:
    query = sys.argv[1]
else:
    query = None

# Load training data
training_loader = DirectoryLoader("data/", show_progress=True)
training_documents = training_loader.load()

# Load test data
test_loader = CSVLoader(r"data/Attack/Data Manipulation (DM)/AS1.csv")
test_documents = test_loader.load()

# Ingest training data into the vectorstore
if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
else:
    vectorstore = Chroma.from_documents(training_documents, OpenAIEmbeddings(), persist_directory="persist")

# Assuming you have a way to load your test file content into a query variable
# For demonstration, let's use a placeholder query
query = "Detect if there are any anomalies with this GOOSE file. If there are, tell me if it is an attack or " \
        "error and what kind it is. "

# Perform the search
results = vectorstore.search(query, k=1)  # Set k to 1 to get only one result

# Assuming you want to print the most relevant document's text
if results:
    print(results[0]['text'])
else:
    print("No results found.")

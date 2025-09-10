import os
import asyncio
from dotenv import load_dotenv
from operator import itemgetter

from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Import from the correct location in langchain_rag_engine
from langchain_rag_engine.rag.intent_classifier import classify_intent, get_quick_reply, context_aware_intent_classifier

load_dotenv()

# --- 1. Initialize Core Components ---

# Initialize the LLM
llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=os.environ.get("GROQ_API_KEY"))

# Initialize the Embedding Model
# Using sentence-transformers, which is wrapped by HuggingFaceEmbeddings
embedding_function = HuggingFaceEmbeddings(
    model_name="NovaSearch/stella_en_400M_v5",
    model_kwargs={'trust_remote_code': True}
)

# Connect to the existing ChromaDB Vector Stores
acts_vectorstore = Chroma(
    persist_directory="./chroma_db",
    collection_name="legal_assistant",
    embedding_function=embedding_function
)

judgments_vectorstore = Chroma(
    persist_directory="./chroma_db",
    collection_name="judgments",
    embedding_function=embedding_function
)

# --- 2. Create Retrievers ---

acts_retriever = acts_vectorstore.as_retriever(search_kwargs={"k": 3})
judgments_retriever = judgments_vectorstore.as_retriever(search_kwargs={"k": 2})

# --- 3. Define Document Formatting ---

def format_docs(docs):
    """Helper function to format retrieved documents into a single string."""
    context = ""
    for doc in docs:
        # Check metadata for document type if available, otherwise just use content
        metadata = doc.metadata
        if metadata.get('type') == 'act':
            context += f"Relevant Act Section: {metadata.get('section_no', '')} - {metadata.get('heading', '')}\n{doc.page_content}\n\n"
        elif metadata.get('type') == 'judgment':
            context += f"Relevant Judgment: {metadata.get('case_title', '')} ({metadata.get('citation', '')})\n{doc.page_content}\n\n"
        else: # Fallback for documents without a type
            context += f"Relevant Document:\n{doc.page_content}\n\n"
    return context

# --- 4. Combine Retrievers and Build the RAG Chain ---

# Define a function to combine documents from both retrievers
def get_combined_documents(query: str):
    """Fetches documents from both retrievers and combines them."""
    acts_docs = acts_retriever.get_relevant_documents(query)
    judgments_docs = judgments_retriever.get_relevant_documents(query)
    # Simple combination, can be improved with ranking later
    return acts_docs + judgments_docs

# Define the prompt template
prompt_template = ChatPromptTemplate.from_template(
    """You are a helpful Indian Legal Assistant with the personality of Grok. You are witty, a bit sarcastic, and have a rebellious sense of humor. However, when it comes to Indian law, you are incredibly knowledgeable and precise.\n\nUse the following legal sections and judgments to answer the user's question. Cite your sources.\n\n**Legal Context:**\n{context}\n\n**User's Question:** {question}\n\n**Your Answer:**"""
)

# Construct the RAG chain using LangChain Expression Language (LCEL)
rag_chain = (
    {
        "context": RunnableLambda(get_combined_documents) | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

# --- 5. Create the Main Query Function ---

async def query_legal_assistant(question: str, conversation_history: list = None) -> dict:
    """The main function to be called by the API, now using LangChain with context-aware intent classification."""

    if conversation_history is None:
        conversation_history = []

    # Step 1: Context-aware intent classification
    intent = context_aware_intent_classifier(question, conversation_history)

    if intent != "legal_query":
        return {
            "answer": get_quick_reply(intent),
            "source": "intent_classifier"
        }

    # Step 2: Invoke the RAG chain
    try:
        # LangChain's invoke method is synchronous by default.
        # For async, we would use `ainvoke`.
        answer = await rag_chain.ainvoke(question)
        return {
            "answer": answer,
            "source": "vector_db_langchain"
        }
    except Exception as e:
        print(f"❌ Error in LangChain RAG chain: {e}")
        # Fallback mechanism can be implemented here if needed
        return {
            "answer": f"An error occurred while processing your request with the LangChain engine: {e}",
            "source": "error_langchain"
        }

# Example of how to run it (for testing purposes)
async def main():
    test_question = "What constitutes Section 498A of the Indian Penal Code?"
    result = await query_legal_assistant(test_question)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

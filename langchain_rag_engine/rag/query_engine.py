import os
import asyncio
from dotenv import load_dotenv
from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Import context-aware intent classifier
from .intent_classifier import context_aware_intent_classifier, get_quick_reply

load_dotenv()

# --- 1. Initialize Core Components ---

# Initialize the LLM to use OpenRouter with streaming enabled
llm = ChatOpenAI(
    model_name="deepseek/deepseek-chat-v3.1:free",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:3000", # Replace with your actual site URL
        "X-Title": "BharatLawAI", # Replace with your actual site name
    },
    streaming=True  # Enable streaming support
)

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
# Note: We create two versions - one with StrOutputParser for non-streaming
# and one without for streaming
rag_chain = (
    {
        "context": RunnableLambda(get_combined_documents) | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

# Streaming version without StrOutputParser to get raw token streaming
rag_chain_streaming = (
    {
        "context": RunnableLambda(get_combined_documents) | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
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

    # Step 2: Proceed with RAG for legal queries
    try:
        # Check if the current task is cancelled before starting
        if asyncio.current_task() and asyncio.current_task().cancelled():
            raise asyncio.CancelledError()

        # LangChain's invoke method is synchronous by default.
        # For async, we would use `ainvoke`.
        answer = await rag_chain.ainvoke(question)

        # Check again if cancelled after processing
        if asyncio.current_task() and asyncio.current_task().cancelled():
            raise asyncio.CancelledError()

        return {
            "answer": answer,
            "source": "vector_db_langchain"
        }
    except asyncio.CancelledError:
        print(f"[Agent] Query cancelled for question: {question[:50]}...")
        raise  # Re-raise to be handled by the caller
    except Exception as e:
        print(f"❌ Error in LangChain RAG chain: {e}")
        # Fallback mechanism can be implemented here if needed
        return {
            "answer": f"An error occurred while processing your request with the LangChain engine: {e}",
            "source": "error_langchain"
        }

async def stream_legal_assistant(question: str, conversation_history: list = None):
    """Streaming version that yields tokens as they are generated by the LLM."""
    if conversation_history is None:
        conversation_history = []

    # Step 1: Context-aware intent classification
    intent = context_aware_intent_classifier(question, conversation_history)

    if intent != "legal_query":
        # For non-legal queries, yield the quick reply as a single chunk
        yield {
            "type": "chunk",
            "content": get_quick_reply(intent),
            "source": "intent_classifier"
        }
        yield {
            "type": "complete",
            "source": "intent_classifier"
        }
        return

    # Step 2: Proceed with streaming RAG for legal queries
    try:
        # Check if the current task is cancelled before starting
        if asyncio.current_task() and asyncio.current_task().cancelled():
            raise asyncio.CancelledError()

        # Use LangChain's streaming capability with the streaming chain (no StrOutputParser)
        async for chunk in rag_chain_streaming.astream(question):
            # Check if cancelled during streaming
            if asyncio.current_task() and asyncio.current_task().cancelled():
                raise asyncio.CancelledError()

            # Extract content from AIMessageChunk
            if hasattr(chunk, 'content'):
                content = chunk.content
            else:
                content = str(chunk)

            # Only yield non-empty content
            if content.strip():
                yield {
                    "type": "chunk",
                    "content": content,
                    "source": "vector_db_langchain"
                }

        # Signal completion
        yield {
            "type": "complete",
            "source": "vector_db_langchain"
        }

    except asyncio.CancelledError:
        print(f"[Agent] Streaming query cancelled for question: {question[:50]}...")
        yield {
            "type": "cancelled",
            "message": "Request was cancelled by user"
        }
        raise  # Re-raise to be handled by the caller
    except Exception as e:
        print(f"❌ Error in streaming LangChain RAG chain: {e}")
        yield {
            "type": "error",
            "message": f"An error occurred while processing your request: {str(e)}"
        }

# Simple streaming test function
async def test_streaming():
    """Test streaming without RAG components"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    # Simple prompt without RAG
    simple_prompt = ChatPromptTemplate.from_template(
        "You are a helpful legal assistant. Answer this question: {question}"
    )

    # Create a simple chain for testing
    simple_chain = simple_prompt | llm

    test_question = "What is Section 498A of IPC?"

    print("Testing simple streaming...")
    try:
        async for chunk in simple_chain.astream({"question": test_question}):
            if hasattr(chunk, 'content'):
                content = chunk.content
            else:
                content = str(chunk)
            if content.strip():
                print(f"Chunk: '{content}'")
    except Exception as e:
        print(f"Streaming error: {e}")

# Example of how to run it (for testing purposes)
async def main():
    await test_streaming()

if __name__ == "__main__":
    asyncio.run(main())

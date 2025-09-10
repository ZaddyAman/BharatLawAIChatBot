# BharatLawAI: LangChain RAG Engine Documentation

This document provides a detailed, beginner-friendly explanation of the LangChain-powered RAG (Retrieval-Augmented Generation) engine. It's designed to help you understand the core concepts of the framework and how they are applied in our project.

---

## 1. What is LangChain and Why Are We Using It?

At its core, **LangChain** is a framework designed to simplify the development of applications that use Large Language Models (LLMs). Before, we wrote a lot of manual code to handle tasks like:

*   Connecting to our vector database (ChromaDB).
*   Searching for relevant documents.
*   Manually formatting the documents and our question into a long string (a "prompt").
*   Sending that prompt to the Groq LLM.

While this worked, it was very rigid. LangChain provides a standardized, modular way to do all of this.

**Key Benefits:**

*   **Modularity:** Each part of our engine (the LLM, the database, the prompt) is now a standardized "component." This makes it incredibly easy to swap components out. For example, we could switch from the Groq LLM to an OpenAI LLM with just one line of code change.
*   **Standardization:** It provides a common language and structure for building RAG pipelines, which is great for collaboration and industry recognition.
*   **Readability:** Using LangChain Expression Language (LCEL), we can define our entire RAG process as a clean, readable "chain" of components.

---

## 2. The Core Components of Our RAG Engine

Our new `query_engine.py` is built by plugging together several key LangChain components. Let's look at each one.

### a. The LLM (`ChatGroq`)

*   **What it is:** This is the language model itself—the "brain" that generates answers. LangChain has wrappers for many different LLM providers.
*   **How we use it:** We use the `ChatGroq` wrapper to connect to the Groq API.

    ```python
    # From: langchain_rag_engine/rag/query_engine.py

    from langchain_groq import ChatGroq

    llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=os.environ.get("GROQ_API_KEY"))
    ```

### b. The Embedding Model (`HuggingFaceEmbeddings`)

*   **What it is:** This is the tool that converts our text (like the user's question or a legal document) into a numerical format (a "vector") so we can perform semantic searches.
*   **How we use it:** We use the `HuggingFaceEmbeddings` wrapper to load our chosen `stella_en_400M_v5` model.

    ```python
    # From: langchain_rag_engine/rag/query_engine.py

    from langchain_huggingface import HuggingFaceEmbeddings

    embedding_function = HuggingFaceEmbeddings(
        model_name="NovaSearch/stella_en_400M_v5",
        model_kwargs={'trust_remote_code': True}
    )
    ```

### c. The Vector Store (`Chroma`)

*   **What it is:** This is our vector database. LangChain's `Chroma` component acts as a bridge, allowing the framework to communicate with our existing ChromaDB database.
*   **How we use it:** We initialize the `Chroma` component, telling it where our database is located (`./chroma_db`), which collection to use (`legal_assistant` or `judgments`), and which embedding function to use for searching.

    ```python
    # From: langchain_rag_engine/rag/query_engine.py

    from langchain_community.vectorstores import Chroma

    acts_vectorstore = Chroma(
        persist_directory="./chroma_db",
        collection_name="legal_assistant",
        embedding_function=embedding_function
    )
    ```

### d. The Retriever (`as_retriever`)

*   **What it is:** If the Vector Store is the database, the **Retriever** is the search engine. Its job is to take a user's question, find the most relevant documents from the Vector Store, and "retrieve" them.
*   **How we use it:** We create two retrievers, one for our `acts` collection and one for our `judgments` collection.

    ```python
    # From: langchain_rag_engine/rag/query_engine.py

    acts_retriever = acts_vectorstore.as_retriever(search_kwargs={"k": 3})
    judgments_retriever = judgments_vectorstore.as_retriever(search_kwargs={"k": 2})
    ```

---

## 3. Putting It All Together: The RAG Chain (LCEL)

This is the most powerful concept. **LangChain Expression Language (LCEL)** allows us to define the entire RAG workflow by "piping" (using the `|` symbol) our components together. It creates a clear, step-by-step flow of data.

Here is the data flow for our chain:

`User Question` -> `Retrieve Documents` -> `Format Documents` -> `Fill Prompt` -> `Send to LLM` -> `Get Final Answer`

And here is the code that implements this flow:

```python
# From: langchain_rag_engine/rag/query_engine.py

rag_chain = (
    {
        "context": RunnableLambda(get_combined_documents) | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt_template
    | llm
    | StrOutputParser()
)
```

Let's break down what each part of this "pipe" does:

1.  **The Input (`{ ... }`)**: This is the starting point. It prepares the necessary data for the prompt.
    *   `"question": RunnablePassthrough()`: This simply takes the user's initial question and passes it through unchanged.
    *   `"context": ...`: This part is responsible for creating the legal context. It first calls our custom `get_combined_documents` function to fetch documents from both retrievers, and then pipes (`|`) those documents to our `format_docs` function to turn them into a single string.

2.  **The Prompt (`| prompt_template`)**: The `context` and `question` from the previous step are automatically fed into our `ChatPromptTemplate`, which fills in the blanks to create the final, detailed prompt.

3.  **The LLM (`| llm`)**: The fully formatted prompt is then sent to our `ChatGroq` LLM for processing.

4.  **The Output (`| StrOutputParser()`)**: The LLM returns a complex object, but we only want the final text of the answer. The `StrOutputParser` automatically extracts this for us, giving us a clean string as the final result.

---

## 4. Summary

By refactoring to LangChain, we have replaced our manual, hard-coded RAG logic with a modular, standardized, and highly readable chain of components. This not only makes our current code cleaner but also makes it much easier to add new features or swap out components in the future, which is a huge advantage for the long-term health of the project.

# BharatLawAI Backend Documentation

This document provides a detailed overview of the backend architecture, components, and design decisions for the BharatLawAI project. It is intended for developers, technical interviewers, and anyone interested in understanding the inner workings of the application.

## 1. Overall Architecture

The backend is a modern, asynchronous web application built with **FastAPI**. It follows a modular, service-oriented architecture with a clear separation of concerns. The three main pillars of the backend are:

1.  **API Layer (FastAPI):** Handles all incoming HTTP requests, data validation, and user authentication.
2.  **RAG Pipeline (AI Core):** The brain of the application, responsible for understanding user queries and generating intelligent, context-aware responses.
3.  **Database Layer (SQLAlchemy & SQLite):** Manages data persistence for users, conversations, and chat history.

![Backend Architecture Diagram]()  <!-- You can create and link a diagram here -->

--- 

## 2. API Endpoints

The API is organized using FastAPI's `APIRouter` to keep the code modular and maintainable.

### 2.1. Main Application (`main.py`)

*   **Purpose:** The main entry point for the FastAPI application.
*   **Key Responsibilities:**
    *   Initializes the FastAPI app and the database (`init_db()`).
    *   Configures CORS middleware to allow requests from the frontend.
    *   Includes the API routers for `acts`, `auth`, and `chat`.
    *   Manages a dictionary of ongoing `asyncio.Task` objects for the "stop generation" feature.

### 2.2. Authentication (`/auth`)

*   **File:** `api/auth.py`
*   **Description:** Handles user registration and login using JWT-based authentication.
*   **Endpoints:**
    *   `POST /auth/register`: Creates a new user. Passwords are hashed using `passlib` before being stored.
    *   `POST /auth/token`: Authenticates a user with email and password, returning a JWT access token.
    *   `GET /auth/users/me`: Returns the details of the currently authenticated user, based on the provided JWT.

### 2.3. Chat (`/chat`)

*   **File:** `main.py`
*   **Description:** The core endpoint for handling user chat requests.
*   **Endpoints:**
    *   `POST /chat`: 
        *   Requires authentication.
        *   Accepts a user's question and an optional `conversation_id`.
        *   If no `conversation_id` is provided, a new conversation is created.
        *   Saves the user's message to the database.
        *   Creates an `asyncio.Task` to run the RAG pipeline (`query_legal_assistant`).
        *   Saves the assistant's response to the database.
        *   Returns the AI-generated answer, source, and `request_id`.
    *   `POST /cancel_chat`: 
        *   Accepts a `request_id`.
        *   Finds the corresponding task in the `_ongoing_tasks` dictionary and cancels it.

### 2.4. Legal Library (`/api/acts`)

*   **File:** `api/acts.py`
*   **Description:** Provides access to the legal library data.
*   **Endpoints:**
    *   `GET /api/acts`: 
        *   Returns a paginated and searchable list of all legal acts.
        *   Accepts `skip`, `limit`, and `search_query` parameters.
        *   Returns only summary data (title, ID, etc.) for fast loading.
    *   `GET /api/acts/{act_file_name}`: 
        *   Returns the full details (preamble, chapters, sections) of a single act.

### 2.5. Chat History (`/conversations`)

*   **File:** `main.py`
*   **Description:** Endpoints for retrieving a user's chat history.
*   **Endpoints:**
    *   `GET /conversations`: Returns a list of all conversations for the currently authenticated user.
    *   `GET /conversations/{conversation_id}/messages`: Returns all messages for a specific conversation.

--- 

## 3. RAG Pipeline

The RAG (Retrieval-Augmented Generation) pipeline is the core of the AI's functionality. It ensures that the AI's responses are grounded in the provided legal documents, reducing hallucinations and improving accuracy.

### 3.1. `rag/query_engine.py`

This is the main entry point for the RAG pipeline. The `query_legal_assistant` function follows these steps:

1.  **Intent Classification:** It first calls `classify_intent` to determine if the user's query is a simple greeting, chitchat, or a genuine legal question. If it's not a legal query, it returns a quick, canned response.
2.  **Vector Search:** If it's a legal query, the user's question is encoded into a vector embedding using a `sentence-transformers` model. This embedding is then used to search the **ChromaDB** vector database for the most semantically similar legal sections.
3.  **Prompt Engineering & RAG:**
    *   If relevant documents are found (with a similarity score above a certain threshold), they are injected into a detailed prompt along with the user's original question. This prompt instructs the LLM (from Groq) to answer the question *only* using the provided legal context and to adopt a specific persona.
    *   This step is crucial for ensuring the AI's answers are accurate and contextually relevant.
4.  **Fallback Mechanism:** If no relevant documents are found in the vector database, the system falls back to a different prompt that asks the LLM to answer the question based on its general knowledge, while also stating that it is not using verified documents.

### 3.2. `rag/intent_classifier.py`

*   **Purpose:** A simple but effective keyword-based classifier. It prioritizes legal keywords to ensure that genuine legal questions are not misclassified.

--- 

## 4. Database Layer

The database layer uses **SQLAlchemy** as its ORM (Object-Relational Mapper) and a **SQLite** database file for simplicity and ease of setup.

*   **`db/database.py`:** Configures the database connection and session management.
*   **`db/models.py`:** Defines the database tables as Python classes (`User`, `Conversation`, `Message`) using SQLAlchemy's declarative base.
*   **`db/schemas.py`:** Defines the Pydantic models for data validation and serialization. This ensures that data sent to and from the API conforms to a strict schema. The use of `ConfigDict(from_attributes=True)` allows Pydantic to read data directly from the SQLAlchemy ORM models.
*   **`db/crud.py`:** Contains all the functions for creating, reading, updating, and deleting data from the database (CRUD operations). This abstracts the database logic from the API endpoints.

--- 

## 5. Key Design Decisions

*   **FastAPI:** Chosen for its high performance, asynchronous support (which was essential for the "stop generation" feature), and automatic data validation with Pydantic.
*   **Vector Database (ChromaDB):** Used for efficient semantic search. This allows the application to find relevant legal sections based on the *meaning* of the user's query, not just keywords.
*   **RAG Architecture:** Implemented to ground the LLM's responses in factual legal documents, which is critical for a legal application to ensure accuracy and build user trust.
*   **In-Memory Caching (`api/acts.py`):** The legal acts data is loaded into an in-memory cache (`_all_acts_cache`) on the first request. This significantly speeds up subsequent requests for the legal library, as it avoids repeated file I/O.
*   **JWT for Authentication:** A standard and secure method for stateless authentication, which is well-suited for modern web applications.
*   **Modular Structure:** The code is organized into logical modules (`api`, `db`, `rag`), making it easier to understand, maintain, and scale.

# BharatLaw AI - System Architecture

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[React Frontend]
        B[Vite Dev Server]
        C[Browser Client]
    end

    subgraph "API Gateway Layer"
        D[FastAPI Application]
        E[CORS Middleware]
        F[JWT Authentication]
        G[Rate Limiting]
    end

    subgraph "Business Logic Layer"
        H[RAG Engine]
        I[Auth Service]
        J[Streaming Service]
        K[Legal Analysis Engine]
    end

    subgraph "Data Layer"
        L[(PostgreSQL)]
        M[(Pinecone Vector DB)]
        N[Voyage AI Embeddings]
        O[OpenRouter LLM]
    end

    subgraph "Infrastructure Layer"
        P[Docker Containers]
        Q[Railway Platform]
        R[Background Tasks]
        S[Monitoring & Logging]
    end

    A --> D
    B --> D
    C --> D

    D --> E
    D --> F
    D --> G

    D --> H
    D --> I
    D --> J
    D --> K

    H --> L
    H --> M
    H --> N
    H --> O

    I --> L
    J --> L
    K --> L

    D --> P
    P --> Q
    D --> R
    D --> S
```

## 🔧 Component Architecture

### Backend Components

```mermaid
graph TD
    subgraph "Main Application"
        A[main.py]
        B[config.py]
        C[dependency_container.py]
    end

    subgraph "API Layer"
        D[auth.py]
        E[acts.py]
        F[feedback.py]
    end

    subgraph "Business Logic"
        G[advanced_rag.py]
        H[hybrid_search.py]
        I[intent_classifier.py]
        J[cot_reasoning.py]
    end

    subgraph "Data Access"
        K[database.py]
        L[models.py]
        M[crud.py]
    end

    subgraph "Services"
        N[scalable_registry.py]
        O[metadata_filter.py]
        P[prompt_chains.py]
    end

    A --> B
    A --> C
    A --> D
    A --> E
    A --> F

    D --> G
    E --> G
    F --> G

    G --> H
    G --> I
    G --> J

    G --> K
    H --> K
    I --> K
    J --> K

    K --> L
    K --> M

    G --> N
    H --> O
    I --> P
```

### Frontend Components

```mermaid
graph TD
    subgraph "Application Shell"
        A[App.tsx]
        B[main.tsx]
        C[index.html]
    end

    subgraph "Routing"
        D[AppRoutes.tsx]
        E[ProtectedRoute.tsx]
        F[AdminProtectedRoute.tsx]
    end

    subgraph "Pages"
        G[LandingPage.tsx]
        H[ChatPage.tsx]
        I[LegalLibraryPage.tsx]
        J[ProfilePage.tsx]
    end

    subgraph "Components"
        K[ErrorBoundary.tsx]
        L[AsyncWrapper.tsx]
        M[LoadingFallback.tsx]
        N[OfflineIndicator.tsx]
    end

    subgraph "Context & Hooks"
        O[AuthContext.tsx]
        P[useErrorHandler.ts]
        Q[useAsyncWrapper.ts]
    end

    subgraph "Utilities"
        R[auth.ts]
        S[chat.ts]
        T[conversations.ts]
        U[secureStorage.ts]
    end

    A --> B
    B --> C

    A --> D
    D --> E
    D --> F

    D --> G
    D --> H
    D --> I
    D --> J

    A --> K
    A --> L
    A --> M
    A --> N

    A --> O
    K --> P
    L --> Q

    R --> O
    S --> O
    T --> O
    U --> O
```

## 📊 Data Flow Architecture

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database
    participant J as JWT

    U->>F: Login Request
    F->>B: POST /auth/token
    B->>D: Verify Credentials
    D-->>B: User Data
    B->>J: Generate Token
    J-->>B: JWT Token
    B-->>F: Token Response
    F->>F: Store Token (Secure)
    F-->>U: Login Success
```

### RAG Query Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant R as RAG Engine
    participant P as Pinecone
    participant V as Voyage AI
    participant O as OpenRouter

    U->>F: Legal Question
    F->>B: POST /chat/start
    B->>R: Process Query
    R->>V: Generate Embeddings
    V-->>R: Query Embeddings
    R->>P: Vector Search
    P-->>R: Relevant Documents
    R->>O: Generate Response
    O-->>R: Streaming Response
    R-->>B: Stream Chunks
    B-->>F: Server-Sent Events
    F-->>U: Real-time Response
```

### Streaming Architecture

```mermaid
graph TD
    subgraph "Client"
        A[React Component]
        B[EventSource]
        C[Streaming UI]
    end

    subgraph "Server"
        D[FastAPI Endpoint]
        E[Streaming Generator]
        F[Background Task]
        G[Database Session]
    end

    subgraph "External Services"
        H[LLM API]
        I[Vector Database]
        J[Embedding Service]
    end

    A --> B
    B --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J

    H --> E
    I --> E
    J --> E
    E --> B
    B --> C
```

## 🔄 State Management Architecture

### Backend State Management

```mermaid
graph TD
    subgraph "Application State"
        A[Configuration]
        B[Service Container]
        C[Database Sessions]
    end

    subgraph "Request State"
        D[Streaming Sessions]
        E[Task Registry]
        F[User Context]
    end

    subgraph "Business State"
        G[RAG Engine State]
        H[Search Cache]
        I[Reasoning Context]
    end

    subgraph "Infrastructure State"
        J[Connection Pools]
        K[Background Tasks]
        L[Cleanup Jobs]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

### Frontend State Management

```mermaid
graph TD
    subgraph "Global State"
        A[AuthContext]
        B[User Preferences]
        C[Application Settings]
    end

    subgraph "Component State"
        D[Loading States]
        E[Error States]
        F[Form Data]
    end

    subgraph "Server State"
        G[API Responses]
        H[Streaming Data]
        I[Cached Data]
    end

    subgraph "UI State"
        J[Modal States]
        K[Navigation State]
        L[Theme Settings]
    end

    A --> D
    A --> E
    A --> F
    B --> D
    B --> E
    B --> F
    C --> D
    C --> E
    C --> F

    G --> D
    G --> E
    G --> F
    H --> D
    H --> E
    H --> F
    I --> D
    I --> E
    I --> F

    J --> D
    J --> E
    J --> F
    K --> D
    K --> E
    K --> F
    L --> D
    L --> E
    L --> F
```

## 🗄️ Database Schema

```mermaid
erDiagram
    User ||--o{ Conversation : owns
    Conversation ||--o{ Message : contains
    Message ||--o{ Feedback : receives
    User ||--o{ Feedback : provides

    User {
        integer id PK
        string email UK
        string hashed_password
        string full_name
        string avatar_url
        string bio
        string phone_number
        boolean is_active
        boolean email_verified
        datetime last_login
        datetime created_at
        datetime updated_at
        string oauth_provider
        string oauth_id
    }

    Conversation {
        integer id PK
        string title
        integer owner_id FK
        datetime created_at
        datetime updated_at
    }

    Message {
        integer id PK
        integer conversation_id FK
        string type
        text content
        string source
        datetime timestamp
    }

    Feedback {
        integer id PK
        integer message_id FK
        integer user_id FK
        string rating
        text comment
        datetime created_at
    }

    StreamSession {
        integer id PK
        string request_id UK
        integer user_id FK
        string question
        integer conversation_id FK
        string status
        datetime created_at
        datetime updated_at
    }

    TaskRegistry {
        integer id PK
        string task_id UK
        string request_id
        string task_type
        string status
        json metadata
        datetime created_at
        datetime updated_at
    }
```

## 🔐 Security Architecture

### Authentication Flow

```mermaid
graph TD
    subgraph "Client Security"
        A[JWT Storage]
        B[Secure Cookies]
        C[Token Refresh]
        D[CORS Headers]
    end

    subgraph "API Security"
        E[JWT Validation]
        F[Rate Limiting]
        G[Input Validation]
        H[SQL Injection Prevention]
    end

    subgraph "Data Security"
        I[Password Hashing]
        J[Data Encryption]
        K[Access Control]
        L[Audit Logging]
    end

    A --> E
    B --> E
    C --> E
    D --> F

    E --> G
    F --> H
    G --> I
    H --> J
    I --> K
    J --> L
```

## 📈 Performance Architecture

### Caching Strategy

```mermaid
graph TD
    subgraph "Application Cache"
        A[Configuration Cache]
        B[User Session Cache]
        C[Search Results Cache]
    end

    subgraph "Database Cache"
        D[Connection Pool]
        E[Query Result Cache]
        F[Prepared Statements]
    end

    subgraph "External Cache"
        G[Redis Sessions]
        H[CDN Assets]
        I[API Response Cache]
    end

    A --> D
    B --> D
    C --> D

    D --> G
    E --> G
    F --> G

    G --> H
    G --> I
```

### Monitoring Architecture

```mermaid
graph TD
    subgraph "Application Metrics"
        A[Response Times]
        B[Error Rates]
        C[Throughput]
        D[Resource Usage]
    end

    subgraph "Business Metrics"
        E[User Engagement]
        F[Search Performance]
        G[Conversion Rates]
        H[Feature Usage]
    end

    subgraph "Infrastructure Metrics"
        I[CPU Usage]
        J[Memory Usage]
        K[Disk I/O]
        L[Network I/O]
    end

    subgraph "External Monitoring"
        M[Health Checks]
        N[Log Aggregation]
        O[Alert System]
        P[Dashboard]
    end

    A --> M
    B --> M
    C --> M
    D --> M

    E --> N
    F --> N
    G --> N
    H --> N

    I --> O
    J --> O
    K --> O
    L --> O

    M --> P
    N --> P
    O --> P
```

## 🚀 Deployment Architecture

### Railway Deployment

```mermaid
graph TD
    subgraph "Railway Platform"
        A[Railway App]
        B[PostgreSQL Database]
        C[Redis Cache]
        D[File Storage]
    end

    subgraph "Application Containers"
        E[Backend Container]
        F[Worker Container]
        G[Migration Container]
    end

    subgraph "External Services"
        H[Pinecone]
        I[Voyage AI]
        J[OpenRouter]
        K[SMTP Service]
    end

    A --> B
    A --> C
    A --> D

    A --> E
    A --> F
    A --> G

    E --> H
    E --> I
    E --> J
    E --> K

    F --> H
    F --> I
    F --> J

    G --> B
```

### Vercel Deployment (Frontend)

```mermaid
graph TD
    subgraph "Vercel Platform"
        A[Vercel App]
        B[Edge Network]
        C[CDN]
        D[Analytics]
    end

    subgraph "Build Process"
        E[Vite Build]
        F[TypeScript Compilation]
        G[Asset Optimization]
        H[Code Splitting]
    end

    subgraph "Runtime"
        I[React Application]
        J[Service Worker]
        K[Error Boundaries]
        L[Performance Monitoring]
    end

    A --> B
    A --> C
    A --> D

    A --> E
    E --> F
    F --> G
    G --> H

    H --> I
    I --> J
    I --> K
    I --> L
```

## 🔧 Development Workflow

### Local Development

```mermaid
graph TD
    subgraph "Development Environment"
        A[VS Code]
        B[Git]
        C[Docker Desktop]
        D[PostgreSQL Local]
    end

    subgraph "Development Tools"
        E[Hot Reload]
        F[TypeScript Compiler]
        G[ESLint]
        H[Jest]
    end

    subgraph "Testing"
        I[Unit Tests]
        J[Integration Tests]
        K[E2E Tests]
        L[Load Tests]
    end

    A --> E
    A --> F
    A --> G
    A --> H

    E --> I
    F --> I
    G --> I
    H --> I

    I --> J
    J --> K
    K --> L
```

### CI/CD Pipeline

```mermaid
graph TD
    subgraph "Source Control"
        A[GitHub Repository]
        B[Pull Request]
        C[Code Review]
    end

    subgraph "CI Pipeline"
        D[Code Quality]
        E[Security Scan]
        F[Unit Tests]
        G[Integration Tests]
    end

    subgraph "CD Pipeline"
        H[Build Artifacts]
        I[Docker Images]
        J[Deploy to Staging]
        K[Deploy to Production]
    end

    subgraph "Monitoring"
        L[Health Checks]
        M[Performance Tests]
        N[Rollback Plan]
        O[Incident Response]
    end

    A --> B
    B --> C
    C --> D

    D --> E
    E --> F
    F --> G

    G --> H
    H --> I
    I --> J
    J --> K

    K --> L
    L --> M
    M --> N
    N --> O
```

This architecture documentation provides a comprehensive view of the BharatLaw AI system's design, components, data flows, and deployment patterns. The modular architecture ensures scalability, maintainability, and robust performance for legal document analysis and AI-powered assistance.
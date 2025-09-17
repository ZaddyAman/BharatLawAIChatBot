# BharatLaw AI - Full-Stack Legal Assistant

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5+-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)](https://fastapi.tiangolo.com/)

A sophisticated AI-powered legal assistant for Indian law with advanced RAG (Retrieval-Augmented Generation) capabilities, real-time streaming responses, and comprehensive legal document search.

## 🌟 Features

### 🤖 Advanced AI Capabilities
- **Chain-of-Thought Reasoning**: 8-step legal analysis process
- **Hybrid Search**: Semantic + keyword + metadata filtering
- **Real-time Streaming**: Live response generation
- **Legal Document Search**: Comprehensive Indian law database
- **Multi-modal Reasoning**: Legal precedent analysis and cross-referencing

### 🔒 Security & Authentication
- **JWT Authentication**: Secure token-based authentication
- **OAuth Integration**: Google and GitHub login support
- **Role-based Access Control**: Admin and user permissions
- **Encrypted Storage**: Secure client-side token storage
- **CORS Protection**: Configurable origin restrictions

### ⚡ Performance & Scalability
- **Database-backed Registry**: Replaces in-memory storage for horizontal scaling
- **Connection Pooling**: Optimized database connections
- **Lazy Loading**: Components and embeddings loaded on demand
- **Background Cleanup**: Automatic session and task cleanup
- **Streaming Optimization**: Efficient real-time communication

### 🛠️ Developer Experience
- **Type Safety**: Full TypeScript and Python typing
- **Error Boundaries**: Comprehensive error handling
- **Hot Reload**: Development with live updates
- **API Documentation**: Auto-generated FastAPI docs
- **Environment Validation**: Configuration validation at startup

## 🏗️ Architecture

### Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BharatLaw AI Backend                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   FastAPI       │  │   PostgreSQL    │  │  Pinecone   │ │
│  │   Application   │  │   Database      │  │  Vector DB  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Auth Service   │  │  RAG Engine     │  │ Voyage AI   │ │
│  │  (JWT/OAuth)    │  │  (Hybrid Search) │  │ Embeddings │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Scalable        │  │ Dependency      │  │ Background  │ │
│  │ Registry        │  │ Container       │  │ Tasks       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   BharatLaw AI Frontend                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   React 18      │  │   TypeScript    │  │  Tailwind   │ │
│  │   Application   │  │   Components    │  │    CSS      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Auth Context    │  │ Error Boundary  │  │ Async       │ │
│  │ (JWT Storage)   │  │ (Error UI)      │  │ Wrapper     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Route Guards    │  │ Lazy Loading    │  │ Secure      │ │
│  │ (Protection)    │  │ (Code Split)    │  │ Storage     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (or Railway database)
- **Pinecone Account** (for vector search)
- **Voyage AI Account** (for embeddings)
- **OpenRouter Account** (for LLM access)

### Backend Setup

1. **Clone and navigate to backend:**
   ```bash
   cd langchain_rag_engine
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   python -c "from db.database import init_db; init_db()"
   ```

6. **Start the backend:**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd bharatlaw-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the frontend:**
   ```bash
   npm run dev
   ```

## 📋 Environment Configuration

### Backend (.env)

```env
# Security
SECRET_KEY=your-super-secure-secret-key-here
ADMIN_EMAILS=admin@example.com,admin2@example.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bharatlaw

# API Configuration
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
MAX_CONCURRENT_STREAMS=3

# External Services
OPENROUTER_API_KEY=your-openrouter-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=bharatlaw-index
VOYAGE_API_KEY=your-voyage-key

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Security
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend (.env)

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Admin Configuration
VITE_ADMIN_EMAILS=admin@example.com
```

## 🔧 API Documentation

Once the backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Backend Testing
```bash
cd langchain_rag_engine
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd bharatlaw-frontend
npm test
```

## 🚀 Deployment

### Railway (Recommended)

1. **Connect Repository:**
   - Link your GitHub repository to Railway
   - Railway will auto-detect Python application

2. **Environment Variables:**
   - Set all environment variables in Railway dashboard
   - Use Railway's PostgreSQL database

3. **Build Configuration:**
   - Railway automatically handles Python dependencies
   - Custom build command: `pip install -r requirements.txt`

### Vercel (Frontend)

1. **Connect Repository:**
   - Link GitHub repository to Vercel
   - Set build command: `npm run build`
   - Set output directory: `dist`

2. **Environment Variables:**
   - Set `VITE_API_URL` to your Railway backend URL

## 📊 Monitoring & Analytics

### Backend Monitoring
- **Health Endpoint**: `/health` - System status and metrics
- **Configuration Summary**: Automatic validation on startup
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Database query monitoring

### Frontend Monitoring
- **Error Boundaries**: Automatic error capture and reporting
- **Analytics Integration**: Google Analytics support
- **Performance Monitoring**: Component load times
- **User Behavior Tracking**: Page views and interactions

## 🔧 Development

### Code Quality
- **Linting**: ESLint for frontend, flake8 for backend
- **Type Checking**: TypeScript strict mode
- **Testing**: Jest for frontend, pytest for backend
- **Pre-commit Hooks**: Automated code quality checks

### Architecture Patterns
- **Dependency Injection**: Clean architecture with service container
- **Repository Pattern**: Data access abstraction
- **Observer Pattern**: Event-driven communication
- **Strategy Pattern**: Pluggable search and reasoning strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Pinecone** - Vector database
- **Voyage AI** - Legal document embeddings
- **OpenRouter** - LLM API access
- **Railway** - Cloud deployment platform

## 📞 Support

For support and questions:
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@bharatlaw.ai

---

**⚖️ Legal Notice**: This application is for educational and informational purposes only. It does not constitute legal advice, and users should consult qualified legal professionals for their specific legal needs.
# Sentellent AI – Personalized Equity Analyst

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-16.2.12-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![AWS](https://img.shields.io/badge/AWS-ECS%2FFargate-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An AI-powered equity analysis platform that provides personalized investment insights using Retrieval-Augmented Generation (RAG). The platform ingests company fundamentals, news articles, and financial documents to deliver context-aware investment recommendations through an intelligent chat interface.

## Features

- 🤖 **AI-Powered Equity Analysis** - Context-aware AI agent using Google Gemini for intelligent investment insights
- 📊 **Real-Time Market Data** - Integration with Finnhub and Alpha Vantage for live stock prices and financial data
- 🔍 **Semantic Search** - RAG pipeline with Qdrant vector database for intelligent document retrieval
- 📰 **News Ingestion & Analysis** - Automated news fetching with sentiment analysis and event categorization
- 💼 **Portfolio Management** - Track holdings, monitor performance, and manage multiple portfolios
- ⭐ **Watchlists** - Create and manage custom watchlists for tracking favorite stocks
- 👤 **Investor Profiles** - Personalized recommendations based on risk tolerance and investment preferences
- 🔐 **Google OAuth Authentication** - Secure authentication with Google OAuth
- 📈 **Historical Price Charts** - Interactive charts for technical analysis
- 🌐 **Responsive UI** - Modern Next.js frontend with Tailwind CSS

## Architecture

The application follows a modern microservices architecture with clear separation between frontend and backend:

```
┌─────────────────┐         ┌─────────────────┐
│   Next.js App   │────────▶│   FastAPI       │
│   (Port 3000)   │         │   (Port 8000)   │
└─────────────────┘         └─────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │PostgreSQL│   │ Qdrant   │   │External  │
              │   RDS    │   │ Vector DB│   │ APIs     │
              └──────────┘   └──────────┘   └──────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.141.1
- **Language**: Python 3.13
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0.51
- **Vector Database**: Qdrant
- **AI/ML**: 
  - Google Gemini (langchain-google-genai)
  - LangChain 1.3.14
  - LangGraph 1.2.10
  - sentence-transformers 5.6.1 (all-MiniLM-L6-v2)
- **Authentication**: JWT + Google OAuth
- **Data Providers**: Finnhub, Alpha Vantage, yFinance
- **Testing**: Pytest

### Frontend
- **Framework**: Next.js 16.2.12 (App Router)
- **Language**: TypeScript 5
- **UI Library**: React 19.2.4
- **Styling**: Tailwind CSS 4
- **Authentication**: NextAuth 5.0.0-beta.32
- **Charts**: Recharts 3.10.1
- **Icons**: Lucide React

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Cloud Provider**: AWS (ap-south-1)
- **Compute**: ECS Fargate
- **Load Balancer**: Application Load Balancer
- **Database**: Amazon RDS PostgreSQL
- **Container Registry**: Amazon ECR
- **Monitoring**: CloudWatch Logs
- **IaC**: Terraform 1.5.0+

## Folder Structure

```
sentellent-ai-equity-analyst/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI agents (equity_analyst, context_builder, memory_extractor)
│   │   ├── api/
│   │   │   ├── routes/          # API route handlers
│   │   │   └── v1/              # API v1 endpoints (auth, chat, companies, etc.)
│   │   ├── core/                # Core functionality (config, security, logging)
│   │   ├── db/                  # Database configuration
│   │   ├── ingestion/           # Data ingestion services (news, fundamentals, PDF)
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── providers/           # External API providers (Finnhub, Gemini, etc.)
│   │   ├── rag/                 # RAG pipeline (embeddings, retrieval, Qdrant)
│   │   ├── repositories/        # Data access layer
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic services
│   │   └── utils/               # Utility functions
│   ├── tests/                   # Backend tests
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile               # Backend Docker image
│   ├── requirements.txt         # Python dependencies
│   └── main.py                  # FastAPI application entry point
├── frontend/
│   ├── app/
│   │   ├── (app)/               # Main application routes
│   │   ├── (auth)/              # Authentication routes
│   │   ├── api/                 # Next.js API routes
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/               # TypeScript type definitions
│   │   └── utils/               # Frontend utilities
│   ├── public/                  # Static assets
│   ├── Dockerfile              # Frontend Docker image
│   ├── package.json             # Node dependencies
│   └── auth.ts                  # NextAuth configuration
├── terraform/
│   ├── alb.tf                   # Application Load Balancer
│   ├── ecr.tf                   # Elastic Container Registry
│   ├── ecs.tf                   # ECS Fargate configuration
│   ├── iam.tf                   # IAM roles and policies
│   ├── rds.tf                   # RDS PostgreSQL
│   ├── security_groups.tf       # Security groups
│   ├── vpc.tf                   # VPC and networking
│   ├── variables.tf             # Terraform variables
│   └── provider.tf              # AWS provider configuration
├── docker-compose.yml           # Local development compose file
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Screenshots

*[Screenshots will be added here - showing dashboard, chat interface, portfolio management, etc.]*

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        User[User Browser]
    end
    
    subgraph "Load Balancer"
        ALB[Application Load Balancer]
    end
    
    subgraph "ECS Fargate"
        Frontend[Next.js Frontend<br/>Port 3000]
        Backend[FastAPI Backend<br/>Port 8000]
    end
    
    subgraph "Data Layer"
        RDS[(Amazon RDS<br/>PostgreSQL 15)]
        Qdrant[(Qdrant<br/>Vector Database)]
    end
    
    subgraph "External Services"
        Gemini[Google Gemini AI]
        Finnhub[Finnhub API]
        AlphaVantage[Alpha Vantage API]
        GoogleAuth[Google OAuth]
    end
    
    User --> ALB
    ALB --> Frontend
    ALB --> Backend
    Backend --> RDS
    Backend --> Qdrant
    Backend --> Gemini
    Backend --> Finnhub
    Backend --> AlphaVantage
    Frontend --> GoogleAuth
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+ (for local development)
- Qdrant instance (local or cloud)
- Google OAuth credentials
- API keys: Finnhub, Alpha Vantage, Google Gemini

### Local Development

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd sentellent-ai-equity-analyst
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Configure environment variables (see Environment Variables section)
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Configure environment variables
# Edit .env with your configuration

# Start the development server
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Compose

#### 1. Configure Environment Variables

Create `.env` files in both backend and frontend directories:

```bash
# Backend .env
DATABASE_URL=postgresql+psycopg2://postgres:Postgres123@postgres:5432/sentellent
GEMINI_API_KEY=your_gemini_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
QDRANT_URL=http://host.docker.internal:6333
QDRANT_API_KEY=your_qdrant_api_key
SECRET_KEY=your_secret_key
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
```

```bash
# Frontend .env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

### Environment Variables

#### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `FINNHUB_API_KEY` | Finnhub API key | Yes | - |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Yes | - |
| `QDRANT_URL` | Qdrant vector database URL | Yes | - |
| `QDRANT_API_KEY` | Qdrant API key | Yes | - |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID | Yes | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | No | 30 |
| `LOG_LEVEL` | Logging level | No | INFO |

#### Frontend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes | - |
| `NEXTAUTH_SECRET` | NextAuth secret | Yes | - |
| `NEXTAUTH_URL` | NextAuth URL | Yes | - |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | - |

## AWS Deployment

### Infrastructure Overview

The application is deployed on AWS using the following services:

- **ECS Fargate**: Serverless container orchestration for frontend and backend
- **Application Load Balancer**: Traffic distribution and routing
- **RDS PostgreSQL 15**: Managed PostgreSQL database
- **ECR**: Docker image registry
- **CloudWatch**: Logging and monitoring
- **VPC**: Isolated network with public subnets

### Deployment Architecture

```mermaid
graph TB
    Internet[Internet]
    
    subgraph "AWS Region: ap-south-1"
        ALB[Application Load Balancer]
        
        subgraph "ECS Cluster"
            FrontendTG[Frontend Target Group]
            BackendTG[Backend Target Group]
            FrontendTask[Frontend Task<br/>Next.js]
            BackendTask[Backend Task<br/>FastAPI]
        end
        
        subgraph "RDS"
            PostgreSQL[(PostgreSQL 15<br/>db.t3.micro)]
        end
        
        subgraph "ECR"
            FrontendECR[Frontend Repository]
            BackendECR[Backend Repository]
        end
        
        subgraph "CloudWatch"
            Logs[Log Groups]
        end
    end
    
    Internet --> ALB
    ALB --> FrontendTG
    ALB --> BackendTG
    FrontendTG --> FrontendTask
    BackendTG --> BackendTask
    BackendTask --> PostgreSQL
    FrontendTask --> BackendTask
    FrontendTask --> FrontendECR
    BackendTask --> BackendECR
    FrontendTask --> Logs
    BackendTask --> Logs
```

### Terraform Infrastructure

#### Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform 1.5.0+
- Existing AWS account with IAM permissions

#### Deployment Steps

1. **Configure Terraform Variables**

Create a `terraform.tfvars` file:

```hcl
aws_region           = "ap-south-1"
project_name         = "sentellent-ai"

# Database credentials
db_username          = "your_db_username"
db_password          = "your_db_password"
db_name              = "sentellent"

# Authentication
jwt_secret           = "your_jwt_secret"
google_client_id     = "your_google_client_id"
google_client_secret = "your_google_client_secret"
nextauth_secret      = "your_nextauth_secret"

# API Keys
gemini_api_key       = "your_gemini_api_key"
finnhub_api_key      = "your_finnhub_api_key"
alpha_vantage_api_key = "your_alpha_vantage_api_key"
qdrant_url           = "your_qdrant_url"
qdrant_api_key       = "your_qdrant_api_key"
```

2. **Initialize Terraform**

```bash
cd terraform
terraform init
```

3. **Plan Infrastructure**

```bash
terraform plan -out=tfplan
```

4. **Apply Infrastructure**

```bash
terraform apply tfplan
```

5. **Retrieve Outputs**

```bash
terraform output
```

Save the outputs for ECR repository URLs and ALB DNS name.

### Docker Build and Push to ECR

#### Backend

```bash
cd backend

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <backend-ecr-url>

# Build image
docker build -t sentellent-ai-backend .

# Tag image
docker tag sentellent-ai-backend:latest <backend-ecr-url>:latest

# Push to ECR
docker push <backend-ecr-url>:latest
```

#### Frontend

```bash
cd frontend

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <frontend-ecr-url>

# Build image
docker build --build-arg NEXT_PUBLIC_API_URL=http://<alb-dns-name> -t sentellent-ai-frontend .

# Tag image
docker tag sentellent-ai-frontend:latest <frontend-ecr-url>:latest

# Push to ECR
docker push <frontend-ecr-url>:latest
```

### ECS Deployment

After pushing images to ECR, update the ECS services:

```bash
# Update backend service
aws ecs update-service --cluster sentellent-ai-cluster --service sentellent-ai-backend-service --force-new-deployment --region ap-south-1

# Update frontend service
aws ecs update-service --cluster sentellent-ai-cluster --service sentellent-ai-frontend-service --force-new-deployment --region ap-south-1
```

### Terraform Resources

| Resource Type | Count | Description |
|---------------|-------|-------------|
| VPC | 1 | 10.0.0.0/16 CIDR |
| Public Subnets | 2 | Across 2 AZs |
| Internet Gateway | 1 | Public internet access |
| ECS Cluster | 1 | Fargate-enabled |
| ECS Task Definitions | 2 | Frontend & Backend |
| ECS Services | 2 | Frontend & Backend |
| Application Load Balancer | 1 | HTTP traffic routing |
| Target Groups | 2 | Frontend & Backend |
| RDS Instance | 1 | PostgreSQL 15, db.t3.micro |
| ECR Repositories | 2 | Frontend & Backend |
| Security Groups | 3 | ALB, ECS, RDS |
| CloudWatch Log Groups | 1 | ECS logs |

## CI/CD Pipeline

**Note: GitHub Actions workflows are not currently implemented.** The following describes the recommended CI/CD setup:

### Recommended GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml (not implemented)
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Build backend Docker image
      - Build frontend Docker image
      - Push to ECR
      - Update ECS services
```

### Manual Deployment Process

Currently, deployment is a manual process:

1. Build Docker images locally
2. Push to Amazon ECR
3. Update ECS services via AWS CLI or Console
4. Monitor deployment in CloudWatch

## API Overview

### Base URL
- Local: `http://localhost:8000`
- Production: `http://<alb-dns-name>`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with email/password |
| POST | `/api/v1/auth/google` | Login with Google OAuth |

### Company Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies` | List all companies |
| GET | `/api/v1/companies/search` | Search companies |
| GET | `/api/v1/companies/recommendations` | Get personalized recommendations |
| GET | `/api/v1/companies/recently-viewed` | Get recently viewed companies |
| POST | `/api/v1/companies/{symbol}/viewed` | Track company view |
| GET | `/api/v1/companies/{symbol}/profile` | Get company profile |
| GET | `/api/v1/companies/{symbol}/quote` | Get latest quote |
| GET | `/api/v1/companies/{symbol}/financials` | Get financial statements |
| GET | `/api/v1/companies/{symbol}/news` | Get company news |
| GET | `/api/v1/companies/{symbol}/history` | Get historical prices |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat/` | Ask AI equity analyst question |

### Portfolio Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/portfolios` | List user portfolios |
| POST | `/api/v1/portfolios` | Create portfolio |
| GET | `/api/v1/portfolios/{id}` | Get portfolio details |
| PUT | `/api/v1/portfolios/{id}` | Update portfolio |
| DELETE | `/api/v1/portfolios/{id}` | Delete portfolio |

### Watchlist Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/watchlists` | List user watchlists |
| POST | `/api/v1/watchlists` | Create watchlist |
| GET | `/api/v1/watchlists/{id}` | Get watchlist details |
| POST | `/api/v1/watchlists/{id}/companies` | Add company to watchlist |
| DELETE | `/api/v1/watchlists/{id}/companies/{company_id}` | Remove company |

### Investor Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/investor-profile` | Get investor profile |
| PUT | `/api/v1/investor-profile` | Update investor profile |

### Ingestion Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingestion/news` | Ingest company news |
| POST | `/api/v1/ingestion/fundamentals` | Ingest company fundamentals |
| POST | `/api/v1/ingestion/pdf` | Ingest PDF documents |

## AI Features

### Equity Analyst Agent

The AI agent uses a context-aware approach to provide investment insights:

- **Context Building**: Gathers user's portfolio, watchlist, and investor profile
- **Memory Extraction**: Extracts relevant information from conversation history
- **RAG Retrieval**: Fetches relevant documents from Qdrant vector database
- **Live Data Integration**: Incorporates real-time market data
- **Document Type Awareness**: Adapts responses based on retrieved document types (news, fundamentals, annual reports)

### Supported Document Types

- **News Articles**: Latest company news with sentiment analysis
- **Fundamentals**: Financial ratios, metrics, and business summaries
- **Annual Reports**: PDF documents from annual reports
- **Live Data**: Real-time market prices and indicators

### AI Model

- **Primary**: Google Gemini (via langchain-google-genai)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: Qdrant with cosine similarity

## RAG Pipeline

### Document Ingestion

1. **News Ingestion**
   - Fetches news from Finnhub API
   - Analyzes sentiment and event type using AI
   - Splits articles into chunks
   - Stores in Qdrant with metadata

2. **Fundamentals Ingestion**
   - Fetches fundamentals from yFinance
   - Converts structured data to natural language
   - Splits into chunks
   - Stores in Qdrant with metadata

3. **PDF Ingestion**
   - Uploads PDF documents
   - Extracts text using PyPDF
   - Splits into chunks
   - Stores in Qdrant with metadata

### Retrieval Process

1. User submits a question
2. Question is embedded using sentence-transformers
3. Semantic search in Qdrant with company filter
4. Top-k relevant chunks retrieved (score threshold: 0.35)
5. Context built from retrieved chunks
6. AI generates response using context and live data

### Vector Database Configuration

- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Distance Metric**: Cosine similarity
- **Indexed Fields**: company, source
- **Collection**: company_documents

## Authentication

### Google OAuth Flow

1. User clicks "Sign in with Google"
2. Frontend redirects to Google OAuth
3. User authenticates with Google
4. Google redirects to callback with ID token
5. Frontend sends ID token to backend
6. Backend verifies token with Google
7. Backend creates/updates user record
8. Backend issues JWT token
9. Frontend stores token for subsequent requests

### JWT Authentication

- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Payload**: User ID
- **Storage**: HTTP-only cookies (recommended)

## Database Schema Overview

### Core Tables

#### Users
```sql
- id (PK)
- email (unique)
- full_name
- hashed_password
- google_id (unique)
- google_avatar_url
- is_active
- is_superuser
- created_at
- updated_at
```

#### Companies
```sql
- id (PK)
- symbol (unique)
- name
- exchange
- sector
- industry
- country
- currency
- description
- website
- is_active
- created_at
- updated_at
```

#### Portfolios
```sql
- id (PK)
- user_id (FK)
- name
- created_at
- updated_at
```

#### Holdings
```sql
- id (PK)
- portfolio_id (FK)
- company_id (FK)
- quantity
- average_buy_price
- purchase_date
- created_at
- updated_at
```

#### Watchlists
```sql
- id (PK)
- name
- user_id (FK)
- created_at
- updated_at
```

#### WatchlistCompany (Association)
```sql
- id (PK)
- watchlist_id (FK)
- company_id (FK)
- created_at
```

#### InvestorProfile
```sql
- id (PK)
- user_id (FK, unique)
- risk_profile
- investment_horizon
- investment_style
- preferred_market
- preferred_sectors
- notes
- created_at
- updated_at
```

#### UserCompanyView
```sql
- id (PK)
- user_id (FK)
- symbol
- viewed_at
```

### Relationships

- User → Portfolios (1:N)
- User → Watchlists (1:N)
- User → InvestorProfile (1:1)
- User → UserCompanyView (1:N)
- Portfolio → Holdings (1:N)
- Watchlist → WatchlistCompany (1:N)
- Company → Holdings (1:N)
- Company → WatchlistCompany (1:N)

## Deployment Architecture

### Resource Allocation

#### Frontend Task
- CPU: 256 vCPU
- Memory: 512 MB
- Port: 3000
- Desired Count: 1

#### Backend Task
- CPU: 256 vCPU
- Memory: 512 MB
- Port: 8000
- Desired Count: 1

#### Database
- Instance: db.t3.micro
- Storage: 20 GB gp3
- Engine: PostgreSQL 15
- Multi-AZ: No

### Networking

- VPC CIDR: 10.0.0.0/16
- Public Subnets: 10.0.1.0/24, 10.0.2.0/24
- Availability Zones: ap-south-1a, ap-south-1b
- Security Groups: ALB, ECS, RDS

### Load Balancer Configuration

- Type: Application Load Balancer
- Scheme: Internet-facing
- Listener: HTTP (Port 80)
- Routing:
  - `/api/v1/*` → Backend Target Group
  - `/*` → Frontend Target Group

## Future Improvements

- [ ] Implement GitHub Actions CI/CD pipeline
- [ ] Add HTTPS/SSL certificate with ACM
- [ ] Implement Redis caching for API responses
- [ ] Add unit and integration tests
- [ ] Implement rate limiting on API endpoints
- [ ] Add real-time WebSocket support for live prices
- [ ] Expand to support more stock exchanges
- [ ] Add technical analysis indicators
- [ ] Implement portfolio performance analytics
- [ ] Add notification system for price alerts
- [ ] Support for multi-language
- [ ] Mobile app development
- [ ] Add advanced charting tools
- [ ] Implement paper trading feature
- [ ] Add social features for sharing portfolios

## Troubleshooting

### Backend Issues

**Problem**: Database connection failed
```bash
# Solution: Check DATABASE_URL in .env
# Ensure PostgreSQL is running
docker-compose ps postgres
```

**Problem**: Qdrant connection timeout
```bash
# Solution: Verify QDRANT_URL and QDRANT_API_KEY
# Check Qdrant service status
curl http://localhost:6333/health
```

**Problem**: Embedding model loading fails
```bash
# Solution: Ensure sufficient memory
# The model is cached after first load
```

### Frontend Issues

**Problem**: NextAuth configuration error
```bash
# Solution: Verify NEXTAUTH_SECRET and NEXTAUTH_URL
# Ensure Google OAuth credentials are correct
```

**Problem**: API calls failing
```bash
# Solution: Check NEXT_PUBLIC_API_URL
# Verify backend is running
curl http://localhost:8000/health
```

### Docker Issues

**Problem**: Containers not starting
```bash
# Solution: Check logs
docker-compose logs

# Rebuild containers
docker-compose up -d --build
```

**Problem**: Port conflicts
```bash
# Solution: Change ports in docker-compose.yml
# Or stop conflicting services
```

### AWS Deployment Issues

**Problem**: ECS tasks not starting
```bash
# Solution: Check CloudWatch logs
# Verify task definition and environment variables
# Ensure security groups allow necessary traffic
```

**Problem**: Load balancer health checks failing
```bash
# Solution: Verify target group health check path
# Check security group rules
# Ensure containers are responding on expected ports
```

## Project Highlights

- **Production-Ready**: Fully containerized with Docker and部署到 AWS ECS
- **AI-Powered**: Advanced RAG pipeline with context-aware AI agent
- **Scalable**: Serverless architecture with ECS Fargate
- **Modern Tech Stack**: Latest versions of Next.js, FastAPI, and Python
- **Security**: JWT authentication + Google OAuth
- **Real-Time Data**: Integration with multiple financial data providers
- **Type Safety**: TypeScript frontend and Python type hints
- **Infrastructure as Code**: Terraform for reproducible deployments

## Contributors

- **Saran S** - Initial development and architecture

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for intelligent equity analysis**

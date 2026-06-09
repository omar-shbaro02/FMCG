# FMCG Trade Promotion Distortion Intelligence
# System Configuration Reference

## Database Configuration

### SQLite (Development/MVP)
```
DATABASE_URL=sqlite:///./fmcg_cases.db
```

### PostgreSQL (Production)
```
DATABASE_URL=postgresql://user:password@localhost:5432/fmcg_intelligence
```

### Other Databases
```
# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/fmcg

# Oracle
DATABASE_URL=oracle+cx_oracle://user:password@localhost:1521/fmcg
```

## OpenAI Configuration

### Recommended Models
```
# Best for quality (slower, more expensive)
OPENAI_MODEL=gpt-4o

# Good balance (faster, cheaper)
OPENAI_MODEL=gpt-4
OPENAI_MODEL=gpt-3.5-turbo
```

### API Configuration
```
OPENAI_API_KEY=sk-your-actual-key
OPENAI_ORG_ID=org-xxxxx  # Optional: for organization routing
```

## LLM Provider Integration

### OpenAI (Current)
Already configured in orchestrator.py

### Azure OpenAI
```python
# Modify orchestrator/orchestrator.py
from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
```

### Anthropic Claude
```python
# Install: pip install anthropic
# Usage: Modify agent prompts and orchestrator
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

### Local LLMs (Ollama, LM Studio)
```
OPENAI_API_BASE=http://localhost:8000/v1
OPENAI_API_KEY=not-needed
OPENAI_MODEL=local-model-name
```

## Agent Configuration

### Adjusting Agent Behavior

Each agent file (agent_1_intent.py, etc.) contains:

1. **AGENT_X_SYSTEM_PROMPT** - Core instructions
2. **create_agent_x_prompt()** - Context building
3. **parse_agent_x_response()** - Output parsing

### Tuning Recommendations

```python
# In orchestrator.py, modify LLM calls:

response = self.client.chat.completions.create(
    model=self.model,
    temperature=0.7,      # Lower = more deterministic, Higher = more creative
    max_tokens=2000,      # Lower = cheaper/faster, Higher = more comprehensive
    top_p=1.0,           # Nucleus sampling: 0.1-1.0
    frequency_penalty=0,  # -2.0 to 2.0: reduce repetition
    presence_penalty=0,   # -2.0 to 2.0: encourage diversity
)
```

## Application Configuration

### CORS Settings
```
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Production
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

### Logging
```
LOG_LEVEL=INFO
DEBUG=False

# Production
LOG_LEVEL=ERROR
DEBUG=False
```

## Performance Configuration

### Database Connection Pooling
```python
# In main.py, after engine creation:
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)
```

### API Rate Limiting
```python
# Install: pip install slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/cases/{case_id}/analyze")
@limiter.limit("10/minute")
async def analyze_case(...):
    ...
```

## Security Configuration

### API Key Management
```
# Never commit .env to version control
# Use environment variable secrets in production

# Recommended: Use cloud secret management
# AWS Secrets Manager
# Azure Key Vault
# Google Cloud Secret Manager
# HashiCorp Vault
```

### HTTPS Configuration
```python
# In production (using Uvicorn with SSL):
uvicorn main:app --ssl-keyfile=/path/to/key.pem --ssl-certfile=/path/to/cert.pem
```

### Authentication (Optional)
```python
# Add to main.py for basic auth:
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)):
    if credentials.credentials != os.getenv("API_SECRET_KEY"):
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials
```

## Monitoring & Observability

### Application Monitoring
```python
# Install: pip install prometheus-client

from prometheus_client import Counter, Histogram
import time

case_analysis_duration = Histogram('case_analysis_seconds', 'Time spent analyzing')

@case_analysis_duration.time()
async def analyze_case(...):
    ...
```

### Error Tracking
```python
# Install: pip install sentry-sdk
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1
)
```

## Frontend Configuration

### API Endpoint
In `frontend/src/hooks/useAPI.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api'
```

### Build Optimization
```javascript
// vite.config.js
export default {
  build: {
    minify: 'terser',
    sourcemap: false,  // Disable in production
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
        }
      }
    }
  }
}
```

## Deployment Configuration

### Docker
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DATABASE_URL: postgresql://user:pass@db:5432/fmcg
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

### Environment Variables Checklist

Required:
- [ ] OPENAI_API_KEY
- [ ] OPENAI_MODEL

Optional:
- [ ] DATABASE_URL (defaults to sqlite)
- [ ] FRONTEND_URL (defaults to localhost:5173)
- [ ] BACKEND_URL (defaults to localhost:8000)
- [ ] LOG_LEVEL (defaults to INFO)

## Troubleshooting Configuration

### High Token Usage
- Reduce `max_tokens` in orchestrator
- Use gpt-3.5-turbo instead of gpt-4
- Optimize prompts to be more concise

### Slow Analysis
- Increase `temperature` (enables more parallel thinking)
- Use faster model (gpt-3.5-turbo)
- Implement caching for similar cases

### API Rate Limits
- Implement request queuing
- Use batching for multiple cases
- Cache LLM responses

## Reference Configurations

### Development Environment
```env
DEBUG=True
LOG_LEVEL=DEBUG
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./fmcg_cases.db
```

### Staging Environment
```env
DEBUG=False
LOG_LEVEL=INFO
OPENAI_MODEL=gpt-4
DATABASE_URL=postgresql://user:pass@staging-db:5432/fmcg
```

### Production Environment
```env
DEBUG=False
LOG_LEVEL=ERROR
OPENAI_MODEL=gpt-4o
DATABASE_URL=postgresql://user:pass@prod-db:5432/fmcg
# Secrets managed via cloud provider
```

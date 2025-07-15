# Technical Architecture Documentation

## System Overview

The Financial Analysis Agent is built as a modular, extensible system that combines modern web technologies with AI-powered analysis capabilities.

## Architecture Principles

### 1. Separation of Concerns
- **Frontend**: Pure HTML/CSS/JS for UI interaction
- **Backend**: Python FastAPI for business logic
- **LLM Layer**: Abstracted provider system
- **Tools**: Isolated analysis components

### 2. Extensibility
- Plugin-style analysis tools
- Multiple LLM provider support
- Configurable analysis parameters
- Modular component registration

### 3. Real-time Communication
- WebSocket-based bidirectional communication
- Asynchronous processing with progress updates
- Session-based state management

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                       │
├─────────────────────────────────────────────────────────────┤
│  HTML/CSS/JS → WebSocket Client → Real-time UI Updates     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                      │
├─────────────────────────────────────────────────────────────┤
│  FastAPI → WebSocket Handler → Session Management          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator → Data Profiler → Query Processing           │
└─────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│        LLM Layer            │ │      Analysis Tools         │
├─────────────────────────────┤ ├─────────────────────────────┤
│ Provider Interface          │ │ Base Tool Class             │
│ ├─ Gemini Provider          │ │ ├─ Variance Analysis         │
│ ├─ OpenAI Provider          │ │ ├─ Preprocessing             │
│ └─ Future Providers         │ │ └─ Future Tools             │
└─────────────────────────────┘ └─────────────────────────────┘
```

## Data Flow Architecture

### 1. File Upload Flow
```
User Upload → Base64 Encode → WebSocket → Temp Storage → 
Data Profiler → Structure Analysis → Session Storage → 
UI Update
```

### 2. Query Processing Flow
```
User Query → WebSocket → LLM Provider → Tool Selection → 
Parameter Extraction → Tool Execution → Result Processing → 
Response Formatting → UI Update
```

### 3. Session Management Flow
```
Connection → Session Creation → Data Association → 
Conversation History → State Persistence → Cleanup
```

## Key Design Patterns

### 1. Provider Pattern (LLM Integration)
```python
class LLMProvider(ABC):
    @abstractmethod
    async def process_query(...) -> Dict[str, Any]
    
    @abstractmethod
    async def format_response(...) -> str
```

### 2. Tool Registry Pattern (Analysis Tools)
```python
class AnalysisTool(ABC):
    tool_name: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    
    def execute(self, data, params) -> output_schema
```

### 3. Factory Pattern (Component Creation)
```python
class LLMProviderFactory:
    @staticmethod
    def create_provider(config) -> LLMProvider
```

## Database Schema (Future Implementation)

### Proposed Tables
```sql
-- User sessions and data
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    data_profile JSONB
);

-- Conversation history
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    role VARCHAR(20),
    content TEXT,
    timestamp TIMESTAMP
);

-- Analysis results cache
CREATE TABLE analysis_cache (
    id UUID PRIMARY KEY,
    query_hash VARCHAR(64),
    tool_name VARCHAR(50),
    parameters JSONB,
    result JSONB,
    created_at TIMESTAMP
);
```

## Security Considerations

### Current Implementation
- File type validation
- Temporary file cleanup
- Environment variable configuration
- CORS configuration for development

### Future Security Enhancements
- Rate limiting
- Input sanitization
- Authentication/authorization
- File size limits
- Virus scanning

## Performance Characteristics

### Current Performance
- File upload: <1s for typical CSV files
- Data profiling: <500ms for standard datasets
- LLM query processing: 2-5s depending on provider
- WebSocket latency: <50ms local

### Optimization Opportunities
- Response caching
- Background processing queues
- Database query optimization
- CDN for static assets

## Monitoring and Logging

### Current Logging
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Future Monitoring
- Application performance monitoring
- Error tracking and alerting
- User analytics
- System health dashboards

## Deployment Architecture

### Development
- Local FastAPI server
- File-based session storage
- Environment variable configuration

### Production Considerations
- Containerization (Docker)
- Load balancing
- Database persistence
- Redis for session management
- File storage service (S3, etc.)

## Testing Strategy

### Current Status
- Manual testing of core workflows
- Error scenario validation
- Cross-browser compatibility

### Future Testing
```
Unit Tests → Integration Tests → E2E Tests → 
Performance Tests → Security Tests
```

## API Documentation

### WebSocket Messages

#### Client to Server
```json
{
  "type": "file_upload",
  "data": "base64_encoded_data",
  "file_name": "data.csv"
}

{
  "type": "query",
  "query": "natural language query"
}
```

#### Server to Client
```json
{
  "type": "file_processed",
  "profile_summary": {
    "file_name": "data.csv",
    "rows": 29,
    "columns": 5,
    "periods": ["2022", "2023", "2024", "2025"]
  }
}

{
  "type": "query_response",
  "response": "formatted analysis result"
}
```

## Configuration Management

### Environment Variables
```env
LLM_PROVIDER=gemini
LLM_API_KEY=your_key
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=8192
PORT=8000
DEBUG=false
```

### Runtime Configuration
- Dynamic tool registration
- Provider switching
- Parameter validation
- Error threshold configuration

---

## Future Architecture Evolution

### Phase 1: Enhanced Analytics
- Additional analysis tools
- Data visualization layer
- Export capabilities

### Phase 2: Scale & Performance
- Database integration
- Caching layer
- Background job processing

### Phase 3: Enterprise Features
- Multi-tenancy
- Advanced security
- Audit logging
- Role-based access control

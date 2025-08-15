# 🚀 DB RAG API - Usage Guide

## 📖 Overview

The DB RAG API enables natural language queries against relational databases using advanced RAG (Retrieval-Augmented Generation) technology. This guide provides comprehensive examples for testing the API using various tools.

## 🔧 Setup

### 1. Start the API Server

```bash
# Navigate to project directory
cd /path/to/db_rag_api

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\Activate.ps1  # Windows

# Start the server
python api.py
```

The API will be available at: `http://localhost:8000`

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication

### Development Mode (Default)

By default, the API runs in development mode with authentication disabled:

```bash
REQUIRE_AUTH=false
DEV_API_KEY=dev-api-key-12345
```

### Production Mode

Enable authentication by setting:

```bash
REQUIRE_AUTH=true
API_KEYS=your-secure-key-1,your-secure-key-2
```

### Using Authentication

Include the Bearer token in your requests:

```http
Authorization: Bearer dev-api-key-12345
```

## 🛠️ Testing Tools Setup

### Postman

1. Import the collection: `docs/api/postman_collection.json`
2. Set variables:
   - `base_url`: `http://localhost:8000`
   - `api_key`: `dev-api-key-12345`

### Bruno

1. Open Bruno and import the collection from: `docs/api/bruno_collection/`
2. Variables are pre-configured in the collection

### VS Code REST Client

1. Install the "REST Client" extension
2. Open `docs/api/api_collection.http`
3. Click "Send Request" above any request

### Insomnia

1. Create a new collection
2. Import the requests from the HTTP file or manually create them
3. Set base URL: `http://localhost:8000`
4. Add Bearer token: `dev-api-key-12345`

## 📋 API Endpoints

### 1. Health & Information

#### API Information
```http
GET /
```

#### Health Check
```http
GET /health
```

#### Authentication Info
```http
GET /auth/info
```

### 2. System Management

#### Initialize System
```http
POST /initialize
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "force_rebuild": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "System initialized successfully",
  "vector_store_created": true,
  "tables_indexed": 5,
  "initialization_time": 12.34
}
```

### 3. Database Queries

#### Natural Language Query
```http
POST /query
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "query": "What are the top 5 customers by revenue?",
  "query_type": "natural_language",
  "limit": 10,
  "include_explanation": true
}
```

#### SQL Query
```http
POST /query
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "query": "SELECT * FROM customers ORDER BY revenue DESC LIMIT 5",
  "query_type": "sql",
  "limit": 5,
  "include_explanation": false
}
```

**Response:**
```json
{
  "success": true,
  "query": "What are the top 5 customers by revenue?",
  "sql_query": "SELECT * FROM customers ORDER BY revenue DESC LIMIT 5",
  "results": [
    {"id": 1, "name": "Acme Corp", "revenue": 50000},
    {"id": 2, "name": "TechCorp", "revenue": 45000}
  ],
  "row_count": 2,
  "execution_time": 0.23,
  "explanation": "Generated SQL to find top customers by revenue..."
}
```

### 4. Schema Exploration

#### List All Tables
```http
GET /tables
Authorization: Bearer {api_key}
```

#### Get Schema Information
```http
POST /schema
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "table_name": "customers",
  "include_sample_data": true,
  "sample_limit": 3
}
```

#### Get All Schema
```http
POST /schema
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "include_sample_data": false
}
```

### 5. Statistics

#### Database Statistics
```http
GET /stats
Authorization: Bearer {api_key}
```

## 📝 Example Queries

### Natural Language Examples

1. **Revenue Analysis**
   ```json
   {"query": "What are the top 10 customers by total revenue?"}
   ```

2. **Time-based Queries**
   ```json
   {"query": "Show me all orders placed in the last 30 days"}
   ```

3. **Product Analysis**
   ```json
   {"query": "Which products have the highest profit margin?"}
   ```

4. **Customer Insights**
   ```json
   {"query": "Find customers who haven't placed orders in the last 90 days"}
   ```

5. **Sales Performance**
   ```json
   {"query": "What is the average order value by month this year?"}
   ```

### SQL Examples

1. **Basic Selection**
   ```json
   {"query": "SELECT * FROM products WHERE price > 100"}
   ```

2. **Aggregations**
   ```json
   {"query": "SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category"}
   ```

3. **Joins**
   ```json
   {"query": "SELECT c.name, COUNT(o.id) as order_count FROM customers c LEFT JOIN orders o ON c.id = o.customer_id GROUP BY c.id"}
   ```

## ⚡ Rate Limiting

- **Limit**: 100 requests per hour per API key
- **Headers**: Rate limit info included in response headers
- **Status Code**: 429 when limit exceeded

## 🔍 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Invalid query parameters",
  "error_code": "INVALID_PARAMS",
  "details": {"message": "Query cannot be empty"}
}
```

#### 401 Unauthorized
```json
{
  "error": "Invalid API key",
  "error_code": "INVALID_API_KEY",
  "details": {"message": "The provided API key is not valid"}
}
```

#### 429 Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "message": "Maximum 100 requests per 60 minutes",
    "retry_after": "60 seconds"
  }
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "details": {"message": "Database connection failed"}
}
```

## 🧪 Testing Workflow

### Recommended Testing Order

1. **Health Check**: Verify API is running
2. **Initialize**: Set up the RAG system
3. **List Tables**: Explore available data
4. **Schema**: Understand table structures
5. **Simple Queries**: Test basic functionality
6. **Complex Queries**: Test advanced features

### Sample Test Script

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Initialize system
curl -X POST http://localhost:8000/initialize \
  -H "Authorization: Bearer dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"force_rebuild": false}'

# 3. List tables
curl http://localhost:8000/tables \
  -H "Authorization: Bearer dev-api-key-12345"

# 4. Natural language query
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top 5 customers?", "query_type": "natural_language"}'
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///data/database.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Authentication
REQUIRE_AUTH=false
DEV_API_KEY=dev-api-key-12345

# OpenAI (for natural language processing)
OPENAI_API_KEY=your-openai-key-here
```

## 📚 Additional Resources

- **Swagger Documentation**: http://localhost:8000/docs
- **API Collections**: Available in `docs/api/` directory
- **Example Database**: Sample SQLite database included
- **Source Code**: Available in the project repository

## 🆘 Troubleshooting

### Common Issues

1. **API Not Starting**
   - Check if port 8000 is available
   - Verify virtual environment is activated
   - Check database connection string

2. **Authentication Errors**
   - Verify API key in Authorization header
   - Check REQUIRE_AUTH setting

3. **Query Failures**
   - Initialize the system first
   - Check database connection
   - Verify table names exist

4. **Rate Limiting**
   - Wait for rate limit window to reset
   - Use different API key if available

### Debug Mode

Enable debug mode for detailed error messages:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 💡 Best Practices

1. **Initialize Once**: Run `/initialize` once per session
2. **Explore Schema**: Use `/schema` to understand data structure
3. **Start Simple**: Begin with basic queries before complex ones
4. **Handle Errors**: Implement proper error handling in your applications
5. **Rate Limiting**: Respect rate limits and implement backoff strategies

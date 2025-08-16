# 🔧 Endpoints Corretos da Multi-LLM API

## ❌ **Problema Resolvido**

O endpoint `/auth/info` **NÃO EXISTE** na API atual. Aqui estão os endpoints corretos:

## ✅ **Endpoints Disponíveis**

### **1. Endpoints Públicos (sem autenticação)**
- `GET /` - Informações da API
- `GET /health` - Status de saúde

### **2. Endpoints Protegidos (requerem API key)**
- `GET /status` - Status completo do sistema
- `GET /providers` - Lista provedores disponíveis
- `POST /query` - Executa consultas em linguagem natural
- `POST /switch-provider` - Troca provedor ativo

## 🔑 **Autenticação**

Use a API key do seu arquivo `.env`:
```
Authorization: Bearer minha-api-key-AuTHvhpVGq_DHiBkg4wi_l7LxWathUy-pLNsar_K-oc
```

## 📋 **Arquivos Atualizados**

### **Para Postman:**
- ✅ `docs/api/postman_collection.json` - Endpoints corretos
- ✅ API Key configurada: `minha-api-key-AuTHvhpVGq_DHiBkg4wi_l7LxWathUy-pLNsar_K-oc`

### **Para VS Code REST Client:**
- ✅ `docs/api/api_collection.http` - Requests atualizados
- ✅ API Key configurada automaticamente

## 🚀 **Como Testar**

1. **Inicie a API:**
   ```bash
   python multi_llm_api.py
   ```

2. **Teste no Postman:**
   - Importe: `docs/api/postman_collection.json`
   - Todos os endpoints já estão configurados

3. **Teste no VS Code:**
   - Abra: `docs/api/api_collection.http`
   - Clique em "Send Request" em cada endpoint

## 📊 **Exemplos de Uso**

### **Status do Sistema:**
```http
GET http://localhost:9000/status
Authorization: Bearer minha-api-key-AuTHvhpVGq_DHiBkg4wi_l7LxWathUy-pLNsar_K-oc
```

### **Consulta Natural:**
```http
POST http://localhost:9000/query
Authorization: Bearer minha-api-key-AuTHvhpVGq_DHiBkg4wi_l7LxWathUy-pLNsar_K-oc
Content-Type: application/json

{
  "query": "What are the top 5 customers by revenue?",
  "provider": "ollama"
}
```

### **Trocar Provedor:**
```http
POST http://localhost:9000/switch-provider
Authorization: Bearer minha-api-key-AuTHvhpVGq_DHiBkg4wi_l7LxWathUy-pLNsar_K-oc
Content-Type: application/json

{
  "provider": "ollama",
  "type": "llm"
}
```

## 🔍 **Documentação Swagger**

Quando a API estiver funcionando, acesse:
- **Swagger UI:** http://localhost:9000/docs
- **ReDoc:** http://localhost:9000/redoc
- **OpenAPI JSON:** http://localhost:9000/openapi.json

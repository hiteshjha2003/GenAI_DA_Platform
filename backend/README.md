# Backend Server Documentation

The `backend/` directory contains a FastAPI application that serves as the API server for the GenAI Data Analytics Platform. It handles file uploads, AI queries, database operations, and charting.

## 📁 Backend Folder Structure

```
backend/
├── main.py              # FastAPI application with all API endpoints
├── requirements.txt     # Python dependencies
├── run.bat              # Windows startup script
└── README.md            # This file
```

## 🚀 Quick Start

### Using Startup Script (Recommended)

**Windows:**

```bash
cd backend
run.bat
```

Or manually:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://0.0.0.0:8000`.

### Vercel Deployment

The application is configured for Vercel deployment via the root `vercel.json` file.

**Deploy with Vercel CLI:**

```bash
# Install Vercel CLI
npm install -g vercel

# From project root:
cd d:\COACHXLIVE\DBA_WEB_APPS
vercel

# Deploy to production
vercel --prod
```

**What Vercel does:**
1. Reads `vercel.json` for configuration
2. Installs dependencies from `backend/requirements.txt`
3. Deploys `backend/main.py` handling `/api/*` routes
4. Serves `public/` directory as static frontend files

See root [README.md](../README.md) for complete deployment details.

## 🔌 API Endpoints

All endpoints are served from the `/api/*` path.

### Health & Status

- `GET /` - Root endpoint
- `GET /health` - Health check (legacy)
- `GET /api/health` - API health check

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_providers": ["openai", "groq", "ollama"],
  "datasets_loaded": 0
}
```

### File Upload & Data Management

- `POST /api/upload` - Upload file (CSV, Excel, PDF, DOCX, TXT)
- `GET /api/datasets` - Get all uploaded datasets
- `DELETE /api/datasets/{dataset_id}` - Delete dataset

### AI Queries

- `POST /api/query` - Execute AI query on data
- `GET /api/queries` - Get query history

### Charts & Visualization

- `POST /api/charts` - Create chart
- `GET /api/charts` - Get all charts

### Database Operations

- `POST /api/database/connect` - Connect to SQL Server
- `GET /api/database/tables` - Get database tables
- `GET /api/database/tables/{table_name}/schema` - Get table schema

### Settings

- `GET /api/settings` - Get application settings
- `POST /api/settings` - Update settings

## 📋 Supported File Types

- **Tables**: CSV, XLSX, XLS
- **Documents**: TXT, PDF, DOCX

## 🔧 Configuration

The backend works in **demo mode** without any configuration:
- File uploads are stored in memory
- AI queries return intelligent responses based on data
- No external API keys required

### Environment Variables (Optional)

Create a `.env` file in the project root (not in backend/):

```env
OPENAI_API_KEY=sk_your_key
GROQ_API_KEY=gsk_your_key
DEFAULT_LLM_PROVIDER=openai
OLLAMA_BASE_URL=http://localhost:11434
```

## 📊 API Documentation

When the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

Update the frontend API URL in `public/app.js`:

```javascript
// Change this line in public/app.js
const API_BASE_URL = `${window.location.origin}/api`;

// To use a different port:
const API_BASE_URL = `http://localhost:8080/api`;
```

### Dependencies Not Installing

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies with verbose output
pip install -v -r requirements.txt
```

### CORS Issues

The backend has CORS enabled for all origins (development mode). If you still get CORS errors:

1. Check backend is running: http://localhost:8000/health
2. Check frontend API URL matches backend address
3. Check browser console for exact error

## 🔄 Frontend-Backend Integration

### Frontend expects these endpoints:

- `GET /api/health` - Health check
- `POST /api/upload` - File upload
- `GET /api/datasets` - Get uploaded files
- `POST /api/query` - AI queries
- `POST /api/charts` - Create charts

### Running Full Stack

1. **Start Backend**: `cd backend && run.bat` (or `uvicorn main:app --reload`)
2. **Start Frontend**: `cd public && python -m http.server 8001`
3. **Open Browser**: http://localhost:8001

## 📝 Example Usage

### Upload File

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@data.csv"
```

### Execute Query

```bash
curl -X POST "http://localhost:8000/api/query" \
  -F "prompt=Show me total sales by region" \
  -F "provider=openai"
```

### Check Health

```bash
curl http://localhost:8000/health
```

## 📐 Technical Details

- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn 0.31.0
- **Python**: 3.11+
- **Data Processing**: pandas
- **File Parsing**: openpyxl, PyPDF2, python-docx

## 🔐 Security Notes

- Backend runs with CORS enabled for all origins (development mode)
- No authentication is required in demo mode
- For production, implement authentication and restrict CORS

## 📦 Requirements

- Python 3.11+
- Dependencies in `requirements.txt`:
  - fastapi - Web framework
  - uvicorn - ASGI server
  - pandas - Data processing
  - openpyxl - Excel support
  - PyPDF2 - PDF parsing
  - python-docx - DOCX parsing

## 🚀 Production Deployment

For production, consider:
- Adding authentication (JWT/OAuth)
- Implementing rate limiting
- Using a proper database (postgreSQL/MySQL)
- Configuring proper CORS origins
- Adding request validation
- Setting up logging and monitoring

## 📞 Support

- Check `main.py` for detailed endpoint documentation
- API Docs available at http://localhost:8000/docs
- All endpoints return JSON responses with `success` flag
# 🚀 GenAI Data Analytics Platform

A modern, production-ready **GenAI-powered data analytics application** with a beautiful interactive UI. Transform data with natural language queries, AI-powered insights, and intelligent visualizations.

![Platform Preview](https://via.placeholder.com/1200x600/6366f1/ffffff?text=GenAI+Data+Analytics+Platform)

---

## 📋 Quick Navigation

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Local Development](#-local-development)
- [Folder Structure](#-folder-structure)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Support](#-support)

---

## 🎯 Overview

GenAI Data Analytics Platform revolutionizes data analysis by combining Large Language Models with an intuitive web interface. No SQL knowledge needed - just ask questions in English and get instant results.

### What Problems Does It Solve?

✅ **For Business Analysts**: Generate reports without SQL knowledge  
✅ **For Data Teams**: Automate repetitive analysis tasks  
✅ **For Executives**: Get insights instantly via natural language  
✅ **For Developers**: Deploy on Vercel in minutes

---

## 🌟 Features

### Frontend UI

- ✨ **Responsive Dashboard** - Works on all devices
- 🎨 **Dark/Light Theme** - User preference support
- 📤 **Drag & Drop Upload** - Easy file management
- 💬 **AI Chat Interface** - Natural language queries
- 📊 **Chart Builder** - Multiple chart types
- ⚙️ **Settings Panel** - API keys, database config
- 📱 **Mobile Friendly** - Optimized for all screens

### Backend API

- 🔒 **RESTful API** - FastAPI with CORS
- 📝 **File Upload** - CSV, Excel, TXT, PDF, DOCX
- 🗄️ **Database** - SQL Server integration
- 🤖 **LLM Support** - OpenAI, Groq, Ollama
- 📊 **Data Processing** - Query execution
- 💾 **Export Options** - CSV, Excel formats

### Deployment Ready

- ✅ **Vercel Compatible** - One-click deploy
- 🌐 **Serverless** - Auto-scaling API
- 📦 **Zero Config** - Pre-configured
- 🔄 **Production Ready** - Built for scale

---

## 🛠️ Tech Stack

| Component      | Technology              | Version |
| -------------- | ----------------------- | ------- |
| **Frontend**   | HTML5, CSS3, JavaScript | ES6+    |
| **Charts**     | Chart.js                | Latest  |
| **Backend**    | FastAPI                 | 0.115+  |
| **Server**     | Uvicorn                 | 0.31+   |
| **Python**     | Python                  | 3.11+   |
| **LLM**        | OpenAI/Groq/Ollama      | Latest  |
| **Deployment** | Vercel                  | -       |

---

## 🚀 Quick Start

**No setup needed for demo!** Just open `public/index.html` in your browser.

```bash
# Clone repository
git clone https://github.com/your-repo/genai-analytics-platform.git
cd genai-analytics-platform

# Open in browser (Windows)
start public/index.html

# Or use Python server
cd public
python -m http.server 8000
# Visit http://localhost:8000
```

> The app works in **demo mode** without backend. Upload sample data and test all features!

---

### 🌐 Deployment

### One-Click Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/genai-analytics-platform)

### Manual Deployment (Vercel CLI)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to project
cd d:\COACHXLIVE\DBA_WEB_APPS

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Vercel Project Configuration

The `vercel.json` file configures the deployment:
- **Frontend**: Served from `public/` directory as static files
- **Backend**: FastAPI server handling `/api/*` routes
- **Python Runtime**: 3.11

### Environment Variables (Vercel Dashboard)

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional) | `sk-...` |
| `GROQ_API_KEY` | Groq API key (optional) | `gsk_...` |
| `DB_SERVERNAME` | SQL Server hostname | `localhost` |
| `DB_DATABASE` | Database name | `mydb` |
| `DB_USERNAME` | Database username | `sa` |
| `DB_PASSWORD` | Database password | `password` |

### Local Development (Before Deployment)

```bash
# Test backend locally
cd backend
uvicorn main:app --reload --port 8000

# In another terminal, test frontend
cd public
python -m http.server 8001

# Visit http://localhost:8001
```

### Troubleshooting Deployment

**Build fails:**
```bash
# Check Python version in vercel.json (should be 3.11)
# Verify requirements.txt exists in backend/
# Check Vercel build logs
vercel logs your-project.vercel.app --follow
```

**API routes not working:**
- Ensure `vercel.json` is properly configured
- Check that `backend/main.py` has all FastAPI endpoints

---

## 💻 Local Development

### Prerequisites

- Python 3.11 or higher
- pip

### Option 1: Frontend Only (Recommended for UI Development)

The frontend is a static single-page application. No backend needed for development/testing.

```bash
# Navigate to frontend directory
cd public

# Start a static file server (choose one)
python -m http.server 8000        # Python
npx http-server                    # Node.js (if available)

# Open in browser
# http://localhost:8000
```

**Frontend features in demo mode:**
- ✅ Upload files (generates sample data)
- ✅ Create charts and visualizations
- ✅ Chat with AI (simulated responses)
- ✅ Theme switching
- ✅ Settings storage

### Option 2: Full Stack (Frontend + Backend API)

Run the complete application with both frontend and backend.

**Terminal 1 - Start Backend:**

```bash
cd backend

# Windows: use the startup script
run.bat

# Or manually
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Reload enabled
```

**Terminal 2 - Start Frontend:**

```bash
cd public
python -m http.server 8001
```

**Access the application:**
- Frontend: http://localhost:8001
- API Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/docs

### Verify Setup

```bash
# Test backend is running
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","database":"connected","llm_providers":["openai","groq","ollama"]}
```

### Development Tips

- Frontend changes: Edit files in `public/` and refresh browser
- Backend changes: Edit `backend/main.py` - auto-reloads with `--reload`
- Backend API docs: http://localhost:8000/docs
- Use `Ctrl+C` to stop servers

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend not loading | Check http://localhost:8001 is running, clear browser cache |
| API calls failing | Ensure backend is running on port 8000, check `curl http://localhost:8000/health` |
| Port 8000 in use | Use `--port 8001` or another port: `uvicorn main:app --port 8001` |
| Import errors | Run `pip install -r backend/requirements.txt` |
| CORS errors | Backend has CORS enabled for all origins by default |

### Common Backend Issues

**Dependencies won't install:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install dependencies
pip install -r backend/requirements.txt
```

**Database won't connect:**
- Verify SQL Server is running
- Check server name, database name, and credentials
- Ensure firewall allows connections

---

## 📞 Support

| Resource | Link |
|----------|------|
| Backend Documentation | See [API Endpoints](#-api-endpoints) above |
| Backend README | [backend/README.md](backend/README.md) |
| Report Issues | GitHub Issues |

---

## 🙏 Contributing

We welcome contributions!

```bash
# 1. Fork the repository
# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes and test
# 4. Commit
git commit -m "Add feature"

# 5. Push and create Pull Request
git push origin feature/your-feature
```

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🚀 Quick Start

### Ready to Use?

1. ✅ Open `public/index.html` in browser
2. ✅ Try uploading sample data
3. ✅ Explore all features

### Ready to Run Full Stack?

1. ✅ Start backend: `cd backend && ./run.bat` (or `uvicorn main:app --reload`)
2. ✅ Start frontend: `cd public && python -m http.server 8001`
3. ✅ Visit http://localhost:8001

### Ready to Deploy to Vercel?

1. ✅ Push code to GitHub
2. ✅ Run `vercel` from project root
3. ✅ Visit your live app!

### Have Questions?

1. ✅ Check Troubleshooting section above
2. ✅ Review [backend/README.md](backend/README.md)
3. ✅ Check API docs at http://localhost:8000/docs

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
| Report Issues         | GitHub Issues                              |

---

## 🙏 Contributing

We welcome contributions!

```bash
# 1. Fork the repository
# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes and test
# 4. Commit
git commit -m "Add feature"

# 5. Push and create Pull Request
git push origin feature/your-feature
```

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🚀 Quick Start

### Ready to Use?

1. ✅ Open `public/index.html` in browser
2. ✅ Try uploading sample data
3. ✅ Explore all features

### Ready to Run Full Stack?

1. ✅ Start backend: `cd backend && ./run.bat` (or `uvicorn main:app --reload`)
2. ✅ Start frontend: `cd public && python -m http.server 8001`
3. ✅ Visit http://localhost:8001

### Have Questions?

1. ✅ Check Troubleshooting section above
2. ✅ Review [backend/README.md](backend/README.md)
3. ✅ Check API docs at http://localhost:8000/docs

---

**Last Updated:** May 2026  
**Version:** 2.0.0  
**Status:** ✅ Production Ready

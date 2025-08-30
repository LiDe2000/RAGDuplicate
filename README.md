# 🧾 RAGDuplicate - Duplicate Content Detection System

This project uses RAG technology to detect duplicate content in documents.

🚀 My First Frontend-Backend Separated Project.

## ✨ Features
- 📤 Upload documents for duplicate content checking
- 📄 Get results in markdown format
- ⬇️ Download results directly from the interface

## 📋 Prerequisites
- 🐍 Python 3.10+
- 🟩 Node.js 14+
- 📦 npm or yarn

## 💾 Installation

1. 🐍 Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. 🟩 Install Node.js dependencies:
```bash
npm install
```

## 🚀 Usage

### ⚙️ Start Methods

You can start both frontend and backend with simple commands from the project root:

🐍 Start the Python backend:
```bash
python .\backend\main.py
```

🐍 Alternative method to start the Python backend:
```bash
python -m backend.main
```

🟩 Start the Node.js frontend server:
```bash
npm start
```

The backend will be available at `http://localhost:8000`

The application will be available at:
- 🏠 Local access: `http://localhost:3000`
- 🌐 Network access: `http://[your-ip-address]:3000`

## 🌐 Network Access Configuration

To access the application from other devices on the local network:

1. ✅ Make sure both servers are running:
   - 🐍 Python backend on port 8000
   - 🟩 Node.js frontend on port 3000

2. 🔍 Find your computer's IP address:
   - 🪟 Windows: Run `ipconfig` in Command Prompt
   - 🍎 macOS/Linux: Run `ifconfig` or `ip addr` in Terminal

3. 📱 Access the application from another device on the same network:
   - 🌐 Open a browser and navigate to `http://[your-ip-address]:3000`

Note: ⚠️ Make sure your firewall allows incoming connections on port 3000 and 8000.

## 📚 API Documentation

When the backend is running, you can access the API documentation at:
- 📘 Swagger UI: `http://localhost:8000/docs`
- 📗 ReDoc: `http://localhost:8000/redoc`
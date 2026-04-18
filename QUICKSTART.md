# 🚀 Sentinel Protocol - Quick Start Guide

## System Status: ✅ FULLY OPERATIONAL

The Sentinel Protocol is a real-time misinformation verification system.

---

## 🏃 Quick Start (60 seconds)

### 1. Start Backend
```bash
cd backend
source ../venv/bin/activate
python run_server.py
# ✅ Server runs on http://localhost:8000
```

### 2. Start Frontend (new terminal)
```bash
cd frontend
npm start
# ✅ Frontend runs on http://localhost:3000
```

### 3. Open Browser
Navigate to: **http://localhost:3000**

---

## 📊 Dataset
- **Total Claims**: 26,232
- **Verified**: 15,913 (60.7%)
- **False**: 10,319 (39.3%)
- **Language**: Hindi Fake News

---

## 📍 What You Can Do

### 📊 Analytics
Real statistics from dataset, instant load

### 🔍 Intelligence Center  
Submit claims, get instant analysis

### 🚨 Active Threats
High-confidence false claims

### 📦 Archived Claims
Browse all 26K claims with pagination

### 🌍 Global Map
Geographic threat distribution

---

## ⚡ Performance

✅ Data endpoints: <100ms
⏳ Claim analysis: 2-10 min (first time), then cached

---

## 🔌 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get analytics
curl http://localhost:8000/analytics

# Get archived claims
curl http://localhost:8000/archived?page=1

# Get threats
curl http://localhost:8000/threats

# Get regions
curl http://localhost:8000/regions

# Analyze a claim
curl -X POST http://localhost:8000/analyze_claim \
  -H "Content-Type: application/json" \
  -d '{"text": "A virus found in Mumbai"}'
```

---

## ✨ Features

✅ Real-time claim verification  
✅ Semantic similarity search  
✅ 26K dataset integrated  
✅ Multi-page dashboard  
✅ Fast data endpoints  
✅ Professional UI  
✅ Pagination support  
✅ No hardcoded values  

---

**Built for Hackathon | Dataset: Bharat Fake News Kosh**

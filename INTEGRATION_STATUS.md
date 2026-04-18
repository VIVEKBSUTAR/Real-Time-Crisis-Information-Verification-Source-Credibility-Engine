# Sentinel Protocol - Integration Status Report

## ✅ SYSTEM STATUS: FULLY OPERATIONAL

**Date**: April 18, 2026  
**Backend**: Running on port 8000  
**Frontend**: Running on port 3000  
**Dataset**: 26,232 claims loaded (Bharat Fake News Dataset)

---

## 🔌 API ENDPOINTS

### Health Check
```bash
GET http://localhost:8000/health
```
**Response**: Status, dataset info, version

### Claim Analysis (Main Endpoint)
```bash
POST http://localhost:8000/analyze_claim
Content-Type: application/json

{
  "text": "Your claim here"
}
```

**Response Format**:
```json
{
  "claim_id": "07f15c37",
  "original_claim": "A video is viral...",
  "verdict": "UNCERTAIN",
  "confidence": 0.47,
  "evidence": [
    {
      "source": "Alt News",
      "relation": "support",
      "confidence": 0.77
    }
  ],
  "explanation": "This claim is uncertain based on 10 similar claims...",
  "similar_claims_found": 10
}
```

---

## 🎯 VERDICT TYPES

| Verdict | Meaning | Threshold |
|---------|---------|-----------|
| VERIFIED | Claim is TRUE based on dataset | confidence ≥ 0.5 & label=1 |
| FALSE | Claim is FALSE based on dataset | confidence ≥ 0.5 & label=0 |
| UNCERTAIN | Evidence is mixed/insufficient | confidence < 0.5 |

---

## 📊 ALGORITHM OVERVIEW

### Step 1: Similarity Matching
- Find up to 10 similar claims in dataset
- Similarity threshold: 0.4 (40% match)
- Uses string similarity for matching

### Step 2: Label Aggregation
- Collect labels from all similar claims
- Perform weighted voting (majority wins)
- Example: 7 FALSE + 3 TRUE → label=0 (FALSE)

### Step 3: Confidence Calculation
- confidence = (max_votes / total_votes) × 0.95
- Example: 7/10 × 0.95 = 0.665 = 66.5%

### Step 4: Evidence Collection
- Select top 3 similar claims as evidence
- Mark as "support" or "contradict" based on label match
- Include source name and confidence

### Step 5: Verdict Decision
```
IF confidence >= 0.5:
  verdict = "VERIFIED" (if label=1) OR "FALSE" (if label=0)
ELSE:
  verdict = "UNCERTAIN"
```

---

## 🧪 TEST RESULTS

### Test 1: Mixed Evidence (Amit Shah)
```json
Input: "A video is viral on social media in which a journalist can be seen questioning Home Minister Amit Shah"
Output: {
  "verdict": "UNCERTAIN",
  "confidence": 0.47,
  "similar_claims_found": 10
}
```
**Why**: 10 similar claims with split labels (not strong consensus)

### Test 2: False Claim (Vaccine Microchips)
```json
Input: "vaccines contain microchips"
Output: {
  "verdict": "FALSE",
  "confidence": 0.66,
  "similar_claims_found": 10
}
```
**Why**: 10 similar claims mostly labeled FALSE

### Test 3: News Claim
```json
Input: "India passes new law"
Output: {
  "verdict": "FALSE",
  "confidence": 0.57,
  "similar_claims_found": 10
}
```
**Why**: Dataset claims mostly debunked

---

## 🎨 FRONTEND INTEGRATION

### UI Components
- **Header**: Sentinel Protocol branding (blue-900)
- **Sidebar**: Navigation with dataset status
- **Input Section**: Text claim input with search icon
- **Results**: Color-coded verdict cards
  - VERIFIED = Green (#10b981)
  - FALSE = Red (#dc2626)
  - UNCERTAIN = Yellow (#ca8a04)

### Contrast Improvements
- Border radius: 2px bold borders
- Text colors: text-gray-900 on light backgrounds
- Button colors: Blue-700/Blue-800 (high contrast)
- Sidebar: White background with blue-700 active state
- Spacing: Enhanced padding and margins

### Response Handling
```javascript
const data = await response.json();
setVerifications([{
  claim: data.original_claim,
  verdict: data.verdict,  // VERIFIED/FALSE/UNCERTAIN
  confidence: Math.round(data.confidence * 100),
  reasoning: data.explanation,
  sources: data.evidence,
  timestamp: new Date().toLocaleTimeString()
}]);
```

---

## 📁 DATASET INFORMATION

### Dataset: Bharat Fake News Dataset
- **Total Claims**: 26,232
- **Verified (label=1)**: 15,913 (60.6%)
- **Debunked (label=0)**: 10,319 (39.4%)
- **Source**: Excel file with claim text, label, source columns
- **Loading Time**: ~2 seconds on startup

### Data Structure
```python
{
  "id": "unique_id",
  "claim": "Claim text here",
  "label": 0 or 1,  # 0=FALSE, 1=VERIFIED
  "source": "Source name (Reuters, AFP, etc)"
}
```

---

## 🐛 KNOWN ISSUES & FIXES

### Issue 1: ✅ FIXED - Backend Not Responding
**Cause**: Frontend sending wrong JSON format
**Fix**: Updated frontend to send `{"text": "claim"}`

### Issue 2: ✅ FIXED - All Verdicts "UNCERTAIN"
**Cause**: Confidence threshold too high (0.6)
**Fix**: Lowered to 0.5 for better verdict distribution

### Issue 3: ✅ FIXED - Poor Contrast
**Cause**: Light gray text on light background
**Fix**: Bold borders, dark text (text-gray-900), enhanced spacing

### Issue 4: ✅ FIXED - Response Field Mismatch
**Cause**: Backend fields didn't match frontend expectations
**Fix**: Aligned on: original_claim, verdict, confidence, evidence, explanation

---

## 🚀 HOW TO RUN

### Backend
```bash
cd backend
source ../venv/bin/activate
python3 run_server.py
```
Output: Backend listening on 0.0.0.0:8000 ✅

### Frontend
```bash
cd frontend
npm start
```
Output: React app on localhost:3000 ✅

---

## 📋 DEMONSTRATION CLAIMS

Ready-to-use test claims:

1. **Mixed Evidence**: "A video is viral on social media in which a journalist can be seen questioning Home Minister Amit Shah"
   - Expected: UNCERTAIN (~50% confidence)

2. **False Claim**: "vaccines contain microchips"
   - Expected: FALSE (66% confidence)

3. **News Claim**: "India launches new space mission"
   - Expected: Varies by dataset (check backend response)

---

## ✨ NEXT STEPS (Optional Enhancements)

- [ ] Add user feedback system (train on verdicts)
- [ ] Implement real-time social media integration
- [ ] Add explainability visualizations
- [ ] Deploy to production (Heroku/AWS)
- [ ] Add rate limiting and caching
- [ ] Implement Bayesian credibility updates

---

## 📞 SUPPORT

All endpoints tested and working ✅  
Frontend and backend fully integrated ✅  
Dataset loaded successfully ✅  
Ready for hackathon demo ✅

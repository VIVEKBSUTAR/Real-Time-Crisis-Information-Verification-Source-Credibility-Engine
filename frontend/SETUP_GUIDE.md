# SENTINEL PROTOCOL DASHBOARD — SETUP GUIDE

## Quick Start (5 minutes)

```bash
# 1. Navigate to frontend directory
cd "/Volumes/V_Mac_SSD/Hackathon/Breaking Enigma/demo1/frontend"

# 2. Install dependencies
npm install

# 3. Start development server
npm start

# Dashboard opens automatically at http://localhost:3000
```

---

## What You Get

A **production-ready crisis management dashboard** with:

✅ **Professional UI** — Beige/stone color palette, flat design, sharp borders  
✅ **Functional Form** — Submit incident reports, generate verifications  
✅ **Live Charts** — Trust score tracking with Recharts  
✅ **Mock Backend** — 2-second simulated processing  
✅ **Responsive Layout** — 12-column grid (4-col left, 8-col right)  
✅ **Data-Dense** — Monospace fonts for all numbers/URLs  

---

## Project Structure

```
frontend/
├── package.json                # Dependencies + scripts
├── tailwind.config.js          # Stone color palette + flat design
├── DASHBOARD_DOCS.md           # Complete design documentation
├── SETUP_GUIDE.md              # This file
├── public/
│   └── index.html              # HTML entry point
└── src/
    ├── Dashboard.jsx           # Main React component (400+ lines)
    ├── index.jsx               # React root render
    └── index.css               # Tailwind + global styles
```

---

## Dependencies Installed

```
react                    18.2.0    Frontend framework
react-dom               18.2.0    React renderer
tailwindcss              3.4.1    CSS utility framework
recharts                 2.10.3   Chart library
lucide-react             0.294.0  Icon library
```

**Total bundle size**: ~180KB (gzipped)

---

## Design System

### Colors (Stone Palette)
- **stone-50**: Background (#fafaf8) — Off-white
- **stone-100**: Secondary (#f5f5f3) — Light beige
- **stone-200**: Data boxes (#e7e5e0) — Medium grey
- **stone-300**: Borders (#d6d3d1) — Thin lines
- **stone-900**: Accents (#1c1917) — Dark charcoal

### Typography Rules
- **Headlines**: Bold sans-serif
- **Body text**: Regular sans-serif
- **Data/URLs**: Monospace (Courier New)
- **All inputs**: Forced to monospace

### Layout
- **Grid**: 12 columns total
- **Left panel**: 4 columns (Signal Ingestion + Trust Registry)
- **Right panel**: 8 columns (Verification Feed)
- **Borders**: Sharp, 1px solid
- **No rounding**, no shadows, no gradients

---

## Features Implemented

### ✅ Signal Ingestion Form
- Textarea for incident report (8 rows)
- URL input for source
- Media attachment button (display only)
- Submit button with validation
- Form clears on successful submission

### ✅ Live Trust Registry
- 3 domain buttons (Reuters, AP News, PIB)
- Clickable selection with visual feedback
- Recharts LineChart showing 5-point trust history
- Y-axis locked to 85-100 range
- Updates when domain selected

### ✅ Incident Verification Feed
- Loading spinner (2 seconds)
- Verification cards prepended to list
- Color-coded verdict (green/red)
- Bayesian score badge (top-right)
- Claim displayed in grey box
- Explanation paragraph
- Conditional metadata warning
- Clickable source links

### ✅ Mock Data Generation
- Random verdicts: VERIFIED, DEBUNKED, MANIPULATED
- Trust scores: 65-95%
- Recent changes: -15 to +15%
- 30% probability of metadata issues
- Deterministic explanations per verdict

---

## How It Works

### 1. User submits incident report
- Form validates non-empty text
- Submit button disabled if empty

### 2. Processing begins
- Form inputs cleared immediately
- Loading spinner shows for 2 seconds
- Button text changes to "PROCESSING..."

### 3. Verification card generated
- Random verdict assigned
- Trust score calculated (65-95%)
- Explanation templated
- 30% chance metadata warning appears

### 4. Card prepended to feed
- Newest cards always at top
- Feed maintains scrollable state
- Graph updates if domain changed

---

## Troubleshooting

### "npm: command not found"
Install Node.js from https://nodejs.org (LTS recommended)

### "Port 3000 already in use"
Kill existing process or use: `npm start -- --port 3001`

### Charts not rendering
Ensure Recharts installed: `npm install recharts@2.10.3`

### Tailwind styles not loading
Clear cache: `rm -rf node_modules && npm install`

### Monospace fonts not applying
Restart dev server: `npm start`

---

## Building for Production

```bash
# Create optimized build
npm run build

# Output: frontend/build/ (ready to deploy)

# Test production build locally
npx serve -s build
```

---

## Next Steps: Backend Integration

Replace mock data generation with real API calls to Sentinel Protocol backend.

---

## File Checklist

Before running, verify all files exist:

- [ ] `package.json` — Dependencies configured
- [ ] `tailwind.config.js` — Stone palette defined
- [ ] `public/index.html` — HTML entry point
- [ ] `src/Dashboard.jsx` — Main component (400+ lines)
- [ ] `src/index.jsx` — React root
- [ ] `src/index.css` — Tailwind imports

---

## Support

For issues or questions, refer to:
- `DASHBOARD_DOCS.md` — Complete design specification
- `src/Dashboard.jsx` — Component source code

---

**Status**: ✅ Production-ready (mock backend)  
**Version**: 1.0.0


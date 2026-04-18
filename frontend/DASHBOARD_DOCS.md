# SENTINEL PROTOCOL DASHBOARD
## Crisis Management Interface - React Implementation

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                     TOP NAVIGATION BAR                         │
│               SENTINEL PROTOCOL | ● OPERATIONAL                │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    [4 COLUMNS]          [8 COLUMNS]          
    LEFT PANEL            RIGHT PANEL
         │                    │
    ┌────┴────┐          ┌────┴─────┐
    │          │          │           │
  Signal  Trust Registry  Verification
 Ingestion               Feed
```

---

## DESIGN SYSTEM

### Color Palette (Stone Theme)
- **stone-50**: Background (#fafaf8) — Off-white
- **stone-100**: Secondary (#f5f5f3) — Light beige
- **stone-200**: Grey box (#e7e5e0) — Claim background
- **stone-300**: Borders (#d6d3d1) — Thin lines
- **stone-500**: Chart (#78716c) — Data visualization
- **stone-900**: Accents (#1c1917) — Dark text/buttons

### Typography Rules
- **Headlines**: Bold sans-serif (700 weight)
- **Body text**: Regular sans-serif (400 weight)
- **Data/URLs**: Monospace font (Courier New)
- **All inputs**: Forced to monospace

### Design Rules
- Sharp borders (1px solid)
- NO rounded corners
- NO shadows
- NO gradients
- Flat, data-dense layout
- Monospace for all numbers/URLs

---

## COMPONENT HIERARCHY

```
Dashboard (root)
├── Navigation (dark header)
│   ├── Title: "SENTINEL PROTOCOL"
│   └── Status: "● OPERATIONAL"
│
├── Left Panel (col-span-4)
│   ├── Signal Ingestion (form)
│   │   ├── Textarea (incident report)
│   │   ├── Input (source URL)
│   │   ├── File upload button
│   │   └── Submit button
│   │
│   └── Live Trust Registry (below form)
│       ├── Domain list (3 items, clickable)
│       └── Recharts LineChart (trust history)
│
└── Right Panel (col-span-8)
    └── Incident Verification Feed
        ├── Loading card (2 seconds)
        └── Verification cards (prepended)
            ├── Verdict header (colored)
            ├── Bayesian badge (top-right)
            ├── Claim box (grey)
            ├── Explanation text
            ├── Metadata warning (conditional)
            └── Source links (clickable)
```

---

## LEFT COLUMN: SIGNAL INGESTION

### Form Structure
```
┌─────────────────────────────────────┐
│ SIGNAL INGESTION                    │
├─────────────────────────────────────┤
│ Raw Incident Report                 │
│ [8-line textarea, monospace]         │
│                                     │
│ Source URL                          │
│ [single-line input, monospace]      │
│                                     │
│ [📎 Media Attachment]               │
│                                     │
│ [RUN VERIFICATION AUDIT]            │
└─────────────────────────────────────┘
```

**Features**:
- Textarea: 8 rows, monospace font (Courier New)
- Text input: Monospace font
- File button: Display only (no upload handling in MVP)
- Submit button: 
  - Dark background (stone-900)
  - White text
  - Bold font (600 weight)
  - Full width
  - Disabled during loading

**Behavior**:
- Validates: Incident report non-empty
- On submit: 
  - Disable form
  - Set loading state
  - Wait 2 seconds (simulated backend)
  - Generate mock verification card
  - Prepend to feed
  - Clear form inputs

---

## LEFT COLUMN: LIVE TRUST REGISTRY

### Registry List
```
┌─────────────────────────────────────┐
│ LIVE TRUST REGISTRY                 │
├─────────────────────────────────────┤
│ Reuters              [96%]           │
│ AP News              [94%]           │
│ PIB                  [92%]           │
└─────────────────────────────────────┘
```

**Features**:
- **3 domains**: Reuters, AP News, PIB (India Press Info Bureau)
- **Clickable**: Highlight on selection
- **Scores**: Right-aligned, monospace, percentage suffix
- **Visual feedback**: 
  - Selected: stone-100 background, stone-900 border
  - Unselected: Transparent, stone-300 border

### Trust History Chart
```
Recharts LineChart showing 5 data points:
- Time range: 10:00, 10:15, 10:30, 10:45, 11:00 (monospace)
- Y-axis: 85-100 (domain-specific credibility range)
- Line color: stone-500
- Line width: 1px
- No dots/markers
- Vertical grid: disabled
- Horizontal grid: enabled
- Tooltip: Custom styled (matching dashboard theme)
- Height: 200px
```

**Data Structure** (mock):
```javascript
{
  'reuters.com': [
    { time: '10:00', score: 96 },
    { time: '10:15', score: 95.5 },
    { time: '10:30', score: 96.2 },
    { time: '10:45', score: 95.8 },
    { time: '11:00', score: 96 }
  ],
  'apnews.com': [ ... ],
  'pib.gov.in': [ ... ]
}
```

**Behavior**:
- Updates when user clicks domain
- Fetches data from hardcoded mock object
- Animates (optional, may be disabled for flat design)
- No tooltip interaction needed for MVP

---

## RIGHT COLUMN: INCIDENT VERIFICATION FEED

### Loading State (2 seconds)
```
┌────────────────────────────────────────────────────┐
│                                                    │
│               [spinner animation]                  │
│          Processing verification...                │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Verification Card Structure
```
┌────────────────────────────────────────────────────────────────┐
│ VERIFIED                    [reuters.com 96% +8]               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Bridge collapse reported in Pune, infrastructure damage.     │
│  (grey box with stone-200 background)                         │
│                                                                │
│ This claim has been verified through analysis of trusted     │
│ sources. Multiple sources corroborate the event timeline      │
│ and geographic details match official reports.                │
│                                                                │
│ ⚠ EXIF METADATA CONTRADICTS CLAIM TIMELINE                   │
│   (red box, monospace text, bold)                             │
│                                                                │
│ Trusted Sources:                                              │
│ City Emergency Services  |  AP News  |  Reuters               │
│ (all monospace, underlined, clickable)                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Card Colors by Verdict**:
- **VERIFIED**: Green theme
  - Background: green-50 (#f0fdf4)
  - Border: green-200 (#dcfce7)
  - Header text: green-700 (#b91c1c)
  
- **DEBUNKED**: Red theme
  - Background: red-50 (#fef2f2)
  - Border: red-200 (#fecaca)
  - Header text: red-700 (#dc2626)
  
- **MANIPULATED**: Red theme (same as DEBUNKED)

**Card Elements**:

1. **Verdict Header** (16px, bold, colored)
   - Left: "VERIFIED", "DEBUNKED", or "MANIPULATED"
   - Right: Bayesian badge

2. **Bayesian Score Badge** (monospace, 12px)
   ```
   Format: "[domain] [score]% [change]"
   Example: "reuters.com 96% +8"
   Background: stone-900
   Text: white (stone-50)
   Padding: 4px 8px
   Border: 1px solid stone-300
   ```

3. **Claim Box** (grey, bordered, 14px)
   - Background: stone-200
   - Border: 1px solid stone-300
   - Padding: 12px
   - Font: Monospace (because it's data)

4. **Explanation Paragraph** (14px, regular, stone-700)
   - Line-height: 1.6
   - Margin top/bottom: 16px
   - Width: 100%

5. **Metadata Warning** (conditional, red, 12px)
   - Background: red-50
   - Border: 1px solid red-200
   - Text: red-700 (bold, monospace)
   - Icon: Warning triangle
   - Padding: 12px
   - Only shows if `hasMetadataIssue === true`

6. **Source Links** (monospace, 12px, underlined)
   - Format: "Source1  |  Source2  |  Source3"
   - Hover: Cursor pointer, underline thickens
   - Color: stone-600, hover: stone-900

**Card Ordering**:
- Newest card prepends to array (top)
- Remove oldest cards when count > 20 (optional optimization)

---

## STATE MANAGEMENT

### React Hooks
```javascript
const [incidentReport, setIncidentReport] = useState('');
const [sourceUrl, setSourceUrl] = useState('');
const [isLoading, setIsLoading] = useState(false);
const [verifications, setVerifications] = useState([]);
const [selectedDomain, setSelectedDomain] = useState('reuters.com');
```

### Data Structures

**Verification Object**:
```javascript
{
  id: 'v_' + Date.now(),
  claim: "Bridge collapse reported in Pune...",
  verdict: 'VERIFIED' | 'DEBUNKED' | 'MANIPULATED',
  score: 96,                    // Credibility 0-100
  domain: 'reuters.com',        // Trusted source
  change: +8,                   // Recent trend -15 to +15
  explanation: "This claim has been verified...",
  hasMetadataIssue: false,      // 30% probability true
  sources: ['City Emergency', 'AP News', 'Reuters']
}
```

**Domain Data**:
```javascript
const domains = [
  { name: 'Reuters', url: 'reuters.com', score: 96 },
  { name: 'AP News', url: 'apnews.com', score: 94 },
  { name: 'PIB', url: 'pib.gov.in', score: 92 }
];

const trustHistory = {
  'reuters.com': [
    { time: '10:00', score: 96 },
    { time: '10:15', score: 95.5 },
    // ...
  ]
};
```

### Event Handlers

**handleSubmit()**:
```
1. Validate incidentReport is non-empty
2. setIsLoading(true)
3. setIncidentReport('') && setSourceUrl('')
4. await 2000ms
5. generateMockVerification(incidentReport, sourceUrl)
6. setVerifications([new, ...existing])
7. setIsLoading(false)
```

**handleSelectDomain(domainUrl)**:
```
1. setSelectedDomain(domainUrl)
2. Chart component watches selectedDomain and re-renders
```

---

## MOCK DATA GENERATION

### generateMockVerification()
```javascript
function generateMockVerification(claim, url) {
  const verdicts = ['VERIFIED', 'DEBUNKED', 'MANIPULATED'];
  const verdict = verdicts[Math.floor(Math.random() * 3)];
  
  return {
    id: 'v_' + Date.now(),
    claim: claim || 'Default incident report',
    verdict: verdict,
    score: Math.floor(Math.random() * 30) + 65,  // 65-95
    domain: domains[0].url,                       // Always Reuters for MVP
    change: Math.floor(Math.random() * 31) - 15,  // -15 to +15
    explanation: getExplanation(verdict),
    hasMetadataIssue: Math.random() < 0.3,       // 30% chance
    sources: ['City Emergency', 'AP News', 'Reuters']
  };
}

function getExplanation(verdict) {
  if (verdict === 'VERIFIED')
    return 'This claim has been verified through analysis...';
  if (verdict === 'DEBUNKED')
    return 'This claim has been debunked by multiple...';
  return 'This claim contains manipulated elements...';
}
```

---

## INSTALLATION & RUNNING

```bash
# Navigate to frontend directory
cd "/Volumes/V_Mac_SSD/Hackathon/Breaking Enigma/demo1/frontend"

# Install dependencies
npm install

# Start development server (port 3000)
npm start

# Build for production
npm run build
```

---

## FILE STRUCTURE

```
frontend/
├── package.json               # Dependencies, scripts
├── tailwind.config.js         # Tailwind configuration (stone palette)
├── DASHBOARD_DOCS.md          # This file
├── public/
│   └── index.html             # HTML entry point (React mounts here)
└── src/
    ├── Dashboard.jsx          # Main component (all UI logic)
    ├── index.jsx              # React root render
    └── index.css              # Tailwind imports, global styles
```

---

## DEPENDENCIES

```json
{
  "react": "18.2.0",
  "react-dom": "18.2.0",
  "tailwindcss": "3.4.1",
  "recharts": "2.10.3",
  "lucide-react": "0.294.0"
}
```

---

## NEXT PHASE: BACKEND INTEGRATION

Replace mock function with real API calls:

```javascript
const handleSubmit = async () => {
  if (!incidentReport.trim()) return;
  
  setIsLoading(true);
  setIncidentReport('');
  setSourceUrl('');
  
  try {
    const response = await fetch('http://localhost:8000/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        claim: incidentReport,
        sourceUrl: sourceUrl
      })
    });
    
    const verification = await response.json();
    setVerifications([verification, ...verifications]);
  } catch (error) {
    console.error('Verification failed:', error);
  } finally {
    setIsLoading(false);
  }
};
```

---

## PERFORMANCE NOTES

- Recharts renders efficiently with 5-point datasets
- No animations enabled (flat design)
- CSS-in-JS via Tailwind keeps bundle small
- Form input events are instant (no debouncing needed)
- Card array management: Remove oldest when count exceeds 20

---

## ACCESSIBILITY

- All inputs have associated labels
- Navigation status indicator provides context
- Monospace fonts ensure data scanability
- High contrast: stone-900 on stone-50 (WCAG AA)
- Semantic HTML elements used


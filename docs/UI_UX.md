# UI/UX Design & Interface Specification

## Product Name: AI Resume Analyzer & ATS Job Matcher (ResumeIQ)
**Document Version:** 1.0  
**Status:** Approved Design Specification  
**Design Aesthetic:** Modern Minimalist Editorial & Warm Glassmorphism  

---

## 1. Design System & Style Guide

### 1.1 Palette & Color System
The application uses an editorial, warm palette combining rich terracotta (`--clay`), deep obsidian ink (`--ink`), and warm muted parchment backgrounds (`--bg-soft`).

```css
:root {
  /* Brand Primary Accents */
  --clay: #D97757;             /* Terracotta Brand Primary */
  --clay-dark: #BF5B3E;        /* Hover & Primary Gradient Dark */
  --clay-deep: #96442E;        /* Active Accent & Deep Borders */

  /* Neutral Ink Hierarchy */
  --ink: #1F1B16;              /* Primary High-Contrast Headlines & Text */
  --ink-dim: #6B6459;          /* Secondary Body Text & Sub-captions */
  --ink-faint: #A8A096;        /* Placeholders & Disabled Icons */

  /* Surface & Background Neutrals */
  --bg-soft: #F5F4ED;          /* Page Background / Input Containers */
  --surface: #FFFFFF;          /* Card & Container Fill */
  --white: #FFFFFF;
  --border: #E1DED2;           /* Subtle Dividers & Card Outlines */

  /* Contextual Status Colors */
  --success: #008A05;          /* High Match (>=75%) & Matched Badges */
  --success-bg: rgba(0,138,5,0.08);
  --success-border: rgba(0,138,5,0.25);
  
  --warning: #D97706;          /* Moderate Match (50-74%) */
  --warning-bg: rgba(217,119,6,0.08);
  
  --error: #C13515;            /* Low Match (<50%) & Validation Alerts */
  --error-bg: #FEF1EF;
  --error-border: #FBD4CD;

  /* Typography Tokens */
  --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif: 'Source Serif 4', Georgia, serif;

  /* Elevation & Geometry */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-sm: 0 2px 4px rgba(31, 27, 22, 0.04);
  --shadow-md: 0 4px 12px rgba(31, 27, 22, 0.08);
  --shadow-lg: 0 8px 24px rgba(31, 27, 22, 0.12);
}
```

---

## 2. Page & Layout Specifications

### 2.1 Hero & Upload Area (`index.html`)
* **Dual Input Layout:** Supports PDF File Upload (with drag-and-drop boundary) or Direct Text Paste.
* **Target Job Description / Role Field:** High-contrast textarea with active focus borders in terracotta (`--clay`), supporting both detailed job descriptions and short target role titles with clear placeholder guidance.
* **Submit CTA Button:** Elevated glass button with hover scale micro-animations (`transform: translateY(-2px)`).

### 2.2 Results Dashboard (`result.html`)
* **Overall Match Gauge:** Interactive SVG radial ring chart displaying overall ATS score (0-100%) with dynamic stroke color interpolation.
* **Sub-Score Cards:** Grid breakdown of Keyword Match (35%), Semantic Match (35%), Experience Alignment (15%), and Resume Quality (15%).
* **Skill Badges:** Categorized visual pills for Matched (Green) and Missing (Red/Yellow) skills.
* **Floating AI Chatbot Widget:** Floating drawer accessible across all pages with context-aware resume query capabilities (`window.RESUME_CONTEXT`).

### 2.3 Analysis History (`history.html`)
* **Analysis Table:** Clean Swiss/editorial table listing past runs, target role, status pills, ATS score bars, and date timestamps.


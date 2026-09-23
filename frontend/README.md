# Metri-Report Frontend Platform
## Smart OIML R-76 Statutory Testing & Metrology Automation UI

Metri-Report Frontend is an enterprise-grade, high-fidelity WebGL 3D interactive web application designed for the statutory evaluation, testing, and certification of Non-Automatic Weighing Instruments (NAWI) strictly adhering to **OIML Recommendation R 76-1 Edition 2006 (E)** and the **Legal Metrology Act, 2009**.

---

## 🏛️ Core Modules & Navigation Routes

| Module | Route URL | Description |
|---|---|---|
| **Homepage** | [`/`](http://localhost:3000/) | Interactive 3D WebGL hero, kinetic typography animation (*Measure, Validate, Report*), interactive video hold demo, typewriter headline, and feature grid. |
| **Evaluation Workspace** | [`/evaluation-workspace`](http://localhost:3000/evaluation-workspace) | 7-Step statutory test wizard with 3D digital scale twin, 5-point eccentricity interactive map, turning point observations, MPE error envelope calculations, and 1-click official PDF/DOCX generation. |
| **Instrument Registry** | [`/instrument-registry`](http://localhost:3000/instrument-registry) | NAWI instrument database with OIML Accuracy Classes (Class I, II, III, IIII), verification scale interval ($e$), multi-interval / multi-range specifications, and search filters. |
| **Report Archive** | [`/report-archive`](http://localhost:3000/report-archive) | Tamper-proof certificate archive with cryptographic SHA-256 validation, versioning, status badges (Approved, Draft, Finalized), and instant report viewer. |
| **Evidence & Vault** | [`/evidence-&-vault`](http://localhost:3000/evidence-&-vault) | Cryptographic evidence repository for calibration weight certificates (OIML E2/F1), raw testing logs, device photos, and cryptographic hash verification. |
| **User Privileges & RBAC** | [`/user-privileges-&-rbac`](http://localhost:3000/user-privileges-&-rbac) | Role-Based Access Control manager for Legal Metrology Officers, Lab Managers, Reviewers, and Test Engineers with dynamic permission toggles. |
| **Audit Trail Log** | [`/audit-trail-log`](http://localhost:3000/audit-trail-log) | Immutable cryptographic event log capturing test modifications, officer IP addresses, timestamps, and JSON event payload inspection. |
| **OIML Rule Engine** | [`/OIML-Rule-Engine`](http://localhost:3000/OIML-Rule-Engine) | Interactive statutory rule inspector, tolerance curve viewer, and clause lookup across Clauses 2, 3, A.4, A.5, A.6, Annex B, and Annex G. |
| **Legal & Privacy** | [`/terms-of-service`](http://localhost:3000/terms-of-service) & [`/privacy`](http://localhost:3000/privacy) | Legal Metrology statutory terms, data confidentiality, and privacy policy. |

---

## 💻 Running the Frontend Locally

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher

### Start the Gateway Server
```bash
cd frontend
npm install
node server.js
```

The application will be accessible at:
- 🌐 **Web Interface**: [http://localhost:3000](http://localhost:3000)
- 📑 **API Documentation (Reverse-Proxied)**: [http://localhost:3000/docs](http://localhost:3000/docs)

---

## 🎨 Visual Identity & Design System

1. **Typography**:
   - **Display / Kinetic Typography**: `ABC Favorit Light` (`font-weight: 300`, geometric stroke and letterforms).
   - **Headings & Accent UI**: `Outfit` (`font-weight: 500 – 800`).
   - **Body & Data**: `Inter` / `Suisse Int'l` (`font-weight: 400 – 600`).
   - **Monospace Metrology Values**: `JetBrains Mono` / `Suisse Int'l Mono` (for tare, weights, formulas, error $\Delta L$, and SHA-256 hashes).

2. **Color Palette & Accents**:
   - **Primary Background**: Charcoal Navy Dark Mode (`#0a0b10`, `#11131b`)
   - **Vibrant Accent**: Metri Pink (`#ff2d75`, `#ff488b`)
   - **Metrology Cyan & Blue**: (`#38bdf8`, `#6366f1`)
   - **Compliance Statuses**: Success Green (`#10b981`), Warning Amber (`#f59e0b`), Error Red (`#ef4444`)

3. **Brand Emblem & Favicon**:
   - High-contrast solid hot-pink emblem featuring the statutory weighing scale and sealed test report document.
   - Direct Base64 Data-URI embedding for zero-cache latency across all desktop and mobile browsers.

4. **Cross-Device Responsiveness**:
   - Full support from **Mobile S (320px)** up to **4K Ultra-HD (3840px)** with adaptive clamps and touch-bleed prevention.

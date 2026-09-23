# METRI-REPORT
## Smart OIML R-76 Statutory Testing & Legal Metrology Automation Platform

**SIH 2026 Prototype**  
**Organization:** Department of Consumer Affairs, Ministry of Consumer Affairs, Food & Public Distribution, Government of India.  
**Problem Statement:** *"Development of a Software Program/Application for Generation of Test Reports for Non-Automatic Weighing Instruments (NAWI) as per OIML Recommendation R-76"*

---

## 1. System Overview & Architecture

**METRI-REPORT** is a full-stack, enterprise-grade digital compliance and test reporting system built to automate the type evaluation, verification workflow, and statutory report generation for Non-Automatic Weighing Instruments (NAWI) strictly adhering to **OIML Recommendation R 76-1 Edition 2006 (E)** and the **Legal Metrology (General) Rules, 2011**.

```
                            ┌──────────────────────────────────────────────┐
                            │          METRI-REPORT 3D WEBGL UI            │
                            │   Three.js + GLTF Mesh + Vanilla JS Modules  │
                            │   ABC Favorit + Outfit Design System         │
                            │   Port: 3000 (Node Gateway / Reverse Proxy)  │
                            └──────────────────────┬───────────────────────┘
                                                   │ (REST API / Reverse Proxy)
                                                   ▼
                            ┌──────────────────────────────────────────────┐
                            │             FastAPI Backend Layer            │
                            │  CORS + Pydantic v2 + Dependency Injection   │
                            │  Port: 8000 (Uvicorn Async Worker)           │
                            └──────────────────────┬───────────────────────┘
                                                   │
     ┌──────────────────┬──────────────────────────┼──────────────────────────┬──────────────────┐
     ▼                  ▼                          ▼                          ▼                  ▼
┌──────────┐    ┌───────────────┐         ┌─────────────────┐        ┌───────────────┐    ┌───────────┐
│ Auth &   │    │ Validation    │         │ OIML Versioned  │        │  Calculation  │    │ Report    │
│ RBAC     │    │ & Applicabil. │         │ Rule Engine     │        │  & MPE Engine │    │ Engine    │
│ (JWT)    │    │ (Pydantic/Zod)│         │ (JSON/DB Rules) │        │  (OIML R-76)  │    │ PDF/DOCX  │
└────┬─────┘    └───────┬───────┘         └────────┬────────┘        └───────┬───────┘    └─────┬─────┘
     │                  │                          │                          │                  │
     └──────────────────┴──────────────────────────┼──────────────────────────┴──────────────────┘
                                                   ▼
                            ┌──────────────────────────────────────────────┐
                            │       SQLAlchemy 2.0 ORM + SQLite / Postgres │
                            │  Immutable Cryptographic Audit Trails        │
                            └──────────────────────┬───────────────────────┘
                                                   │
                                                   ▼
                            ┌──────────────────────────────────────────────┐
                            │ File Storage (Evidence, Photos, PDF, DOCX)   │
                            │ Local FS / S3 Abstraction + SHA-256 Hashing  │
                            └──────────────────────────────────────────────┘
```

---

## 2. Project Directory Structure

```
MetriReport/
├── backend/                        # FastAPI REST API Backend
│   ├── app/
│   │   ├── api/                    # Versioned REST Routers (v1)
│   │   ├── calculations/           # Metrological Turning Point & MPE Formulae
│   │   ├── compliance/             # OIML R-76 Statutory Rule Enforcers
│   │   ├── core/                   # Security, JWT, Database & Config
│   │   ├── models/                 # SQLAlchemy 2.0 Database Models
│   │   ├── reports/                # PDF & DOCX Certificate Generators
│   │   ├── schemas/                # Pydantic v2 Request/Response Models
│   │   ├── services/               # Cryptographic Hashing & Business Logic
│   │   └── tests/                  # 32+ Unit, Integration & Math Test Suite
│   └── requirements.txt            # Python Dependencies
│
├── frontend/                       # Production 3D WebGL Frontend & Subpages
│   ├── index.html                  # Interactive 3D Homepage with Kinetic Typography
│   ├── evaluation-workspace/       # 7-Step Statutory Evaluation Wizard & 3D Twin
│   ├── instrument-registry/        # NAWI Instrument Registration & Registry Table
│   ├── report-archive/             # Statutory Certificate Archive & Verification
│   ├── evidence-&-vault/           # Tamper-Proof Cryptographic Evidence Vault
│   ├── user-privileges-&-rbac/     # Officer Roles, Privileges & RBAC Manager
│   ├── audit-trail-log/            # Immutability Audit Logs & Event Timeline
│   ├── OIML-Rule-Engine/           # OIML R-76 Rule Inspector & Tolerance Curve
│   ├── server.js                   # Node.js Static Server & Reverse Proxy (Port 3000)
│   ├── subpage-shell.css           # Unified Statutory Subpage Styling & Theme
│   ├── fonts/                      # High-Fidelity ABC Favorit & Suisse Int'l Fonts
│   └── assets/                     # 3D Models, Emblems, Logos, and Video Posters
│
├── docs/                           # Architecture Blueprints & Compliance Matrices
└── README.md                       # Comprehensive System Documentation
```

---

## 3. Statutory Metrology Modules & Live Endpoints

| Module | URL Path | Description |
|---|---|---|
| **Homepage** | [`http://localhost:3000/`](http://localhost:3000/) | 3D WebGL hero ribbon, kinetic word animation (*Measure, Validate, Report*), interactive video hold demo, and module directory. |
| **Evaluation Workspace** | [`http://localhost:3000/evaluation-workspace`](http://localhost:3000/evaluation-workspace) | 7-Step statutory test wizard with 3D digital scale twin, 5-point eccentricity map, turning point observations, MPE error envelope calculations, and 1-click official PDF/DOCX generation. |
| **Instrument Registry** | [`http://localhost:3000/instrument-registry`](http://localhost:3000/instrument-registry) | NAWI instrument database with OIML Accuracy Classes (Class I, II, III, IIII), verification scale interval ($e$), multi-interval / multi-range specifications. |
| **Report Archive** | [`http://localhost:3000/report-archive`](http://localhost:3000/report-archive) | Tamper-proof certificate archive with cryptographic SHA-256 validation, versioning, status badges (Approved, Draft, Finalized), and instant report viewer. |
| **Evidence & Vault** | [`http://localhost:3000/evidence-&-vault`](http://localhost:3000/evidence-&-vault) | Cryptographic evidence repository for calibration weight certificates (OIML E2/F1), raw testing logs, device photos, and cryptographic hash verification. |
| **User Privileges & RBAC** | [`http://localhost:3000/user-privileges-&-rbac`](http://localhost:3000/user-privileges-&-rbac) | Role-Based Access Control manager for Legal Metrology Officers, Lab Managers, Reviewers, and Test Engineers with dynamic permission toggles. |
| **Audit Trail Log** | [`http://localhost:3000/audit-trail-log`](http://localhost:3000/audit-trail-log) | Immutable cryptographic event log capturing test modifications, officer IP addresses, timestamps, and JSON event payload inspection. |
| **OIML Rule Engine** | [`http://localhost:3000/OIML-Rule-Engine`](http://localhost:3000/OIML-Rule-Engine) | Interactive statutory rule inspector, tolerance curve viewer, and clause lookup across Clauses 2, 3, A.4, A.5, A.6, Annex B, and Annex G. |
| **Swagger API Docs** | [`http://localhost:3000/docs`](http://localhost:3000/docs) | Interactive OpenAPI / Swagger UI reverse-proxied through the gateway. |

---

## 4. Source-of-Truth Regulatory Policy

- **Primary Technical Source**: **OIML R 76-1:2006 (E)** *"Non-automatic weighing instruments - Part 1: Metrological and technical requirements - Tests"*.
- **Authoritative Rules**: Every compliance calculation, permissible error limit, and changeover evaluation is derived from verified clauses (Clauses 2, 3, A.4, A.5, A.6, Annex B, Annex G).
- **Turning Point Formula**: Changeover points calculated using $P = I + 0.5d - \Delta L$ with exact error determination $E = P - L$ and corrected error $E_c = E - E_0$.
- **No Silent Guessing**: Ambiguous or unconfigured requirements are explicitly surfaced with `"MANUAL REVIEW REQUIRED"` / `"NOT CONFIGURED"` statuses.
- **Explainability**: Every result displays its observed values, permissible limits ($MPE$), margin, formula, and exact OIML clause reference.

---

## 5. Demo Credentials & User Roles

| Email Address | Password | Role | System Permissions |
|---|---|---|---|
| `admin@metrireport.local` | `admin123` | **ADMIN** | Full administrative control, role assignment, rule toggles, finalization |
| `manager@metrireport.local` | `manager123` | **LAB_MANAGER** | Create/edit instruments, assign tests, approve workflow, rule inspection |
| `engineer@metrireport.local` | `engineer123` | **TEST_ENGINEER** | Execute test sessions, enter observations, upload evidence, draft reports |
| `reviewer@metrireport.local` | `reviewer123` | **REVIEWER** | Review calculations, add technical comments, approve/reject draft reports |
| `viewer@metrireport.local` | `viewer123` | **VIEWER** | Read-only access to repository, audit trails, and standards |

> **Note**: The login screen includes **1-Click Demo Account Switchers** with expressive interactive feedback and 100% offline fallback.

---

## 6. Getting Started (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at: `http://localhost:8000`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`

### Frontend Gateway Setup
```bash
cd frontend
npm install
node server.js
```
Frontend Web Application will be accessible at: `http://localhost:3000`

---

## 7. Running Automated QA Test Suite

To run all 32+ backend unit, boundary, calculation, compliance, security, and report generation tests:

```bash
cd backend
python3 -m pytest app/tests/ -v
```

---

## 8. Docker Compose Deployment

To build and run the complete multi-container stack in Docker:

```bash
docker compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:3000/docs` or `http://localhost:8000/docs`

---

## 9. SIH 2026 3–5 Minute Demonstration Workflow

1. **Login Screen**: Click **"Lead Engineer"** (or login with `engineer@metrireport.local` / `engineer123`).
2. **Dashboard**: View 8 KPI metrics, 3D Metrology Platform Scale Twin, and interactive Recharts.
3. **Launch Test Workspace**: Click **"Launch Test Workspace"** on Dashboard.
4. **Step 1 (Instrument)**: Choose the seeded `MW-3000 Electronic Platform Scale (Class III, Max=3000kg, e=1kg)`.
5. **Step 2 (Conditions)**: Inspect ambient conditions ($22.5^\circ\text{C}$, $54\%$ RH, $230\text{V AC}$) and proceed.
6. **Step 3 (Applicable Tests)**: View dynamic test selection (filtered by Class III & electronic specifications).
7. **Step 4 (Observations)**: Click **"1-Click Load Verified Demo Observations"** to populate real changeover weights ($\Delta L$) and explore the interactive **3D 5-Point Eccentricity Map**.
8. **Step 5 & 6 (Calculations & Compliance)**: Click **"Run Verified Calculations"** to trigger the Python Calculation Engine and view explainable compliance cards with exact OIML clauses and margins.
9. **Step 7 (Evidence)**: Upload high-resolution photographs with automated cryptographic **SHA-256 integrity hashing**.
10. **Step 8 (Review & Sign)**: Enter reviewer technical observations and click **"Generate Official PDF & DOCX"**.
11. **Step 9 (Report Export)**: Click **"Download Official PDF Report"** to view the Government of India format with crest, metrology tables, and disclaimers.
12. **Step 10 (Finalize)**: Click **"Finalize & Lock Report Immutability"** to permanently seal the report in the statutory repository.

---

## 10. Legal Metrology Disclaimer
> **IMPORTANT NOTICE:** METRIREPORT is a prototype system developed for SIH 2026. It generates compliance evaluation test reports strictly based on configured OIML R-76 requirements and does not falsely claim statutory Legal Metrology Model Approval certification under Section 22 of the Legal Metrology Act, 2009 without gazette notification.

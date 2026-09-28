# PRIVASCOPE

> **"Protect Before Your Data Leaves Your Device."**

PRIVASCOPE is an AI-assisted personal data firewall engineered to protect Indian personal identifiers and sensitive user data before it crosses network boundaries. Built on a zero-raw-cloud-exposure invariant, PRIVASCOPE inspects documents and outbound AI prompts locally, applying context-aware risk analysis, deterministic checksum validation, true PDF content-stream redaction, and reversible token pseudonymization.

---

## Features

- **Document Privacy Firewall (Mode A)**:
  - Multi-format inspection supporting PDF, DOCX, XLSX, CSV, TXT, PNG, and JPG.
  - True PDF content-stream redaction with zeroable text layer coordinates.
  - Coordinate heatmaps and high-resolution visual previews.
  - Format-preserving sanitization for spreadsheets (openpyxl) and documents (python-docx).
  - Context-aware sharing purpose engine across 8 real-world sharing contexts.
  - Binary magic-byte signature validation against disguised payloads.
- **AI Privacy Firewall & Gateway (Mode B)**:
  - Real-time outbound prompt interception and policy evaluation (`ALLOW`, `WARN`, `PROTECT`, `BLOCK`).
  - Reversible local pseudonymization substituting raw PII with typed tokens (`<AADHAAR_01>`, `<PHONE_01>`).
  - Volatile, session-scoped token vault ensuring zero raw PII reaches third-party AI providers.
  - Local browser token rehydration preserving user privacy during AI response interpretation.
  - Real-time network wire payload inspector comparing prompt text against wire transmission.
- **Indian Identifier Detection Engine**:
  - Aadhaar with Verhoeff checksum algorithm validation and consecutive digit rejection.
  - PAN card verification with fourth-character status checking.
  - Indian 10-digit mobile number detection with contextual proximity disambiguation.
  - UPI ID detection verified against payment service provider registries.
  - Bank account and IFSC code recognition with financial keyword proximity filtering.
  - Student identifier validation with educational context verification.
- **Production Authentication & Security**:
  - Dual authentication: Secure local credentials (bcrypt + JWT) and real Google Identity Services OpenID Connect.
  - Cryptographic server-side token signature verification via Google public keys.
  - Safe account linking by immutable Google Subject ID (`sub`) or verified email address.
  - Strict tenant user data isolation on all queries and storage operations.
  - PII-sanitizing logging formatter preventing accidental logging of sensitive identifiers.
  - Security headers including Content Security Policy (CSP), X-Frame-Options, and X-Content-Type-Options.

---

## Architecture

```
                    +------------------------------------+
                    |        CLIENT WEB BROWSER          |
                    |    React 18 + TypeScript + Vite    |
                    |    Google Identity Services (GIS)  |
                    +-----------------+------------------+
                                      |
                     HTTPS / REST API | (JWT Bearer Auth)
                                      v
                    +------------------------------------+
                    |        FASTAPI BACKEND CORE        |
                    |   Rate Limiter & Security Headers  |
                    |   User Isolation & Auth Middleware |
                    +--------+------------------+--------+
                             |                  |
            +----------------+                  +----------------+
            v                                                    v
[MODE A: DOCUMENT FIREWALL]                             [MODE B: AI GATEWAY]
  - File Validation (Magic Bytes)                         - Prompt Policy Engine
  - OCR Engine (Tesseract/EasyOCR)                        - Contextual Risk Analyzer
  - Format Redaction Engines                              - Pseudonymization Vault
  - Sharing Purpose Matrix                                - AI Provider Abstraction
            |                                                    |
            +----------------+                  +----------------+
                             |                  |
                             v                  v
                    +----------------+  +----------------+
                    | SQL DATABASE   |  | AI PROVIDERS   |
                    | PostgreSQL /   |  | OpenAI /       |
                    | SQLite (Dev)   |  | Anthropic /    |
                    | Alembic Schema |  | Gemini / Demo  |
                    +----------------+  +----------------+
```

---

## Frontend

The frontend is built with:
- **Framework**: React 18 with TypeScript 5.5 and Vite 8
- **Styling**: TailwindCSS with responsive dark cybersecurity theme
- **Animations**: Framer Motion with hardware acceleration and `prefers-reduced-motion` compliance
- **Icons**: Lucide React
- **Client Authentication**: Google Identity Services (`https://accounts.google.com/gsi/client`)

---

## Backend

The backend is built with:
- **Framework**: FastAPI with Pydantic v2 and Python 3.12
- **Database ORM**: SQLAlchemy 2.0 with Alembic migration versioning
- **Authentication**: PyJWT (HMAC-SHA256) and Passlib/Bcrypt
- **Document Processing**: PyMuPDF (fitz), python-docx, openpyxl, pandas, Pillow
- **Optical Character Recognition**: EasyOCR and Pytesseract
- **HTTP Client**: HTTPX for secure outbound AI provider calls

---

## Authentication

PRIVASCOPE provides two secure authentication methods:

1. **Local Authentication**:
   - Direct email/password registration with bcrypt password hashing.
   - Issues signed, time-limited JWT access tokens.
2. **Google OAuth 2.0 / OpenID Connect**:
   - Initiated via Google Identity Services in the browser.
   - The frontend receives an OpenID Connect ID token and transmits it to `POST /api/auth/google`.
   - The backend cryptographically validates the token signature, audience, issuer, expiration, and verified email using Google public key certificates.
   - Identity is resolved using the immutable Google `sub` identifier.
   - Safe Account Linking: If a user with a verified matching email already exists, their Google `sub` is safely linked. Otherwise, a new user account is created.
   - Rate limiting protects against brute force and abuse.

---

## Privacy Firewall

PRIVASCOPE's privacy engine executes a multi-layered analysis:
1. **Deterministic Pattern Extraction**: Regex matching with strict format specifications.
2. **Mathematical Validation**: Verhoeff checksum algorithm for Aadhaar; structure validation for PAN and IFSC.
3. **Context Intelligence**: Proximity-based heuristic filtering to suppress non-PII false positives (e.g., distinguishing a tracking ID or invoice number from a phone number).
4. **Risk Calculation**: Severity-weighted cumulative scoring with classification into `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.

---

## Document Firewall

Mode A protects sensitive documents prior to sharing:
- **Purpose Selection**: Select the intended sharing context (**Job Application**, **College Admission**, **Scholarship**, **Bank Verification**, **Medical Document**, **Government Form**, **General Sharing**, or **Custom**).
- **Contextual Recommendation Engine**: Analyzes each detected entity against the purpose policy to recommend `KEEP` (permitted for the specific purpose) or `PROTECT` (sensitive and unnecessary for the purpose).
- **Verified Protection**: Applies permanent redactions (solid pixel redactions on PDFs and images; cell/run level masks on Excel/Word) and runs an automated verification pass ensuring sensitive values no longer exist in the output artifact.

---

## AI Gateway

Mode B safeguards outbound AI interactions:
- **Policy Decision Matrix**:
  - `ALLOW`: Clean prompt without sensitive entities; passes through directly.
  - `WARN`: Advisory notice for low-sensitivity entities with user confirmation.
  - `PROTECT`: Reversible pseudonymization replacing raw values with tokens before outbound transmission.
  - `BLOCK`: Outbound transmission halted due to compound risk (e.g., simultaneous Aadhaar + Bank Account + Phone).
- **Local Pseudonymization**:
  - The external AI provider receives only sanitized tokens (e.g., `<AADHAAR_01>`).
  - Token-to-value mappings are held in server memory with automatic TTL expiration.
  - Tokens are rehydrated in the user's browser session after the AI provider responds.
- **Provider Abstraction**:
  - Supports `LocalDemoProvider` (air-gapped local test engine), `OpenAIProvider`, `AnthropicProvider`, and `GeminiProvider`.
  - When API keys are unconfigured, the system reports a clear configuration state without fabricating responses.

---

## Local Development

### Prerequisites
- Python 3.10 to 3.12
- Node.js 18+ and npm
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be accessible at:
- API Base: `http://127.0.0.1:8000/api`
- Health Check: `http://127.0.0.1:8000/health`
- OpenAPI Documentation: `http://127.0.0.1:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend will be accessible at `http://localhost:5173`.

---

## Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `ENV` | Application environment (`development` or `production`) | `development` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./privascope.db` |
| `JWT_SECRET` | Secret key for signing session JWTs (min 32 chars in production) | Cryptographic random string |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Session token validity duration in minutes | `1440` (24 hours) |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:5173,http://127.0.0.1:5173` |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Web Application Client ID | `YOUR_CLIENT_ID.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret | `YOUR_CLIENT_SECRET` |
| `DEFAULT_GATEWAY_PROVIDER`| Default AI provider (`local_demo`, `openai`, `anthropic`, `gemini`) | `local_demo` |
| `OPENAI_API_KEY` | Optional OpenAI API key | Blank |
| `ANTHROPIC_API_KEY` | Optional Anthropic API key | Blank |
| `GEMINI_API_KEY` | Optional Google Gemini API key | Blank |
| `MAX_UPLOAD_SIZE_MB` | Maximum allowed document upload size in megabytes | `25` |

### Frontend Configuration (`frontend/.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `VITE_API_URL` | Base URL of the backend API | `http://localhost:8000/api` |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth 2.0 Web Application Client ID | `YOUR_CLIENT_ID.apps.googleusercontent.com` |

---

## Database

- **Development**: SQLite (`sqlite:///./privascope.db`) is used for frictionless local development.
- **Production**: PostgreSQL (`postgresql://user:password@host:port/database`).
- **Migrations**: Database schema versioning is managed via Alembic:
  ```bash
  # Apply latest migrations
  alembic upgrade head
  
  # Create a new migration revision
  alembic revision --autogenerate -m "description_of_change"
  ```

---

## Deployment

### Render Deployment (Recommended)

PRIVASCOPE includes a pre-configured `render.yaml` blueprint defining:
1. **`privascope-api`**: FastAPI Web Service running on Python 3.12.
2. **`privascope-web`**: Static Site hosting the React production bundle.
3. **`privascope-db`**: Managed PostgreSQL database instance.

To deploy on Render:
1. Push repository to your Git provider (GitHub / GitLab).
2. Connect your repository to Render via **Blueprints** (`render.yaml`).
3. Set the required production environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

---

## Google OAuth Production Setup

To enable Google Sign-In for all external users in production:

1. Open [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Navigate to **APIs & Services** &rarr; **Credentials**.
3. Select your **OAuth 2.0 Client ID** (Application Type: *Web application*).
4. Under **Authorized JavaScript origins**, add your exact production frontend URL:
   - Example: `https://privascope.example.com`
   - For local development: `http://localhost:5173` and `http://127.0.0.1:5173`
   *(Do NOT include paths like `/login` or `/api/auth/google` in Authorized JavaScript origins)*.
5. In **OAuth consent screen**:
   - Set User Type to **External** so any standard Google account can sign in.
   - Configure basic application info (Application name, User support email).
   - Ensure scopes are set to minimum identity permissions: `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid`.
6. Add the Client ID to `frontend/.env` (`VITE_GOOGLE_CLIENT_ID`) and `backend/.env` (`GOOGLE_CLIENT_ID`).

---

## Security

- **Zero-Cloud-Exposure Invariant**: Sensitive data is inspected and sanitized locally before any network dispatch.
- **Content Security Policy (CSP)**: Restricts script execution and iframe origins to self and Google Identity Services.
- **Fail-Fast Security Validation**: In `ENV=production`, the server refuses to boot if `JWT_SECRET` is missing, insecure, or shorter than 32 characters.
- **User Data Isolation**: Every document, scan result, audit log, and gateway session is explicitly scoped to the authenticated user's ID.
- **PII-Scrubbed Logging**: Log formatters automatically mask Aadhaar, PAN, phone numbers, email addresses, and financial coordinates.
- **Rate Limiting**: Authentication endpoints are rate-limited by client IP to mitigate brute-force and credential-stuffing attacks.

---

## Limitations

- **OCR Quality**: Image and scanned PDF text extraction accuracy depends on document resolution, lighting, and scan clarity.
- **Contextual Heuristics**: While context heuristics substantially reduce false positives, uncommon phrasing or non-standard formatting may occasionally require manual user review.
- **Encrypted Files**: Password-protected PDFs and encrypted archives cannot be processed without the decryption passphrase.

---

## Project Structure

```
PRIVASCOPE/
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── components/       # UI components, layout, document viewer
│   │   ├── context/          # Authentication context & state
│   │   ├── pages/            # Core dashboard, scans, gateway, history, audit
│   │   ├── services/         # API client & HTTP abstraction
│   │   ├── types/            # TypeScript interfaces
│   │   ├── App.tsx           # Router configuration
│   │   └── main.tsx          # Application entrypoint
│   ├── .env.example          # Frontend configuration template
│   ├── index.html            # HTML shell with GIS client script
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   └── vite.config.ts        # Vite build configuration
│
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI router endpoints (auth, scans, docs, gateway)
│   │   ├── core/             # Configuration, database engine, rate limiting, logging
│   │   ├── db/               # Database session & base exports
│   │   ├── detectors/        # Indian PII detectors (Verhoeff, regex, heuristics)
│   │   ├── firewall/         # Policy engine & gateway service exports
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── processors/       # PDF, Excel, Word, CSV, Image redaction engines
│   │   ├── schemas/          # Pydantic request/response validation schemas
│   │   ├── services/         # Scan pipeline, pseudonymization, providers, OCR
│   │   ├── storage/          # Storage directory with uploads, protected, temp (.gitkeep)
│   │   └── main.py           # FastAPI application entrypoint
│   ├── migrations/           # Alembic database migrations
│   ├── .env.example          # Backend configuration template
│   ├── .python-version       # Python version specification (3.12.3)
│   ├── alembic.ini           # Alembic configuration
│   └── requirements.txt      # Python dependencies
│
├── .gitignore                # Comprehensive version control exclusions
├── render.yaml               # Cloud deployment blueprint
└── README.md                 # Project documentation
```

---

## License

This project is licensed under the MIT License. Built for privacy engineering, data protection, and secure AI enablement.

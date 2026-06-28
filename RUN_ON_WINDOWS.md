# Running BrokerAssist on Windows — step-by-step

This runs the app **mocks-first**: SQLite + in-memory cache + mock AI. **No API keys or credentials
needed.** You only need Python and Node installed.

The app has two parts that run at the same time in **two separate terminals**:

- **Backend** — FastAPI (Python) on `http://localhost:8200`
- **Frontend** — Next.js (Node) on `http://localhost:3000`

---

## 1. Install prerequisites (one time)

1. **Python 3.11** — https://www.python.org/downloads/
   During install, tick **"Add python.exe to PATH"**.
2. **Node.js 18+ (LTS)** — https://nodejs.org/
3. **Git** (optional, only if cloning) — https://git-scm.com/download/win

Verify in **PowerShell**:

```powershell
python --version    # should print 3.11.x
node --version      # should print v18+ or v20+/v22+
npm --version
```

> Use **PowerShell** (not the old `cmd`) for everything below. Open it from Start menu, or in the
> project folder: Shift + right-click → "Open PowerShell window here".

---

## 2. Get to the project folder

Your project is at `C:\Users\sethu\Downloads\AI bot`. The app lives in a sub-folder:

```powershell
cd "C:\Users\sethu\Downloads\AI bot\deliverables\phase_2\brokerassist"
```

### Remove the old Mac build folders (do this once)

This folder was last run on a Mac, so it contains a Python environment and a Next.js build that
**won't work on Windows**. Delete them so Windows rebuilds fresh — paste this whole block:

```powershell
Remove-Item -Recurse -Force ".\apps\backend\.venv" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\apps\frontend\.next" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\apps\frontend\node_modules" -ErrorAction SilentlyContinue
Remove-Item -Force ".\apps\backend\brokerassist.db" -ErrorAction SilentlyContinue
Write-Host "Cleaned - ready for a fresh Windows setup." -ForegroundColor Green
```

---

## 3. Start the BACKEND (Terminal 1)

```powershell
cd "C:\Users\sethu\Downloads\AI bot\deliverables\phase_2\brokerassist\apps\backend"

# create + activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt
```

> **If `Activate.ps1` is blocked** with a script-execution error, run this once, then retry activate:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

Now set the **mocks-first** environment variables (these override the `.env` file, which is pointed at
live vendors), then start the server:

```powershell
$env:BA_USE_MOCKS = "true"
$env:BA_INGEST_LIVE = "false"
$env:BA_EMBEDDING_PROVIDER = "mock"
$env:BA_DATABASE_URL = "sqlite:///./brokerassist.db"

uvicorn app.main:app --port 8200
```

Leave this terminal running. Check it works — open these in a browser:

- http://localhost:8200/health  → `{"status":"ok","use_mocks":true,...}`
- http://localhost:8200/docs    → interactive API page

**Optional — run the test suite** (in the same activated venv, before starting uvicorn):

```powershell
pytest -q     # expect: 142 passed
```

---

## 4. Start the FRONTEND (Terminal 2)

Open a **second** PowerShell window (keep the backend running in the first):

```powershell
cd "C:\Users\sethu\Downloads\AI bot\deliverables\phase_2\brokerassist\apps\frontend"

npm install

$env:NEXT_PUBLIC_API_BASE = "http://localhost:8200"
$env:NEXT_PUBLIC_WIDGET_KEY = "demo-public-key"

npm run dev
```

Then open **http://localhost:3000** in your browser.

Pages to try: `/`, `/stock-research`, `/algo-education`, `/nalco`. Click the **Ask** assistant and send
a question like *"NALCO dividend?"* — you should get an answer with citations and an
"informational only — not investment advice" disclaimer.

---

## 5. Stopping / restarting

- Stop either server with **Ctrl + C** in its terminal.
- Next time, you don't reinstall. Just reactivate and run:
  - **Backend:** `cd ...\apps\backend` → `.\.venv\Scripts\Activate.ps1` → set the 4 `$env:` vars → `uvicorn app.main:app --port 8200`
  - **Frontend:** `cd ...\apps\frontend` → set the 2 `$env:` vars → `npm run dev`

> The `$env:` variables only last for that terminal session, so set them again each time (or put them
> in the `.env` / `.env.local` files — see note below).

---

## Optional: make settings permanent via .env files

Instead of setting `$env:` vars each time:

- **Backend** — edit `apps\backend\.env` and change:
  ```
  BA_USE_MOCKS=true
  BA_INGEST_LIVE=false
  BA_EMBEDDING_PROVIDER=mock
  ```
  (The shipped `.env` has these set for live vendors with real API keys. For a credential-free local
  run, the three values above are all you need.)

- **Frontend** — create `apps\frontend\.env.local` with:
  ```
  NEXT_PUBLIC_API_BASE=http://localhost:8200
  NEXT_PUBLIC_WIDGET_KEY=demo-public-key
  ```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python` not found | Reinstall Python with "Add to PATH" ticked, reopen PowerShell. |
| `Activate.ps1 cannot be loaded` | Run the `Set-ExecutionPolicy` command in step 3. |
| Backend chat returns 500 about "Ollama"/"proxy" | You're hitting live vendors — make sure `BA_USE_MOCKS=true` **and** `BA_EMBEDDING_PROVIDER=mock` are set in that terminal. |
| `pip install` fails on a package | Confirm you're on Python 3.11 (`python --version`); 3.13 can break some pinned deps. |
| Frontend can't reach backend | Confirm backend is running on 8200 and `NEXT_PUBLIC_API_BASE=http://localhost:8200`. |
| Port already in use | Change the port: `uvicorn app.main:app --port 8201` (and update `NEXT_PUBLIC_API_BASE`), or `npm run dev -- -p 3001`. |

---

## Security note

The committed `apps\backend\.env` contains **real vendor API keys in plaintext** (Ollama, Jina,
Sarvam). The mocks-first steps above never use them. If these keys are real and active, consider
rotating them and keeping `.env` out of version control.

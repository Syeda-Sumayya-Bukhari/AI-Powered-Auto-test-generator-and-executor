# Free AI Providers — Step-by-Step Setup

Use this guide to switch from **mock** (offline) to a **free live AI** that generates real test cases.

---

## Quick comparison

| Provider | Cost | API key? | Internet? | Best for |
|----------|------|----------|-----------|----------|
| **mock** | Free | No | No | Assignment demo (default) |
| **Gemini** | Free tier | Yes (free) | Yes | Easiest free cloud AI |
| **Groq** | Free tier | Yes (free) | Yes | Fast responses |
| **Ollama** | Free | No | No* | Runs on your PC |
| **OpenAI** | Paid | Yes | Yes | If you have credits |

\*Ollama runs locally; no cloud API key needed.

---

## Before you start (all providers)

1. Open project in VS Code: `AI_Test_Automation_Project`
2. Open terminal (**Ctrl+`**)
3. Run:

```powershell
cd "c:\Users\Sumayya PC\Desktop\AI_Test_Automation_Project"
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

4. Edit `.env` — only change the provider you want (see below)

5. Run:

```powershell
python main.py "Test login page"
```

Terminal will show: `AI provider: gemini` (or groq, ollama, mock)

---

## Option A — Google Gemini (recommended, free)

### Step 1: Get free API key

1. Open https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click **Create API key**
4. Copy the key

### Step 2: Configure `.env`

Open `.env` and set:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=paste_your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### Step 3: Install Gemini library

```powershell
pip install google-generativeai
```

### Step 4: Run

```powershell
python main.py "Test login page"
```

You should see AI-generated scenarios (may differ from mock each time).

---

## Option B — Groq (free, fast)

### Step 1: Get free API key

1. Open https://console.groq.com/
2. Sign up (free)
3. Go to **API Keys** → **Create API Key**
4. Copy the key

### Step 2: Configure `.env`

```env
AI_PROVIDER=groq
GROQ_API_KEY=paste_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### Step 3: Run

```powershell
python main.py "Test login page"
```

No extra package needed (uses `openai` library with Groq endpoint).

---

## Option C — Ollama (100% free, local, no API key)

### Step 1: Install Ollama

1. Download: https://ollama.com/download
2. Install for Windows
3. Ollama runs in background after install

### Step 2: Download a model

Open **new** terminal:

```powershell
ollama pull llama3.2
```

Wait until download completes.

### Step 3: Configure `.env`

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Step 4: Run

```powershell
python main.py "Test login page"
```

**If error "Cannot reach Ollama":**
- Open Ollama app from Start menu, or run `ollama serve` in terminal
- Then try again

---

## Option D — Mock (no key, for assignment)

```env
AI_PROVIDER=mock
```

No API key. Built-in login test cases. **Use this if you have no credits.**

---

## Switching providers

Only change **one line** in `.env`:

```env
AI_PROVIDER=gemini
```

Then save and run `python main.py "Test login page"` again.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `GEMINI_API_KEY is not set` | Paste key in `.env`, set `AI_PROVIDER=gemini` |
| `GROQ_API_KEY is not set` | Paste key in `.env`, set `AI_PROVIDER=groq` |
| `Cannot reach Ollama` | Install Ollama, run `ollama pull llama3.2`, start Ollama app |
| Falls back to mock | API failed — check key, internet, or quota; mock still runs tests |
| Invalid JSON from AI | Run again; or use `AI_PROVIDER=mock` for stable output |

---

## For your assignment report

Example paragraph:

> We integrated multiple AI backends (Google Gemini, Groq, Ollama, OpenAI) via a provider abstraction in `src/ai_providers.py`. For demonstration without paid API credits, we used `AI_PROVIDER=mock` with a built-in fallback. Live AI generation was verified using [Gemini / Groq / Ollama — pick what you used].

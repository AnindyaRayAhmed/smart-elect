<div align="center">
  <br />
    <h1 align="center">SmartElect</h1>
    <p align="center"><b>A Deterministic Civic Engine. Zero Hallucinations. Immutable Workflows.</b></p>
  <br />
</div>

<p align="center">
  Chatbots guess. SmartElect guides. <br/>
  It strips away the conversational fluff of modern AI wrappers and replaces it with <b>State-Machine Precision</b>. <br/>
  No ambiguous advice. Just clear, authoritative civic guidance, reliable information, and simple next steps.
</p>

---

## ⚡ The 10-Second Pitch (Why This Wins)

- **It is Approachable but Structured:** Users state what they need, and the system provides a predefined, verified guide.
- **It is Politically Neutral:** Core Safety Guidelines handle subjective requests (e.g., "who to vote for") by offering an objective Candidate Evaluation Guide.
- **It Encourages Action:** Clear guidance is paired with a specific 'Next step' and a one-click `.ics` integration to add deadlines to the user's calendar.
- **It Builds Trust:** The UI is clean, modern, and structured to feel like a secure, reliable civic tool rather than just a chatbot.

## 🎬 The "Lock-In" Demo Flow

This is the exact sequence that proves dominance:

1. **The Request:** The user inputs *"How do I register to vote?"*
2. **Processing:** Instead of a generic typing indicator, the system shows 'Processing your request...' in a structured format.
3. **The Reveal:** The interface locks into a strict dual-pane HUD.
4. **The Metadata:** The left pane exposes the system's thought process: `Target Intent: registration_help | Confidence Interval: 96% | Primary Data Source: NVSP Portal`. Absolute transparency.
5. **The Guide:** The right pane delivers clear, step-by-step instructions.
6. **The Real-World Hook:** At the bottom, a 'Next step' guides document assembly, alongside an **Add to Calendar** button that instantly drops a reminder.

## 🏛 Architecture (Pure Signal, Zero Noise)

SmartElect achieves maximum impact with zero bloat. It requires **no external dependencies** beyond FastAPI and Pydantic.

- **`routers/`**: Pydantic-enforced API contracts. Invalid queries are instantly rejected with a 422 JSON trap.
- **`core/security.py`**: The immutable safety layer. It mathematically neutralizes biased adjectives before they render.
- **`services/`**: The deterministic decision engine. Every output guarantees a `title`, `content`, `confidence`, and `next_step`.

## 🚀 Deployment Protocol

```bash
# 1. Initialize environment
pip install -r requirements.txt

# 2. Ignite the engine
uvicorn app.main:app --reload

# 3. Access the application
Navigate to http://localhost:8000/
```

## 🚀 Deployment Guide (Local + Google Cloud Run)

---

### 🖥️ Run Locally

#### Prerequisites
- Python 3.10+
- pip
- Gemini API Key (Google AI Studio)

---

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/smart-elect.git
cd smart-elect
```

---

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

#### 3. Set Environment Variables

**Windows (PowerShell):**
```bash
$env:GOOGLE_API_KEY="your_api_key_here"
$env:LLM_ENABLED="true"
$env:LLM_PROVIDER="gemini"
```

**Mac/Linux:**
```bash
export GOOGLE_API_KEY="your_api_key_here"
export LLM_ENABLED="true"
export LLM_PROVIDER="gemini"
```

---

#### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Open in browser:
```
http://localhost:8000
```

---

### ☁️ Deploy to Google Cloud Run

#### Prerequisites
- Google Cloud account
- Billing enabled
- gcloud CLI installed

---

#### 1. Authenticate & Set Project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

---

#### 2. Enable Required Services

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

#### 3. Deploy to Cloud Run

```bash
gcloud run deploy smartelect \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated
```

---

#### 4. Set Environment Variables (IMPORTANT)

After deployment:

- Go to Cloud Run Console
- Open your service → Edit & Deploy New Revision
- Add the following variables:

```
GOOGLE_API_KEY=your_api_key_here
LLM_ENABLED=true
LLM_PROVIDER=gemini
```

- Click Deploy

---

#### 5. Access the Application

Cloud Run will provide a public URL:

```
https://smartelect-xxxxx.run.app
```

Open it in your browser.

---

### 🧪 Quick Test

**Explore Mode:**
- Explain voting like a pizza party
- Write a short poem about elections

**Guided Mode:**
- I am 25, Indian, from Kolkata

---

### ⚠️ Notes

- Uses Gemini 2.5 Flash Lite via google-genai
- Guided Mode → Deterministic engine + LLM interpretation
- Explore Mode → Fully LLM-driven responses
- Ensure API key is valid and has quota available


---
<div align="center">
  <b>SmartElect</b> • <i>Clear, confident civic guidance.</i>
</div>


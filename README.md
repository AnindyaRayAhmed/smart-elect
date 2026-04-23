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

---
<div align="center">
  <b>SmartElect</b> • <i>Clear, confident civic guidance.</i>
</div>

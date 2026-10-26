# PRAVAHA: AI-Powered Multilingual Crisis Intelligence System

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Ayush-Mishra6343/PRAVAH)

PRAVAHA transforms fragmented, multilingual emergency reports into structured incidents, groups cross-lingual evidence, explicitly surfaces conflicting claims, tracks relief supply inventory, and generates traceable recommendations with human-in-the-loop oversight.

---

## 🌟 Live Sarvam AI Sovereign Integration
- **LLM Reasoning & Structured Incident Extraction:** `sarvam-105b-conversations`
- **Real-Time Indic Translation & Normalization:** `mayura:v1`
- **Supported Languages (10):** Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi.
- **Resilient Fallback & Key Failover:** Automatic key rotation on quota exhaustion, plus deterministic crisis NLP fallback.

---

## 🚀 1-Click Render Deployment
Click the button above or visit:
**[Deploy on Render](https://render.com/deploy?repo=https://github.com/Ayush-Mishra6343/PRAVAH)**

- **Environment:** Python
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Environment Variable:** Set `SARVAM_API_KEY`

---

## 💻 Local Launch

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Sarvam API Key to .env
# SARVAM_API_KEY=your_key_here

# 3. Launch application
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

# PRAVAHA: AI-Powered Multilingual Crisis Intelligence System

PRAVAHA transforms fragmented, multilingual emergency reports into structured incidents, groups cross-lingual evidence, explicitly surfaces conflicting claims, tracks relief supply inventory, and generates traceable recommendations with human-in-the-loop oversight.

---

## 🌟 Live Sarvam AI Sovereign Integration
- **LLM Reasoning & Structured Incident Extraction:** `sarvam-105b-conversations`
- **Real-Time Indic Translation & Normalization:** `mayura:v1`
- **Supported Languages (10):** Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi.
- **Resilient Fallback:** Automatically switches to a deterministic crisis NLP engine if network, quota, or rate-limits occur, with transparent indicator badges.

---

## 🚀 Quick Local Launch

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Sarvam API Key to .env
# SARVAM_API_KEY=your_key_here

# 3. Launch application
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 🧪 Verification & Acceptance Testing

Run the automated verification suite:
```bash
python test_system.py
```
This tests:
1. Multilingual report ingestion (Hindi, Bengali, Tamil, English at same Government School).
2. Canonical entity resolution & corroboration into `INC-001`.
3. Non-merging of distinct geographic locations (Rampur Village preserved as `INC-002`).
4. Contradictory road access claims surfaced with route warnings.
5. Simulated relief inventory allocations and capacity deductions.
6. Unified summary translation into operator-selected Indian languages.
7. Graceful fallback mode toggle.

---

## ☁️ Public Deployment Options

### Option 1: Render / Railway (Recommended)
1. Push this repository to GitHub.
2. In Render / Railway, select **Web Service**.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Environment Variable: `SARVAM_API_KEY`

### Option 2: Docker Container
```bash
docker build -t pravaha .
docker run -p 8000:8000 -e SARVAM_API_KEY=your_key pravaha
```

# KisaanGPT — Your AI Agriculture Assistant

KisaanGPT is a premium AI-powered crop advisory platform for Tamil Nadu farmers. It features an "Apple-esque" minimalist design, multi-agent reasoning, machine learning crop predictions, voice AI, and a persistent digital twin of your farm.

---

## 🚀 Key Features

-   **Intelligent Soil Analysis:** Precise crop recommendations based on NPK, pH, and environmental data.
-   **Farm Digital Twin:** Detailed history of soil health readings over time with trajectory analysis.
-   **AI Chat Assistant:** Combined RAG (Research-Augmented Generation) and Text-to-SQL for querying agricultural guidelines and farm data.
-   **Multi-Language UI:** Fully localized English and Tamil interface with instant switching.
-   **Voice Advisory:** Tamil/English Speech-to-Text and Text-to-Speech integration.
-   **Regional Benchmarking:** Compare your farm's health against Tamil Nadu district averages.

---

## 🛠️ Tech Stack

-   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
-   **Frontend:** [React](https://reactjs.org/) + [Vite](https://vitejs.dev/)
-   **Styling:** Clean Vanilla CSS with Apple-inspired frosted glass effects.
-   **Visualization:** [Recharts](https://recharts.org/) (Timeline charts & Radar confidence meters).
-   **Database:** [Supabase](https://supabase.com/) (pgvector for RAG, PostgreSQL for farm records).
-   **AI Models:** RandomForest (Crop/Fertilizer ML), OpenAI Whisper (STT), Google TTS, and Groq/OpenAI (LLM).

---

## 📦 Getting Started

### 1. Configure Environment
Create a `.env` file in the project root with the following:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
```

### 2. Manual Data Setup (One-time)
1. Run `supabase_setup.sql` in your Supabase SQL Editor.
2. Place crop datasets in `data/raw/`.
3. Train ML models: `python models/train_crop_model.py`.
4. Build RAG: `python rag/build_knowledge_base.py`.

### 3. Run the Backend
The backend serves the AI logic and also powers the auto-training lifecycle on startup.
```bash
# From project root
uvicorn backend.main:app --reload --port 8000
```

### 4. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 📂 Project Structure

```
kisaangpt/
├── backend/            # FastAPI application (main.py, routers)
├── frontend/           # React application (Vite structure)
│   ├── src/            # App.jsx, i18n.js, css
│   └── public/         # logo.png, assets
├── agents/             # 6-agent modular pipeline
├── models/             # ML training and model artifacts (.pkl)
├── memory/             # Supabase data persistence (Digital Twin)
├── rag/                # Vector search knowledge base
├── voice/              # Audio transcription & speech synthesis
└── data/               # Raw datasets for training
```

---

## 🚂 Deployment: Railway

The project is pre-configured for **Railway** deployment.
-   **Strategy:** Single-service deployment.
-   **Process:** The FastAPI server build script automates the React build (`npm install && npm run build`) and serves the static files from `frontend/dist`.
-   **Auto-training:** If ML model files are missing on the server, the FastAPI `lifespan` triggers training automatically on boot.

---

## 🎓 Academic / Theme Implementation

| Theme | Details |
| :--- | :--- |
| **Prompt Engineering** | SynthesisAgent with structural constraints, anti-hallucination, and regional context. |
| **RAG** | ICAR/TNAU document vector searching via Supabase pgvector. |
| **AI Agents** | Orchestrator-led flow: Soil Analyst → ML Predictor → RAG → Synthesis. |
| **Voice AI** | Bilingual (Tamil/English) STT/TTS loop for accessibility. |
| **Model Parity** | RandomForest ensemble achieving ≈99.3% accuracy for regional crop fitness. |

"# Kisaan-GPT" 
"# Kisaan-gpt"

# KisaanGPT — Your AI Agriculture Assistant

AI-powered crop advisory system for Tamil Nadu farmers. Combines machine learning,
RAG (Supabase pgvector), multi-agent reasoning, voice AI, and a farm digital twin.

---

## Quick Start

### 1. Clone & install
```bash
git clone <your-repo>
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env
# Edit .env — fill in all 4 keys
```

### 3. Supabase one-time setup
1. Create a free project at https://supabase.com
2. Open **SQL Editor** and run the entire contents of `supabase_setup.sql`
3. Copy your **Project URL** and **service_role key** from Settings → API into `.env`

### 4. Download datasets
| Dataset | Source | Save to |
|---------|--------|---------|
| Crop Recommendation (Atharva Ingle) | kaggle.com/datasets/atharvaingle/crop-recommendation-dataset | `data/raw/crop_recommendation.csv` |
| Fertilizer Prediction | kaggle.com/datasets/gdabhishek/fertilizer-prediction | `data/raw/fertilizer_prediction.csv` |

### 5. Train ML models
```bash
python models/train_crop_model.py
```
This trains and compares 5 models, selects the best (RandomForest ~99%), and saves:
- `models/crop_model.pkl`
- `models/fertilizer_model.pkl`
- `models/model_metadata.json`

### 6. Build RAG knowledge base
```bash
python rag/build_knowledge_base.py
```
This chunks 5 ICAR/TNAU documents, embeds them with `all-MiniLM-L6-v2`,
and uploads to Supabase. Then go to Supabase SQL Editor and run:
```sql
CREATE INDEX rag_embedding_idx ON rag_documents
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 7. Run the app
```bash
streamlit run app.py
```

---

## Project Structure

```
kisaangpt/
├── app.py                          Main Streamlit application
├── requirements.txt
├── supabase_setup.sql              One-time DB setup script
├── .env.example
│
├── agents/
│   ├── orchestrator.py             Master pipeline coordinator
│   ├── soil_analyst_agent.py       Threshold-based soil health checker
│   ├── crop_predictor_agent.py     ML inference (RandomForest)
│   ├── rag_retriever_agent.py      Supabase pgvector retriever
│   ├── weather_agent.py            OpenWeatherMap integration
│   ├── fertilizer_agent.py         ICAR-calibrated dose calculator
│   └── synthesis_agent.py          Claude LLM final advisory
│
├── rag/
│   ├── supabase_client.py          Singleton Supabase client
│   ├── build_knowledge_base.py     Chunk → embed → upload pipeline
│   └── documents/                  ICAR & TNAU source documents
│       ├── icar_soil_health_guidelines.txt
│       ├── icar_fertilizer_recommendations.txt
│       ├── tnau_crop_guide_kharif.txt
│       ├── tnau_crop_guide_rabi.txt
│       └── soil_health_thresholds.txt
│
├── models/
│   ├── train_crop_model.py         Training + 5-model comparison script
│   ├── crop_model.pkl              Saved RandomForest (after training)
│   ├── fertilizer_model.pkl        Saved fertilizer classifier
│   └── model_metadata.json         Thresholds, crop classes, accuracy
│
├── memory/
│   └── farm_twin.py                Supabase CRUD for farm digital twin
│
├── voice/
│   ├── transcriber.py              Whisper STT (Tamil/English)
│   └── speaker.py                  gTTS TTS (Tamil/English)
│
└── data/
    └── raw/                        Place downloaded CSVs here
```

---

## ML Models Used

| Model | Purpose | Accuracy |
|-------|---------|---------|
| RandomForest (200 trees) | Crop prediction — primary | ~99.3% |
| GradientBoosting | Compared, not deployed | ~98.5% |
| SVM (RBF kernel) | Compared, not deployed | ~97.8% |
| KNN (k=5) | Compared, not deployed | ~97.2% |
| Naive Bayes | Compared, not deployed | ~90.4% |
| RandomForest (100 trees) | Fertilizer prediction | ~96% |
| SentenceTransformer (MiniLM-L6) | RAG embeddings (384-dim) | — |

---

## Mandatory Theme Coverage

| Theme | Implementation |
|-------|---------------|
| Prompt Engineering | `SynthesisAgent` — structured system prompt with anti-hallucination rules, citation requirements, language control, and response format constraints |
| RAG | Supabase pgvector + `all-MiniLM-L6-v2` on 5 ICAR/TNAU documents. `match_documents` RPC with cosine similarity threshold. Retrieved chunks are injected into synthesis prompt. |
| Voice AI | OpenAI Whisper STT (Tamil + English) + Google TTS. Full voice loop in Tab 3. |
| AI Agents | 6-agent pipeline: Soil Analyst → Crop Predictor → RAG Retriever → Weather → Fertilizer → Synthesis, all coordinated by Orchestrator. |

---
"# Kisaan-GPT" 
"# Kisaan-gpt" 

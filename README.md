# PitchIQ — AI Football Intelligence Platform

An AI-powered football player analysis system for amateur and developing players.

## Features
- **Position Prediction** — ML ensemble (Random Forest, KNN, SVM, Neural Network) predicts top 5 positions with confidence scores
- **Gap Analysis** — Compares player stats against ideal position profiles derived from 51,878 real FIFA players
- **Player Clustering** — K-Means finds similar players by playing style from 51,878 real FIFA player profiles
- **Training Plans** — Personalized weekly plans generated from gap data
- **Session History** — Save and revisit past analyses
- **Model Metrics** — View accuracy, F1, precision and recall for all 5 classifiers

## Dataset
- **Source**: `male_players.csv` — real FIFA player data
- **Size**: 51,878 unique player profiles (11 positions)
- **Attributes**: pace, shooting, passing, dribbling, defending, physical, stamina, strength, agility, vision

## Quick Start

### 1. Train the ML models (run once)
```bash
pip install -r requirements.txt
python ml_models/training/train_classifier.py
```

### 2. Start the backend
```bash
python backend/app.py
```
API runs at `http://localhost:5000`

### 3. Start the frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict/positions` | Predict top 5 positions |
| POST | `/api/predict/gap-analysis` | Gap analysis for a position |
| POST | `/api/predict/full` | Full pipeline in one call + saves session |
| POST | `/api/training/plan` | Generate training plan |
| POST | `/api/analytics/overview` | Full player overview |
| POST | `/api/cluster/similar` | Find similar players |
| POST | `/api/cluster/info` | Cluster information |
| GET  | `/api/evaluate/models` | All 5 model metrics |
| GET  | `/api/evaluate/models/<name>` | Single model metrics |
| GET  | `/api/evaluate/confusion-matrix/<name>` | Confusion matrix |
| GET  | `/api/sessions/` | List saved sessions |
| GET  | `/api/sessions/<token>` | Get a session |
| GET  | `/api/health` | Health check |

## Model Performance (trained on 51,878 real FIFA players)

| Model | Accuracy | F1 Score |
|-------|----------|----------|
| Neural Network (MLP) ⭐ Best | **85.87%** | **85.99%** |
| Random Forest | 81.10% | 81.18% |
| Decision Tree | 80.38% | 80.76% |
| SVM | 76.39% | 76.75% |
| Gradient Boosting | 75.57% | 75.70% |
| KNN | 73.56% | 73.00% |

## Tech Stack
- **Frontend**: React 18, Vite, Recharts, CSS Modules
- **Backend**: Flask, Flask-CORS, SQLite
- **ML**: scikit-learn (Random Forest, KNN, SVM, Neural Network, K-Means)
- **Data**: 51,878 real FIFA player profiles from male_players.csv

# PitchIQ — Project Technical Report

---

**Project Name:** PitchIQ — AI-Powered Football Player Analysis System  
**Version:** 2.0.0  
**Type:** Machine Learning + Full-Stack Web Application  
**Dataset:** male_players.csv — 51,878 real FIFA player profiles  
**Models Trained:** KNN, Decision Tree, Random Forest, SVM, Neural Network (MLP), K-Means  
**Best Classifier:** Neural Network (MLP) — F1: 65.10% | Accuracy: 66.56%  
**Backend:** Python 3.13 + Flask 3.0  
**Frontend:** React 18 + Vite 5  
**Database:** SQLite  
**Test Coverage:** 52 automated tests — 100% pass rate  

---

## Executive Summary

PitchIQ is a football intelligence platform built for amateur and developing players who lack access to professional performance profiling. The system accepts 10 player attribute ratings (pace, shooting, passing, dribbling, defending, physical, stamina, strength, agility, vision) and applies machine learning to deliver four core outputs:

1. **Position Prediction** — Top-5 suitable positions with confidence scores, using an ensemble of 5 trained classifiers
2. **Gap Analysis** — Per-attribute comparison against ideal position profiles derived from 51,878 real FIFA players
3. **Player Similarity** — K-Means clustering and cosine similarity to find real players with matching playing styles
4. **Training Plans** — Personalised weekly drill schedules targeting the player's identified weaknesses

The system was trained on real FIFA player data (`male_players.csv`, 180,021 raw rows cleaned to 51,878 unique profiles) and achieves 66.6% accuracy on an inherently ambiguous 11-class position prediction problem. The Neural Network (MLP) was selected as the production model based on its highest weighted F1 score (65.10%) across all 11 positions.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
   - 2.1 Frontend
   - 2.2 Backend
   - 2.3 Database
   - 2.4 Machine Learning Stack
3. [Dataset](#3-dataset)
   - 3.1 Feature Engineering
   - 3.2 Position Distribution
   - 3.3 Position Profiles (75th Percentile)
4. [Classifiers Used](#4-classifiers-used)
   - 4.1 K-Nearest Neighbours
   - 4.2 Decision Tree
   - 4.3 Random Forest
   - 4.4 Support Vector Machine
   - 4.5 Neural Network (MLP)
5. [Classifier Performance Comparison](#5-classifier-performance-comparison)
6. [Clustering — K-Means](#6-clustering--k-means)
7. [Preprocessing Pipeline](#7-preprocessing-pipeline)
8. [API Design](#8-api-design)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Key Design Decisions & Trade-offs](#10-key-design-decisions--trade-offs)
11. [Limitations & Future Work](#11-limitations--future-work)
12. [Project Folder Structure](#12-project-folder-structure)
13. [System Architecture](#13-system-architecture)
14. [Data Flow — Full Analysis Request](#14-data-flow--full-analysis-request)
15. [Gap Analysis Methodology](#15-gap-analysis-methodology)
16. [Training Plan Methodology](#16-training-plan-methodology)
17. [Testing](#17-testing)
18. [Deployment Instructions](#18-deployment-instructions)
19. [Per-Position Classifier Analysis](#19-per-position-classifier-analysis)
20. [Conclusion](#20-conclusion)
21. [Appendix — API Reference](#21-appendix--api-reference)
22. [Appendix — Attribute Definitions](#22-appendix--attribute-definitions)
23. [Appendix — Position Abbreviations](#23-appendix--position-abbreviations)

---

**Purpose:** Help amateur and developing football players understand their strengths, suitable positions, and training priorities through data-driven analysis.

---

## 1. Project Overview

PitchIQ is a football intelligence platform that takes a player's attribute ratings (pace, shooting, passing, etc.) and uses machine learning to:

- Predict the top 5 most suitable playing positions with confidence scores
- Perform gap analysis by comparing the player's stats against ideal position profiles
- Find similar real-world players using K-Means clustering and cosine similarity
- Generate personalised weekly training plans based on identified weaknesses
- Persist analysis sessions for future reference

The system was built for players who do not have access to professional performance profiling — it democratises data-driven football analysis.

---

## 2. Technology Stack

### 2.1 Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 18.2 | UI component framework |
| Vite | 5.0 | Build tool and dev server |
| React Router DOM | 6.22 | Client-side routing |
| Recharts | 2.10 | Data visualisation (radar, bar, pie charts) |
| Axios | 1.6 | HTTP client for API calls |
| React Icons | 5.0 | Icon library |
| CSS Modules | — | Scoped component styling |

**Why React?**  
React's component model maps cleanly to the UI structure — each analysis section (predictions, gap analysis, training plan) is an independent component with its own state. The virtual DOM ensures smooth re-renders when attribute sliders update in real time.

**Why Vite?**  
Vite's native ES module dev server starts in under 300ms and provides HMR (Hot Module Replacement) without configuration. It also handles the `/api` proxy to the Flask backend during development.

**Why Recharts?**  
Recharts is built on top of D3 but exposes a React-native API. It handles responsive containers natively, which is critical for the radar chart (attribute profile) and bar chart (classifier comparison) components.

---

### 2.2 Backend

| Technology | Version | Purpose |
|---|---|---|
| Flask | 3.0 | REST API framework |
| Flask-CORS | 4.0 | Cross-origin request handling |
| Python | 3.13 | Runtime |
| python-dotenv | 1.0 | Environment variable management |
| SQLite (built-in) | — | Session persistence database |
| joblib | 1.3 | Model serialisation/deserialisation |

**Why Flask?**  
Flask is lightweight and does not impose an ORM or project structure. For a machine learning API where the heavy lifting is done by scikit-learn, Flask's minimal overhead is ideal. It starts in milliseconds and the Blueprint system keeps routes organised by domain (prediction, clustering, training, analytics, evaluation, sessions).

**Architecture pattern used:** Routes → Controllers → Services → ML Models  
Routes are thin (validate input, call controller, return JSON). Controllers contain business logic. Services wrap the ML layer. This separation means the ML models can be swapped without touching routes.

---

### 2.3 Database

**Database used: SQLite**

SQLite was chosen for the following reasons:

1. **Zero configuration** — no server process, no connection string, no installation. The database is a single file (`backend/database/pitchiq.db`).
2. **Appropriate scale** — PitchIQ is a single-user or small-team tool. SQLite handles thousands of concurrent reads efficiently for this use case.
3. **Portability** — the entire database travels with the project folder. No external dependency to set up when deploying or sharing.
4. **Python built-in** — Python's `sqlite3` module is part of the standard library, adding zero dependencies.

**What is stored:**  
The `analysis_sessions` table stores every full analysis run — player name, age, all 10 attribute values, and the JSON results (predictions, gap analysis, training plan, cluster info). This allows users to revisit past analyses via the Sessions page.

**Schema:**
```sql
CREATE TABLE analysis_sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    session_token TEXT    NOT NULL UNIQUE,   -- UUID
    player_name   TEXT    NOT NULL DEFAULT 'Anonymous',
    player_age    INTEGER,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    pace, shooting, passing, dribbling, defending,
    physical, stamina, strength, agility, vision  -- INTEGER 1-99
    predictions   TEXT,   -- JSON
    gap_analysis  TEXT,   -- JSON
    training_plan TEXT,   -- JSON
    cluster_info  TEXT    -- JSON
);
```

**Why not PostgreSQL or MongoDB?**  
PostgreSQL would be appropriate if PitchIQ were a multi-user SaaS product with concurrent writes. MongoDB would suit a schema-less document store. Neither is necessary here — the data model is fixed (10 attributes + JSON blobs) and the user base is local/single-user.

---

### 2.4 Machine Learning Stack

| Library | Version | Purpose |
|---|---|---|
| scikit-learn | 1.3.2 | All classifiers, scaler, label encoder, K-Means |
| pandas | 2.1.4 | Data loading, cleaning, feature engineering |
| numpy | 1.26.2 | Numerical operations |
| joblib | 1.3.2 | Model persistence (.pkl files) |

---

## 3. Dataset

**Source:** `male_players.csv` — real FIFA player data  
**Raw rows:** 180,021 (spanning multiple FIFA editions)  
**After deduplication (latest version per player):** 53,111  
**After cleaning and null removal:** 51,878 unique player profiles  
**Positions covered:** 11 (CAM, CB, CDM, CF, CM, GK, LB, LW, RB, RW, ST)  
**Train / Test split:** 80% / 20% (41,502 train, 10,376 test)

### 3.1 Feature Engineering

The raw FIFA dataset has 109 columns. PitchIQ maps these to 10 canonical attributes:

| PitchIQ Attribute | FIFA Source Column(s) | Notes |
|---|---|---|
| pace | `pace` | Direct mapping for outfield players |
| shooting | `shooting` | Direct mapping |
| passing | `passing` | Direct mapping |
| dribbling | `dribbling` | Direct mapping |
| defending | `defending` | Direct mapping |
| physical | `physic` | FIFA uses "physic" not "physical" |
| stamina | `power_stamina` | Sub-attribute |
| strength | `power_strength` | Sub-attribute |
| agility | `movement_agility` | Sub-attribute |
| vision | `mentality_vision` | Sub-attribute |

**GK handling:** Goalkeepers have NaN for all outfield stats. Their 6 missing attributes are derived from GK-specific columns:
- pace ← avg(goalkeeping_speed, goalkeeping_reflexes)
- shooting ← avg(goalkeeping_kicking × 0.6, goalkeeping_handling × 0.4)
- passing ← goalkeeping_kicking
- dribbling ← movement_agility
- defending ← avg(gk_positioning × 0.4, gk_reflexes × 0.4, gk_diving × 0.2)
- physical ← power_strength

### 3.2 Position Distribution (after cleaning)

| Position | Count | % of dataset |
|---|---|---|
| CB | 8,803 | 17.0% |
| ST | 7,690 | 14.8% |
| CM | 6,035 | 11.6% |
| GK | 5,848 | 11.3% |
| CDM | 4,242 | 8.2% |
| RB | 4,013 | 7.7% |
| RW | 3,924 | 7.6% |
| LW | 3,911 | 7.5% |
| LB | 3,901 | 7.5% |
| CAM | 3,158 | 6.1% |
| CF | 353 | 0.7% |

### 3.3 Position Profiles (75th Percentile)

These profiles are used for gap analysis — they represent what a genuinely good player at each position looks like:

| Position | Pace | Shooting | Passing | Dribbling | Defending | Physical | Stamina | Strength | Agility | Vision |
|---|---|---|---|---|---|---|---|---|---|---|
| GK | 55 | 64 | 64 | 44 | 67 | 67 | 35 | 67 | 44 | 44 |
| CB | 65 | 41 | 53 | 55 | 69 | 75 | 69 | 81 | 60 | 49 |
| LB | 76 | 52 | 62 | 66 | 64 | 70 | 75 | 70 | 74 | 58 |
| RB | 76 | 51 | 61 | 65 | 65 | 70 | 76 | 70 | 73 | 58 |
| CDM | 67 | 57 | 64 | 66 | 67 | 74 | 77 | 75 | 70 | 65 |
| CM | 69 | 61 | 67 | 68 | 61 | 69 | 75 | 69 | 73 | 68 |
| CAM | 73 | 65 | 68 | 71 | 47 | 62 | 69 | 64 | 78 | 70 |
| LW | 80 | 64 | 64 | 71 | 44 | 63 | 70 | 64 | 80 | 65 |
| RW | 81 | 64 | 64 | 70 | 44 | 63 | 71 | 64 | 80 | 64 |
| ST | 75 | 68 | 57 | 67 | 34 | 70 | 69 | 77 | 72 | 60 |
| CF | 79 | 68 | 66 | 73 | 40 | 64 | 71 | 67 | 82 | 69 |

---

## 4. Classifiers Used

Five classifiers were trained and evaluated. Each was chosen for a specific reason.

### 4.1 K-Nearest Neighbours (KNN)

**Why chosen:**  
KNN is a natural fit for this problem. Position prediction is fundamentally about similarity — "which position do players with similar attributes typically play?" KNN answers this directly by finding the K most similar players in the training set and taking a majority vote.

**Configuration:** K=7, Euclidean distance metric  
**Strengths:** Intuitive, no training phase, handles non-linear boundaries  
**Weaknesses:** Slow at inference on large datasets (must compute distances to all 41k training points), sensitive to irrelevant features

**Result:** Accuracy 63.44% | F1 62.30%

---

### 4.2 Decision Tree

**Why chosen:**  
Decision Trees produce human-interpretable rules (e.g. "if defending > 70 AND pace < 65 → CB"). This is valuable for a football analysis tool where explainability matters — a player can understand *why* they were classified as a CB.

**Configuration:** max_depth=15  
**Strengths:** Fully interpretable, fast inference, no feature scaling needed  
**Weaknesses:** Prone to overfitting, high variance, struggles with overlapping position boundaries (e.g. CM vs CDM)

**Result:** Accuracy 59.29% | F1 59.06% — lowest performer

---

### 4.3 Random Forest

**Why chosen:**  
Random Forest addresses the Decision Tree's overfitting problem by averaging 200 trees trained on random subsets of data and features. It also provides feature importance scores, which can reveal which attributes matter most for each position.

**Configuration:** 200 estimators, max_depth=30 (capped to prevent 500MB+ model files)  
**Strengths:** Robust to overfitting, handles class imbalance better than single trees, provides feature importance  
**Weaknesses:** Large model size, slower training, less interpretable than a single tree

**Result:** Accuracy 65.65% | F1 64.25%

---

### 4.4 Support Vector Machine (SVM)

**Why chosen:**  
SVM finds the optimal hyperplane that maximally separates classes in high-dimensional space. With 10 features and 11 classes, the RBF kernel can capture non-linear boundaries between positions that are hard to separate linearly (e.g. LW vs RW, LB vs RB).

**Configuration:** RBF kernel, C=10, gamma='scale', probability=True  
**Strengths:** Effective in high-dimensional spaces, good generalisation, works well with standardised features  
**Weaknesses:** Slow training on large datasets (O(n²) to O(n³)), requires feature scaling

**Result:** Accuracy 66.60% | F1 65.02%

---

### 4.5 Neural Network — Multi-Layer Perceptron (MLP)

**Why chosen:**  
The MLP can learn complex non-linear relationships between attributes and positions that rule-based or linear models miss. With three hidden layers (128→64→32 neurons), it has enough capacity to model the subtle attribute patterns that distinguish similar positions like CM vs CAM or LW vs RW.

**Configuration:** Hidden layers (128, 64, 32), ReLU activation, Adam optimiser, early stopping (patience=20), max 500 iterations  
**Strengths:** Highest capacity model, learns complex patterns, early stopping prevents overfitting  
**Weaknesses:** Black box (not interpretable), requires careful hyperparameter tuning, slower training

**Result:** Accuracy 66.56% | F1 65.10%

---

## 5. Classifier Performance Comparison

All models trained on 41,502 players, evaluated on 10,376 held-out players.

| Rank | Model | Accuracy | Precision | Recall | F1 Score |
|---|---|---|---|---|---|
| 1 | **SVM** | **66.60%** | **65.26%** | **66.60%** | **65.02%** |
| 2 | Neural Network | 66.56% | 64.55% | 66.56% | 65.10% |
| 3 | Random Forest | 65.65% | 63.42% | 65.65% | 64.25% |
| 4 | KNN | 63.44% | 61.88% | 63.44% | 62.30% |
| 5 | Decision Tree | 59.29% | 58.91% | 59.29% | 59.06% |

**Best model by F1:** Neural Network (65.10%)  
**Best model by Accuracy:** SVM (66.60%)  
**Saved as `best_classifier.pkl`:** Neural Network

### Why ~65% accuracy is acceptable

Position prediction is an inherently ambiguous multi-class problem. Many positions share very similar attribute profiles:
- LW and RW are nearly identical (both need pace, dribbling, shooting)
- LB and RB are nearly identical (both need pace, defending, stamina)
- CM, CDM, and CAM overlap significantly in the middle of the pitch

A human scout looking at raw stats would face the same ambiguity. The system addresses this by returning **top-5 predictions with confidence scores** rather than a single hard prediction — a player with 40% ST and 35% CF confidence is correctly identified as a forward-type player even if the exact label is uncertain.

---

## 6. Clustering — K-Means

**Purpose:** Find players with similar playing styles, not just similar positions.

**Configuration:** K=8 clusters, 10 random initialisations, StandardScaler normalisation  
**Similarity metric:** Cosine similarity (via `sklearn.metrics.pairwise.cosine_similarity`)

**Why K-Means:**  
K-Means is computationally efficient on 51k rows and produces interpretable cluster centroids. Each cluster represents a "playing style archetype" (e.g. fast technical wingers, physical defensive midfielders, creative playmakers). The number of clusters (8) was chosen to be larger than the number of positions (11) to capture style variations within positions.

**Why cosine similarity for player matching:**  
Cosine similarity measures the angle between two attribute vectors, making it scale-invariant. A player rated 80/80/80 across all attributes will match a player rated 60/60/60 more closely than a player rated 90/50/70, which is the correct behaviour — playing style matters more than raw rating level.

---

## 7. Preprocessing Pipeline

```
male_players.csv (180,021 rows)
        ↓
Deduplication (latest FIFA version per player)
        ↓  53,111 rows
Position extraction (primary position from player_positions)
        ↓
GK attribute derivation (from goalkeeping sub-stats)
        ↓
Null removal (rows missing any of 10 attributes)
        ↓
Name+position deduplication (keep highest overall)
        ↓  51,878 rows
StandardScaler (fit on training data, saved as scaler.pkl)
        ↓
LabelEncoder (11 position classes, saved as label_encoder.pkl)
        ↓
Train/Test split (80/20, random_state=42)
        ↓
Model training
```

---

## 8. API Design

The backend exposes 15 REST endpoints organised into 6 blueprints:

| Blueprint | Prefix | Endpoints |
|---|---|---|
| Prediction | `/api/predict` | positions, gap-analysis, full |
| Clustering | `/api/cluster` | similar, info |
| Training | `/api/training` | plan |
| Analytics | `/api/analytics` | overview, position-profiles |
| Evaluation | `/api/evaluate` | models, models/<name>, confusion-matrix/<name>, status |
| Sessions | `/api/sessions` | list, get, delete |

**Key design decisions:**
- Routes are thin — they only validate input and call controllers
- Controllers contain business logic — they call services and shape responses
- Services wrap the ML layer — they can be swapped without touching routes
- Evaluation metrics are pre-computed to JSON at training time — the API reads a file, not re-runs ML on every request

---

## 9. Frontend Architecture

```
src/
├── pages/          — 9 pages (Home, Dashboard, Predictions, Analytics,
│                     Training, Sessions, ModelMetrics, About, NotFound)
├── components/
│   ├── common/     — Navbar (with mobile menu), Footer, Button, Loader
│   ├── forms/      — PlayerForm, InputSlider (with live colour feedback)
│   ├── prediction/ — PredictionCard, ConfidenceBar, SimilarPlayers, PositionRanking
│   ├── analysis/   — GapAnalysis, StrengthCard, WeaknessCard, ImprovementArea
│   ├── training/   — TrainingSuggestions, DrillCard, WeeklyPlan
│   └── charts/     — RadarChart, BarChart, PieChart, LineChart, ClusterChart
├── hooks/          — usePrediction, useAnalytics, useTraining,
│                     useSessions, useEvaluation
├── services/       — api, predictionService, analyticsService,
│                     trainingService, sessionService, evaluationService
├── context/        — PlayerContext (global attribute state), ThemeContext
└── utils/          — constants, calculations, formatters, helper
```

**State management:** React Context (no Redux). The `PlayerContext` holds the current player's attributes and is shared across all pages — changing a slider on the Predictions page updates the Dashboard instantly.

---

## 10. Key Design Decisions & Trade-offs

| Decision | Choice | Reason |
|---|---|---|
| Database | SQLite | Zero config, portable, appropriate for single-user scale |
| ML framework | scikit-learn | Mature, well-documented, all needed algorithms in one library |
| Position profiles | 75th percentile from real data | More realistic than hardcoded values; represents a genuinely good player |
| Evaluation caching | Pre-computed JSON | Avoids 30-60s re-computation on every API request |
| Model selection | Neural Network (best F1) | Highest weighted F1 across all 11 positions |
| GK handling | Derived from GK sub-stats | GKs have NaN for outfield stats; derivation preserves them in the dataset |
| Confidence scores | `predict_proba` | Returns probability distribution across all 11 positions, not just top-1 |
| Similarity search | Cosine similarity | Scale-invariant; style matters more than raw rating level |

---

## 11. Limitations & Future Work

**Current limitations:**
- 65% accuracy reflects genuine position ambiguity (LW/RW, LB/RB overlap)
- CF class is underrepresented (353 players vs 8,803 CB) — class imbalance affects CF predictions
- No user authentication — sessions are not tied to accounts
- Training plans are rule-based (drill library lookup) — not ML-generated

**Potential improvements:**
- SMOTE oversampling for underrepresented positions (CF, CAM)
- Hyperparameter tuning via GridSearchCV for SVM and Neural Network
- Add female player dataset for gender-inclusive analysis
- Replace rule-based training plans with a recommendation model trained on player progression data
- Add player progression tracking (compare sessions over time)

---

---

## 12. Project Folder Structure

```
PitchIQ/
│
├── backend/                        Flask REST API
│   ├── app.py                      Application factory — registers all blueprints
│   ├── config.py                   Centralised config (paths, CORS, logging, DB)
│   ├── .env                        Environment variables (not committed)
│   ├── requirements.txt            Python dependencies
│   │
│   ├── controllers/                Business logic layer
│   │   ├── prediction_controller.py
│   │   ├── analytics_controller.py
│   │   ├── clustering_controller.py
│   │   ├── training_controller.py
│   │   ├── evaluation_controller.py
│   │   └── session_controller.py
│   │
│   ├── routes/                     Thin HTTP layer (validate → controller → JSON)
│   │   ├── prediction_routes.py    POST /api/predict/*
│   │   ├── analytics_routes.py     POST /api/analytics/*
│   │   ├── clustering_routes.py    POST /api/cluster/*
│   │   ├── training_routes.py      POST /api/training/*
│   │   ├── evaluation_routes.py    GET  /api/evaluate/*
│   │   └── session_routes.py       GET/DELETE /api/sessions/*
│   │
│   ├── services/                   ML integration layer
│   │   ├── prediction_service.py   Loads classifier, runs predictions & gap analysis
│   │   ├── clustering_service.py   Wraps similarity engine & cluster analysis
│   │   ├── recommendation_service.py  Drill library lookup for training plans
│   │   └── evaluation_service.py   Reads metrics.json, serves confusion matrices
│   │
│   ├── database/
│   │   ├── db.py                   SQLite connection, CRUD for sessions
│   │   ├── schema.sql              Table definitions
│   │   └── pitchiq.db              SQLite database file (auto-created)
│   │
│   ├── middleware/
│   │   ├── error_handler.py        JSON error responses for 400/404/500
│   │   └── request_logger.py       Request/response timing logger
│   │
│   ├── utils/
│   │   └── validators.py           Input validation for all 10 attributes
│   │
│   └── tests/
│       ├── conftest.py             Pytest fixtures (in-memory SQLite)
│       ├── test_api.py             23 integration tests (every endpoint)
│       ├── test_prediction.py      16 unit tests (prediction service)
│       ├── test_clustering.py      13 unit tests (clustering service)
│       └── verify_pipeline.py      End-to-end pipeline verification script
│
├── frontend/                       React + Vite SPA
│   ├── index.html
│   ├── vite.config.js              Dev proxy: /api → localhost:5000
│   ├── package.json
│   └── src/
│       ├── App.jsx                 Root component (BrowserRouter + Providers)
│       ├── main.jsx                React DOM entry point
│       ├── index.css               Global CSS variables (dark theme)
│       │
│       ├── pages/                  9 route-level pages
│       │   ├── Home.jsx            Landing page with feature overview
│       │   ├── Dashboard.jsx       Player overview with charts
│       │   ├── Predictions.jsx     Full analysis pipeline UI
│       │   ├── Analytics.jsx       Deep-dive attribute analysis
│       │   ├── Training.jsx        Weekly training plan generator
│       │   ├── Sessions.jsx        Saved analysis history
│       │   ├── ModelMetrics.jsx    Classifier performance dashboard
│       │   ├── About.jsx           Project information
│       │   └── NotFound.jsx        404 page
│       │
│       ├── components/
│       │   ├── common/             Navbar, Footer, Button, Loader
│       │   ├── forms/              PlayerForm, InputSlider
│       │   ├── prediction/         PredictionCard, ConfidenceBar, SimilarPlayers, PositionRanking
│       │   ├── analysis/           GapAnalysis, StrengthCard, WeaknessCard, ImprovementArea
│       │   ├── training/           TrainingSuggestions, DrillCard, WeeklyPlan
│       │   └── charts/             RadarChart, BarChart, PieChart, LineChart, ClusterChart
│       │
│       ├── hooks/                  Custom React hooks (data fetching + state)
│       │   ├── usePrediction.js
│       │   ├── useAnalytics.js
│       │   ├── useTraining.js
│       │   ├── useSessions.js
│       │   └── useEvaluation.js
│       │
│       ├── services/               Axios API wrappers
│       │   ├── api.js              Base axios client with interceptors
│       │   ├── predictionService.js
│       │   ├── analyticsService.js
│       │   ├── trainingService.js
│       │   ├── sessionService.js
│       │   └── evaluationService.js
│       │
│       ├── context/
│       │   ├── PlayerContext.jsx   Global player attribute state
│       │   └── ThemeContext.jsx    Theme provider
│       │
│       ├── routes/
│       │   └── AppRoutes.jsx       React Router route definitions
│       │
│       └── utils/
│           ├── constants.js        FEATURE_COLS, POSITION_LABELS, ATTRIBUTE_COLORS
│           ├── calculations.js     overallRating, normalizeToPercent
│           ├── formatters.js       capitalize, ratingColor, gapColor
│           └── helper.js           clamp, debounce
│
├── ml_models/                      Machine learning layer
│   ├── classification/             5 classifier implementations
│   │   ├── knn_classifier.py
│   │   ├── decision_tree.py
│   │   ├── random_forest.py
│   │   ├── svm_classifier.py
│   │   └── neural_network.py
│   │
│   ├── clustering/
│   │   ├── kmeans_clustering.py    K-Means training
│   │   ├── cluster_analysis.py     Cluster assignment & statistics
│   │   └── similarity_engine.py    Cosine similarity player matching
│   │
│   ├── preprocessing/
│   │   ├── clean_data.py           Raw FIFA data → cleaned_players.csv
│   │   ├── normalize_data.py       StandardScaler → normalized_players.csv
│   │   ├── label_encoding.py       LabelEncoder → encoded_dataset.csv
│   │   ├── feature_selection.py    Canonical FEATURE_COLS definition
│   │   └── compute_profiles.py     75th-percentile position profiles
│   │
│   ├── evaluation/
│   │   ├── accuracy_metrics.py     accuracy, precision, recall, F1
│   │   ├── confusion_matrix.py     Confusion matrix computation
│   │   ├── classification_report.py  Per-class report
│   │   └── model_comparison.py     Compare all 5 models, save metrics.json
│   │
│   └── training/
│       ├── train_classifier.py     Master pipeline (clean→train→evaluate)
│       ├── compute_and_train.py    Full retrain with profile computation
│       ├── train_cluster.py        Standalone KMeans retraining
│       └── hyperparameter_tuning.py  GridSearchCV for Random Forest
│
├── dataset/
│   ├── raw/
│   │   ├── male_players.csv        Source data (180,021 rows, 109 columns)
│   │   └── generate_dataset.py     Legacy synthetic data generator (unused)
│   └── processed/
│       ├── cleaned_players.csv     51,878 rows × 17 columns
│       ├── normalized_players.csv  StandardScaler applied
│       └── encoded_dataset.csv     LabelEncoder applied (position_encoded column)
│
├── saved_models/                   Trained model files (.pkl)
│   ├── best_classifier.pkl         Copy of best model (Neural Network)
│   ├── knn_model.pkl
│   ├── decision_tree.pkl
│   ├── random_forest.pkl
│   ├── svm_model.pkl
│   ├── neural_network.pkl
│   ├── kmeans_model.pkl
│   ├── scaler.pkl                  StandardScaler (fitted on training data)
│   └── label_encoder.pkl           LabelEncoder (11 position classes)
│
├── reports/
│   ├── project_report.md           This document
│   ├── metrics.json                Pre-computed model metrics (served by API)
│   ├── model_comparison.txt        Human-readable comparison table
│   └── position_profiles.txt       75th-percentile profiles per position
│
├── requirements.txt                Root Python dependencies
├── pytest.ini                      Test configuration
├── README.md                       Quick-start guide
└── .gitignore
```

---

## 13. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
│                                                             │
│  React SPA (Vite, port 5173)                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │  Pages   │  │Components│  │  Hooks   │  │ Services  │  │
│  │ 9 routes │→ │ 30+ comps│→ │ 5 hooks  │→ │ Axios API │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────┬─────┘  │
└────────────────────────────────────────────────────┼────────┘
                                                     │ HTTP/JSON
                                              /api/* proxy
                                                     │
┌────────────────────────────────────────────────────▼────────┐
│                    FLASK API (port 5000)                     │
│                                                             │
│  Routes → Controllers → Services                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/predict/*   /api/cluster/*   /api/training/*   │   │
│  │  /api/analytics/* /api/evaluate/*  /api/sessions/*   │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                    │                │            │
│    ML Services           Evaluation         SQLite DB        │
│    (prediction,          (reads             (sessions        │
│     clustering,           metrics.json)      table)          │
│     recommendation)                                          │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    ML MODELS LAYER                           │
│                                                             │
│  saved_models/                  dataset/processed/          │
│  ├── best_classifier.pkl  ←──── encoded_dataset.csv         │
│  ├── scaler.pkl           ←──── normalized_players.csv      │
│  ├── label_encoder.pkl    ←──── cleaned_players.csv         │
│  └── kmeans_model.pkl                                       │
│                                                             │
│  Source: dataset/raw/male_players.csv (51,878 players)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Data Flow — Full Analysis Request

When a user clicks "Predict Positions" on the frontend, the following sequence occurs:

```
1. User adjusts 10 attribute sliders (pace, shooting, etc.)
   └─ PlayerContext stores values globally

2. POST /api/predict/full  {pace:80, shooting:85, ...}
   └─ prediction_routes.py validates all 10 fields (1–99 range)
   └─ prediction_controller.handle_full_analysis()

3. predict_positions(attrs)
   └─ Loads best_classifier.pkl (Neural Network)
   └─ Scales input with scaler.pkl
   └─ predict_proba() → 11 confidence scores
   └─ Returns top-5 [{position, confidence}, ...]

4. gap_analysis(attrs, top_position)
   └─ Compares each attribute against POSITION_PROFILES[position]
   └─ diff ≥ +3  → strength
   └─ diff ≤ -5  → weakness
   └─ Returns {gaps, strengths, weaknesses}

5. get_similar_players(attrs, top_n=5)
   └─ Loads cleaned_players.csv + scaler.pkl
   └─ Scales input vector
   └─ cosine_similarity(input, all_51878_players)
   └─ Returns top-5 most similar real players

6. get_cluster(attrs)
   └─ Loads kmeans_model.pkl
   └─ Predicts cluster assignment (0–7)
   └─ Returns cluster stats (size, avg attributes, dominant positions)

7. generate_recommendations(weaknesses, position)
   └─ Looks up DRILL_LIBRARY for each weak attribute
   └─ Builds 5-day weekly plan (Mon–Fri)

8. save_session(player_name, attrs, predictions, gap, plan, cluster)
   └─ Inserts row into analysis_sessions (SQLite)
   └─ Returns UUID session_token

9. Response JSON → Frontend
   └─ PredictionCard renders confidence bars
   └─ RadarChart overlays player vs ideal profile
   └─ GapAnalysis shows per-attribute gaps
   └─ SimilarPlayers lists real FIFA players
   └─ TrainingSuggestions shows weekly drill plan
```

---

## 15. Gap Analysis Methodology

Gap analysis is the core analytical feature of PitchIQ. It answers: *"How far is this player from being good at position X?"*

### How it works

For each of the 10 attributes, the system computes:

```
gap = player_value - ideal_value
```

Where `ideal_value` is the **75th percentile** of that attribute among all real players at that position in the dataset. This means the ideal represents a genuinely good player — not the average, and not the elite.

**Classification rules:**
- `gap ≥ +3` → **Strength** (player exceeds the ideal)
- `-5 < gap < +3` → **Neutral** (within acceptable range)
- `gap ≤ -5` → **Weakness** (player is meaningfully below ideal)

### Example — Striker (ST) profile

A player with these attributes:

| Attribute | Player | Ideal (ST 75th pct) | Gap | Classification |
|---|---|---|---|---|
| pace | 75 | 75 | 0 | Neutral |
| shooting | 85 | 68 | +17 | **Strength** |
| passing | 55 | 57 | -2 | Neutral |
| dribbling | 70 | 67 | +3 | **Strength** |
| defending | 25 | 34 | -9 | **Weakness** |
| physical | 72 | 70 | +2 | Neutral |
| stamina | 60 | 69 | -9 | **Weakness** |
| strength | 80 | 77 | +3 | **Strength** |
| agility | 70 | 72 | -2 | Neutral |
| vision | 58 | 60 | -2 | Neutral |

**Strengths:** shooting (+17), strength (+3), dribbling (+3)  
**Weaknesses:** defending (-9), stamina (-9)  
**Training priority:** stamina and defending drills

---

## 16. Training Plan Methodology

Training plans are generated from gap analysis results using a curated drill library.

### Process

1. **Identify top-4 weaknesses** from gap analysis (sorted by deficit size)
2. **Look up 2 drills per weak attribute** from the `DRILL_LIBRARY` dictionary
3. **Build a 5-day weekly plan** (Monday–Friday), assigning 2 drills per day
4. **Rest days** are assigned when all priority drills are covered

### Drill Library Coverage

| Attribute | Drill 1 | Drill 2 |
|---|---|---|
| pace | Sprint Intervals (20 min) | Resistance Band Sprints (15 min) |
| shooting | Finishing Drills (25 min) | Long-Range Shooting (20 min) |
| passing | Rondo 5v2 (20 min) | Long-Pass Accuracy (15 min) |
| dribbling | Cone Slalom (15 min) | 1v1 Isolation (20 min) |
| defending | Defensive Positioning (20 min) | Tackle Timing (15 min) |
| physical | Strength Circuit (30 min) | Plyometric Training (20 min) |
| stamina | Interval Running (30 min) | Fartlek Run (25 min) |
| strength | Upper Body Circuit (25 min) | Core Stability (20 min) |
| agility | Ladder Drills (15 min) | T-Drill (15 min) |
| vision | Awareness Rondo (20 min) | Positional Play (25 min) |

### Example Weekly Plan (for a player weak in stamina and defending)

| Day | Drills |
|---|---|
| Monday | Interval Running, Fartlek Run |
| Tuesday | Defensive Positioning, Tackle Timing |
| Wednesday | Rest / Recovery |
| Thursday | Rest / Recovery |
| Friday | Rest / Recovery |

---

## 17. Testing

### Backend Test Suite

52 automated tests across 3 test files, run with pytest.

| File | Tests | Coverage |
|---|---|---|
| `test_api.py` | 23 | All 15 API endpoints (integration tests via Flask test client) |
| `test_prediction.py` | 16 | Prediction service + controller (unit tests) |
| `test_clustering.py` | 13 | Clustering service + controller (unit tests) |

**Test infrastructure:**
- In-memory SQLite database (patched via `conftest.py`) — tests never touch the real DB
- Session-scoped Flask app fixture — app created once per test session for speed
- Fixtures: `valid_attrs` (strong striker profile), `weak_attrs` (below-average player)

**Key test cases:**
- Confidence scores sum to ~100% across all 5 predictions
- GK profile correctly predicts GK as top position
- Striker profile predicts an attacking position in top-3
- Gap analysis returns exactly 10 attribute gaps
- Session lifecycle: create → retrieve → list → delete
- Confusion matrix returns 11×11 matrix with correct labels
- Invalid input (missing field, out-of-range value) returns 400

**Run tests:**
```bash
python -m pytest backend/tests -v
```

---

## 18. Deployment Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- `male_players.csv` placed in `dataset/raw/`

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Train all models (run once, ~5–10 minutes)
```bash
python ml_models/training/train_classifier.py
```
This produces:
- `dataset/processed/cleaned_players.csv` (51,878 rows)
- `saved_models/*.pkl` (all 9 model files)
- `reports/metrics.json` (pre-computed evaluation metrics)

### Step 3 — Start the backend
```bash
python backend/app.py
```
API available at `http://localhost:5000`  
Health check: `GET http://localhost:5000/api/health`

### Step 4 — Start the frontend
```bash
cd frontend
npm install
npm run dev
```
App available at `http://localhost:5173`

### Environment variables (`backend/.env`)
```
FLASK_DEBUG=1
PORT=5000
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

---

## 19. Per-Position Classifier Analysis

The confusion matrix reveals which positions are easiest and hardest to classify correctly.

### Easy to classify (high precision & recall)
- **GK** — Goalkeepers have a completely unique attribute profile (low pace/shooting, high defending/physical). All 5 classifiers achieve near-perfect GK classification.
- **CB** — Centre-backs have the highest defending + strength combination, making them clearly distinguishable.
- **ST** — Strikers have the highest shooting + physical combination among forward positions.

### Hard to classify (frequent misclassification)
- **LW / RW** — Left and right wingers have nearly identical attribute profiles. The model frequently confuses them with each other. This is expected — in real football, many players play both wings.
- **LB / RB** — Same issue as LW/RW. Full-backs on both sides have identical attribute requirements.
- **CM / CDM / CAM** — The three central midfield positions overlap significantly. A player with balanced attributes across passing, defending, and vision could legitimately play any of the three.
- **CF** — Only 353 CF players in the dataset (0.7%) vs 8,803 CB players (17%). The severe class imbalance means the model rarely predicts CF even when it is the correct answer.

### Implication for the product
This is why PitchIQ returns **top-5 predictions with confidence scores** rather than a single label. A player who is genuinely a LW will see LW at 45% and RW at 40% — both are correct, and the user understands they are a winger type. The gap analysis then clarifies which specific attributes to develop for each option.

---

## 20. Conclusion

PitchIQ successfully demonstrates that machine learning can provide meaningful football position analysis for amateur players without access to professional scouting infrastructure.

### What was achieved
- A complete full-stack application with 9 frontend pages, 15 API endpoints, and 5 trained ML classifiers
- Real data pipeline processing 180,021 raw FIFA records down to 51,878 clean player profiles
- Position prediction accuracy of 66.6% on an inherently ambiguous 11-class problem
- Gap analysis grounded in real player data (75th percentile profiles, not hardcoded values)
- Session persistence allowing players to track their analyses over time
- 52 automated tests with 100% pass rate

### Key technical achievements
- **GK handling** — Derived 6 missing attributes from GK-specific sub-stats, preserving 5,848 goalkeeper profiles that would otherwise be discarded
- **Evaluation caching** — Pre-computed metrics.json eliminates 30–60 second API timeouts on the Model Metrics page
- **Architecture separation** — Routes → Controllers → Services → ML means any component can be replaced independently
- **Real position profiles** — 75th-percentile profiles from 51,878 real players produce more accurate gap analysis than hardcoded values

### Performance summary

| Model | Accuracy | F1 | Verdict |
|---|---|---|---|
| Neural Network | 66.56% | 65.10% | **Best overall (selected)** |
| SVM | 66.60% | 65.02% | Best raw accuracy |
| Random Forest | 65.65% | 64.25% | Good balance of speed and accuracy |
| KNN | 63.44% | 62.30% | Intuitive but slower at inference |
| Decision Tree | 59.29% | 59.06% | Most interpretable, lowest accuracy |

The Neural Network was selected as the production model (`best_classifier.pkl`) due to its highest weighted F1 score across all 11 positions, indicating the best balance of precision and recall across the full position distribution.

---

*PitchIQ v2.0.0 — Technical Report*  
*Dataset: male_players.csv | 51,878 real FIFA player profiles | 11 positions*  
*Models trained: KNN, Decision Tree, Random Forest, SVM, Neural Network (MLP), K-Means*

---

## 21. Appendix — API Reference

Complete list of all 15 REST endpoints exposed by the Flask backend.

### Prediction Endpoints

| Method | Endpoint | Request Body | Response |
|---|---|---|---|
| POST | `/api/predict/positions` | 10 attributes (1–99) | `{predictions: [{position, confidence}×5]}` |
| POST | `/api/predict/gap-analysis` | 10 attributes + `position` | `{position, gaps, strengths, weaknesses}` |
| POST | `/api/predict/full` | 10 attributes + optional `player_name`, `player_age`, `save` | Full pipeline result + `session_token` |

### Clustering Endpoints

| Method | Endpoint | Request Body | Response |
|---|---|---|---|
| POST | `/api/cluster/similar` | 10 attributes + optional `top_n` | `{similar_players: [{name, position, similarity, ...attrs}]}` |
| POST | `/api/cluster/info` | 10 attributes | `{cluster_id, cluster_size, avg_attributes, dominant_positions}` |

### Training Endpoint

| Method | Endpoint | Request Body | Response |
|---|---|---|---|
| POST | `/api/training/plan` | 10 attributes + optional `position` | `{gap_analysis, training_plan: {drills, weekly_plan}}` |

### Analytics Endpoints

| Method | Endpoint | Request Body | Response |
|---|---|---|---|
| POST | `/api/analytics/overview` | 10 attributes | `{overall_rating, attributes, top_position, predictions, gap_analysis, similar_players}` |
| GET  | `/api/analytics/position-profiles` | — | `{profiles: {GK:{...}, CB:{...}, ...}}` |

### Evaluation Endpoints

| Method | Endpoint | Response |
|---|---|---|
| GET | `/api/evaluate/models` | `{models: {knn:{accuracy,f1,...}, ...}, best_model}` |
| GET | `/api/evaluate/models/<name>` | `{model, display, metrics: {accuracy, f1, precision, recall}}` |
| GET | `/api/evaluate/confusion-matrix/<name>` | `{model, labels:[11 positions], matrix:[[11×11]]}` |
| GET | `/api/evaluate/status` | `{metrics_ready: bool}` |

### Session Endpoints

| Method | Endpoint | Response |
|---|---|---|
| GET | `/api/sessions/` | `{sessions:[...], total, limit, offset}` |
| GET | `/api/sessions/<token>` | Full session object with all stored results |
| DELETE | `/api/sessions/<token>` | `{deleted: bool, session_token}` |

### Health

| Method | Endpoint | Response |
|---|---|---|
| GET | `/api/health` | `{status: "ok", service: "PitchIQ API", version: "2.0.0"}` |
| GET | `/api` | Full endpoint map |

### Input Validation

All POST endpoints that accept player attributes enforce:
- All 10 fields must be present: `pace`, `shooting`, `passing`, `dribbling`, `defending`, `physical`, `stamina`, `strength`, `agility`, `vision`
- Each value must be an integer between 1 and 99 (inclusive)
- Missing or out-of-range values return HTTP 400 with `{"error": "..."}`

---

## 22. Appendix — Attribute Definitions

The 10 canonical attributes used throughout PitchIQ, their meaning in football, and their FIFA source column:

| Attribute | Football Meaning | FIFA Source | Range |
|---|---|---|---|
| **pace** | Sprint speed and acceleration | `pace` (outfield) / derived for GK | 1–99 |
| **shooting** | Finishing, shot power, long shots | `shooting` (outfield) / derived for GK | 1–99 |
| **passing** | Short passing, long passing, crossing | `passing` (outfield) / `goalkeeping_kicking` for GK | 1–99 |
| **dribbling** | Ball control, close control, agility with ball | `dribbling` (outfield) / `movement_agility` for GK | 1–99 |
| **defending** | Tackling, marking, interceptions | `defending` (outfield) / derived from GK positioning for GK | 1–99 |
| **physical** | Strength, jumping, aggression, stamina composite | `physic` (outfield) / `power_strength` for GK | 1–99 |
| **stamina** | Ability to maintain performance over 90 minutes | `power_stamina` (all positions) | 1–99 |
| **strength** | Physical power in duels and challenges | `power_strength` (all positions) | 1–99 |
| **agility** | Quickness of movement, balance, body control | `movement_agility` (all positions) | 1–99 |
| **vision** | Awareness, decision-making, through-ball ability | `mentality_vision` (all positions) | 1–99 |

**Overall Rating** (displayed on Dashboard) is the simple arithmetic mean of all 10 attributes, rounded to the nearest integer.

---

## 23. Appendix — Position Abbreviations

All 11 positions used in PitchIQ, their full names, and their typical role on the pitch:

| Code | Full Name | Zone | Primary Attributes |
|---|---|---|---|
| **GK** | Goalkeeper | Goal | defending, physical, strength |
| **CB** | Centre-Back | Defence | defending, strength, physical |
| **LB** | Left-Back | Defence | pace, defending, stamina, agility |
| **RB** | Right-Back | Defence | pace, defending, stamina, agility |
| **CDM** | Defensive Midfielder | Midfield | defending, stamina, strength, passing |
| **CM** | Central Midfielder | Midfield | passing, stamina, vision, dribbling |
| **CAM** | Attacking Midfielder | Midfield | vision, passing, dribbling, agility |
| **LW** | Left Winger | Attack | pace, dribbling, agility, shooting |
| **RW** | Right Winger | Attack | pace, dribbling, agility, shooting |
| **ST** | Striker | Attack | shooting, strength, pace, physical |
| **CF** | Centre-Forward | Attack | dribbling, agility, shooting, vision |

**Position mapping from FIFA raw data:**

| FIFA Raw Values | Mapped To |
|---|---|
| GK | GK |
| CB, LCB, RCB | CB |
| LB, LWB | LB |
| RB, RWB | RB |
| CDM, LDM, RDM | CDM |
| CM, LCM, RCM | CM |
| CAM, LAM, RAM | CAM |
| LW, LM, LF | LW |
| RW, RM, RF | RW |
| ST, LS, RS | ST |
| CF | CF |

---

*PitchIQ v2.0.0 — Technical Report*  
*Dataset: male_players.csv | 51,878 real FIFA player profiles | 11 positions*  
*Models: KNN, Decision Tree, Random Forest, SVM, Neural Network (MLP), K-Means*  
*Best Model: Neural Network (MLP) — Accuracy 66.56% | F1 65.10%*  
*Tests: 52 automated tests — 100% pass rate*

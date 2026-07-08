# PitchIQ — Deployment Guide

Deploy the backend on **Render** and the frontend on **Vercel**, with **MongoDB Atlas** as the database.

---

## Prerequisites

- Project pushed to a GitHub repository
- MongoDB Atlas cluster running (already configured with your Atlas URI)
- Render account: [render.com](https://render.com)
- Vercel account: [vercel.com](https://vercel.com)

> **Important:** The `saved_models/` `.pkl` files and `dataset/raw/male_players.csv`
> are in `.gitignore` and will NOT be pushed to GitHub. Render needs them to work.
> See **Step 3** for how to handle this.

---

## Step 1 — Push to GitHub

From the project root:

```bash
git init                          # if not already a git repo
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/YOUR_USERNAME/pitchiq.git
git push -u origin main
```

Verify your repo has these files at the root:
- `wsgi.py`
- `Procfile`
- `render.yaml`
- `start_backend.py`
- `requirements.txt` (root-level, same as `backend/requirements.txt`)

---

## Step 2 — Deploy Backend on Render

### 2a. Create the Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub account → select your **pitchiq** repository
4. Configure the service:

| Setting | Value |
|---|---|
| **Name** | `pitchiq-backend` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Instance Type** | Free (or Starter $7/mo for always-on) |

### 2b. Set Environment Variables

In the Render dashboard → **Environment** tab, add these one by one:

| Key | Value |
|---|---|
| `FLASK_DEBUG` | `0` |
| `SECRET_KEY` | `1dab92286800769a13195b746996f25ccc23b824965cc76b6a0daef16ba3f772` |
| `MONGO_URI` | `mongodb+srv://peraownabbas_db_user:Fsmi42h5Socux6RP@cluster0.tuj5kpz.mongodb.net/` |
| `MONGO_DB` | `pitchiq` |
| `CORS_ORIGINS` | *(fill after Vercel deploy — e.g. `https://pitchiq.vercel.app`)* |
| `OPENAI_API_KEY` | `API here` |
| `OPENAI_MODEL` | `gpt-4o-mini` |
| `LOG_LEVEL` | `INFO` |

Click **Save Changes** then **Manual Deploy** → **Deploy latest commit**.

### 2c. Handle saved_models (the ML .pkl files)

The trained models can't go in git (they're 200MB+). You have two options:

**Option A — Upload via Render Shell (simplest)**

After the service deploys:
1. In Render dashboard → your service → **Shell**
2. The shell opens at `/opt/render/project/src`
3. Upload your `.pkl` files using the Render API or copy them via curl from a cloud URL

**Option B — Add a Persistent Disk + upload script**

1. In Render → your service → **Disks** → Add disk
2. Mount path: `/opt/render/project/src/saved_models`
3. Size: 2 GB (enough for all models)
4. SSH into the shell and upload the `.pkl` files once

**Option C — Retrain on Render during build (slow but automatic)**

Change the Build Command to:
```
pip install -r backend/requirements.txt && python ml_models/training/train_classifier.py
```

This runs the full training pipeline on every deploy (~10 minutes). You also need to upload `male_players.csv` somewhere accessible (S3, Dropbox public link, etc.) and modify `clean_data.py` to download it.

### 2d. Verify backend is live

Visit: `https://pitchiq-backend.onrender.com/api/health`

You should see:
```json
{"status": "ok", "service": "PitchIQ API", "version": "2.0.0"}
```

> **Note:** On the free tier, Render spins down after 15 minutes of inactivity.
> The first request after a cold start takes ~30 seconds. The frontend has a
> 30-second timeout configured for this.

---

## Step 3 — Deploy Frontend on Vercel

### 3a. Import project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure:

| Setting | Value |
|---|---|
| **Framework Preset** | `Vite` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

### 3b. Set Environment Variable

Under **Environment Variables** in the Vercel setup:

| Key | Value |
|---|---|
| `VITE_API_BASE` | `https://pitchiq-backend.onrender.com/api` |

> Replace `pitchiq-backend` with your actual Render service name.

Click **Deploy**.

### 3c. Update CORS on Render

Once Vercel gives you a URL (e.g. `https://pitchiq-abc123.vercel.app`):

1. Go back to Render → your service → **Environment**
2. Update `CORS_ORIGINS` to your exact Vercel URL:
   ```
   https://pitchiq-abc123.vercel.app
   ```
3. Click **Save Changes** → service redeploys automatically

---

## Step 4 — Verify the full stack

1. Open your Vercel URL
2. Enter player attributes on the Predictions page → click Predict
3. Results should appear (backend is responding)
4. Click **Generate Report** → AI scouting report should appear
5. Check MongoDB Atlas → **pitchiq** database → **analysis_sessions** → your session should be there

---

## Post-deployment checklist

- [ ] `GET https://pitchiq-backend.onrender.com/api/health` returns `{"status": "ok"}`
- [ ] Frontend loads at your Vercel URL
- [ ] Position prediction works (ML models accessible)
- [ ] Sessions are saved to MongoDB Atlas
- [ ] AI scouting report generates successfully
- [ ] CORS is set to the exact Vercel URL (not `localhost`)

---

## Environment variables reference

### Render (backend)

| Variable | Description | Example |
|---|---|---|
| `FLASK_DEBUG` | Must be `0` in production | `0` |
| `PORT` | Set automatically by Render | *(leave unset)* |
| `SECRET_KEY` | Flask secret key | `1dab92286...` |
| `MONGO_URI` | MongoDB Atlas connection string | `mongodb+srv://...` |
| `MONGO_DB` | Database name | `pitchiq` |
| `CORS_ORIGINS` | Allowed frontend URL | `https://pitchiq.vercel.app` |
| `OPENAI_API_KEY` | OpenRouter API key | `sk-or-v1-...` |
| `OPENAI_MODEL` | Model to use | `gpt-4o-mini` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Vercel (frontend)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_BASE` | Backend API URL | `https://pitchiq-backend.onrender.com/api` |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'backend'` | Build command must be run from project root, not `backend/` |
| `Cannot POST /api/predict/full` | Backend didn't start with Gunicorn — check Render logs |
| CORS error in browser | `CORS_ORIGINS` on Render doesn't match your exact Vercel URL |
| `Connection refused` to MongoDB | Check `MONGO_URI` env var on Render — Atlas IP whitelist must allow `0.0.0.0/0` |
| Models not found (`FileNotFoundError: saved_models/...`) | `.pkl` files not on Render disk — use Persistent Disk option |
| Cold start timeout | First request after inactivity takes ~30s on free tier — normal behaviour |

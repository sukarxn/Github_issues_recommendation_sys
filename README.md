# GitHub Issues Recommender

A small project that recommends relevant GitHub issues to contributors based on profile and issue content. This repository contains a Python backend (model/logic & API) and a Vite-based frontend (React).

This README gives a quick overview, how the project is organised, and simple steps to run it locally.

## What this project does

- Analyzes issue text and user profile information.
- Scores or ranks issues that may be relevant to a user.
- Provides a small frontend for browsing recommendations and a backend API for computing them.

## Repository structure (important files)

- `backend/` — project backend code and helper modules.
- `api.py`, `core.py`, `main.py`, `phi4_predictor.py` — Python scripts implementing API endpoints and prediction logic.
- `requirements.txt` — Python dependencies for the backend.
- `frontend/` — Vite + React frontend.
- `package.json` — frontend deps and scripts.
- `sample_profile.txt`, `testdata.json`, `smalltestdata.json` — example inputs used for testing and evaluation.

## Quick start (run locally)

Prerequisites:
- Python 3.8+ (3.10 recommended)
- Node.js 16+ and npm or yarn

Backend (Python)

1. Open a terminal and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and run the backend server:

```bash
pip install -r requirements.txt
# Start whichever entrypoint you prefer. Common options in this repo:
python main.py
# or
python api.py
```

If `main.py` or `api.py` starts a small web server, the terminal will show the listen address.

Frontend (Vite + React)

1. In a new terminal window/tab:

```bash
cd frontend
npm install
npm run dev
```

2. Open the provided local URL (usually http://localhost:5173) to view the UI and test recommendations.

## Tests and evaluation

- There are a few evaluation scripts (`evaluate_phi2.py`, `evaluate_small.py`) and simple tests (`test_caching.py`). Run them from the project root with the Python virtual environment activated:

```bash
python evaluate_small.py
```

## Notes about large files

- I removed the `Presentation and Report/` files from git history and added that folder to `.gitignore` so those large media files are not uploaded to GitHub. The files should still be present on your local disk unless you explicitly delete them.
- If you need to track large media in the repo, consider using Git LFS. I can help set that up if you want.

## Contributing

- Create an issue or a pull request. For code changes, follow the existing style and add a short test where practical.

## License

This repository does not currently contain a LICENSE file. If you want an open-source license, I recommend adding an `MIT` or `Apache-2.0` file. Tell me which one and I can add it.

## Contact

If you want further help (set up Git LFS, switch to SSH remotes, or add CI), tell me what you'd like and I’ll continue.


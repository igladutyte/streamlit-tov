## TOV Copywriter

### Setup
1. Create and activate a virtual env (optional).
2. Install deps:
```bash
pip install -r requirements.txt
```
3. Create `.env` with your OpenAI key:
```env
OPENAI_API_KEY=sk-...
# Optional: override model
OPENAI_MODEL=gpt-4o-mini
```

### Run
```bash
streamlit run app.py
```

### Notes
- Data persists to `data/app_state.json`.
- Use the sidebar to manage projects and navigate to Editor, History, and Tone of Voice Admin.

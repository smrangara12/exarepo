# Exa Probabilistic Search Lab

This Streamlit project searches with Exa, converts results into a
probability-weighted return distribution, and evaluates result quality.

It supports:

- Exa API search through `EXA_API_KEY`
- Sidebar API key input for local exploration
- Demo mode when no key is available
- Probability scoring based on Exa semantic score, query-term overlap, and freshness
- Built-in eval queries
- Downloadable search-result CSV

## Setup

```powershell
python -m pip install -r requirements.txt
```

## API Key

Set the key with one of these methods:

```powershell
$env:EXA_API_KEY = "your-exa-api-key"
```

or paste it into the app sidebar. Do not commit API keys.

## Run

```powershell
python -m streamlit run app.py --server.port 8504
```

Open:

```text
http://localhost:8504
```

## Evaluate

```powershell
python eval_app.py
```

The eval harness runs in demo mode, checks probability normalization, verifies
evaluation labels, and confirms the Streamlit app executes without exceptions.

# Exa Probabilistic Search Lab

This Streamlit project searches with Exa, converts results into a
probability-weighted return distribution, and evaluates result quality.

It supports:

- Exa API search through `EXA_API_KEY`
- Sidebar API key input for local exploration
- Demo mode when no key is available
- Probability scoring based on Exa semantic score, query-term overlap, and freshness
- Built-in eval queries
- Query variation generation across investor, macro, technical, risk, and recency contexts
- A variation harness that compares context-specific queries by quality score
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
evaluation labels, runs query-variation harness checks, and confirms the
Streamlit app executes without exceptions.

## How To Analyze And Improve Over Iterations

Use the app as a search experimentation loop rather than a one-shot query tool.

1. Start with a direct baseline query that states the decision question.
2. Choose variation contexts in the sidebar:
   - `Investor due diligence` adds growth, FCF, valuation, margin, guidance, and customer concentration language.
   - `Macro regime` adds rates, inflation, recession, liquidity, credit, dollar, and oil context.
   - `Technical implementation` adds model, data, reproducibility, and benchmark language.
   - `Risk and counterargument` adds downside, uncertainty, constraints, and sensitivity language.
   - `Recent market evidence` pushes the query toward newer reports and current trend language.
3. Compare the `Variations` tab:
   - Higher `Quality score` is better.
   - Higher `Coverage` means more expected concepts appeared in the top results.
   - Higher `Diversity` means the top results are spread across more sources.
   - `Top probability` should not become too concentrated; a single dominant result can mean the query is too narrow.
4. Improve the query:
   - If coverage is low, add missing concepts from the eval terms.
   - If diversity is low, remove narrow company/product names or broaden the industry phrase.
   - If the top result dominates, reduce recency or semantic weight, or add a counterargument context.
   - If results are stale, increase recency weight or shorten the freshness half-life.
5. Record each iteration:

```text
Question:
Baseline query:
Context added:
Expected concepts:
Best variation:
What improved:
What got worse:
Next query change:
Decision / research takeaway:
```

The goal is not only to find more results; it is to find a repeatable query
form that returns relevant, diverse, current evidence for the decision being
researched.

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(
    page_title="Exa Probabilistic Search Lab",
    page_icon="EXA",
    layout="wide",
)


PALETTE = {
    "ink": "#17212b",
    "muted": "#607080",
    "line": "#d7dee6",
    "blue": "#2f6f9f",
    "green": "#2f8f6f",
    "amber": "#bd7a1f",
    "red": "#bf4e45",
    "purple": "#725ba7",
}

DEMO_RESULTS = [
    {
        "title": "AI data center power demand is reshaping grid investment",
        "url": "https://example.com/ai-data-center-power-grid",
        "publishedDate": "2026-08-28",
        "score": 0.91,
        "text": "Hyperscaler AI buildouts are increasing demand for switchgear, transformers, grid upgrades, and cooling infrastructure.",
    },
    {
        "title": "Financial repression and negative real returns",
        "url": "https://example.com/financial-repression-real-returns",
        "publishedDate": "2026-07-14",
        "score": 0.84,
        "text": "When deposit rates remain below essentials inflation, household savings lose purchasing power even if nominal balances rise.",
    },
    {
        "title": "AI infrastructure: networking, optical, storage, and power",
        "url": "https://example.com/ai-infrastructure-stack",
        "publishedDate": "2026-09-02",
        "score": 0.88,
        "text": "The AI infrastructure chain includes GPUs, networking, optical links, memory, storage, power, cooling, and construction.",
    },
    {
        "title": "Treasury yields and valuation pressure for high-growth equities",
        "url": "https://example.com/rates-growth-valuation",
        "publishedDate": "2026-06-20",
        "score": 0.76,
        "text": "Higher risk-free rates increase the hurdle rate for long-duration growth stocks and raise the importance of free cash flow.",
    },
    {
        "title": "Enterprise AI monetization in cloud platforms",
        "url": "https://example.com/cloud-ai-monetization",
        "publishedDate": "2026-09-06",
        "score": 0.82,
        "text": "Cloud platforms are translating AI demand into infrastructure revenue, usage growth, and enterprise software attach rates.",
    },
]


EVAL_QUERIES = [
    {
        "query": "AI data center power demand grid investment transformers switchgear",
        "expected_terms": ["ai", "data", "power", "grid", "transformers", "switchgear"],
    },
    {
        "query": "financial repression real return erosion savings inflation interest income",
        "expected_terms": ["financial", "repression", "real", "return", "inflation", "savings"],
    },
    {
        "query": "10 year treasury yields valuation pressure high growth stocks free cash flow",
        "expected_terms": ["treasury", "yield", "valuation", "growth", "free", "cash"],
    },
]


VARIATION_CONTEXTS = {
    "Baseline": "",
    "Investor due diligence": "forward revenue growth EPS free cash flow valuation margin customer concentration guidance",
    "Macro regime": "interest rates inflation recession probability liquidity credit spreads dollar oil market conditions",
    "Technical implementation": "methods data sources model assumptions evaluation harness benchmark reproducibility",
    "Risk and counterargument": "risks constraints downside scenario criticism uncertainty sensitivity analysis",
    "Recent market evidence": "latest data recent report current trend 2026 market expectations",
}


@dataclass(frozen=True)
class SearchConfig:
    query: str
    result_count: int
    recency_weight: float
    semantic_weight: float
    freshness_half_life_days: int
    use_demo: bool
    api_key: str


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17212b;
            --muted: #607080;
            --line: #d7dee6;
            --blue: #2f6f9f;
            --green: #2f8f6f;
            --amber: #bd7a1f;
            --red: #bf4e45;
        }

        .stApp {
            color: var(--ink);
            background: linear-gradient(180deg, #f8fafb 0%, #eef3f1 52%, #f7f4ee 100%);
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid var(--line);
        }

        [data-testid="stHeader"] {
            background: rgba(248, 250, 251, 0.94);
        }

        h1, h2, h3, p, div, span, label {
            letter-spacing: 0;
        }

        h1 {
            font-size: clamp(2rem, 3vw, 3.1rem);
            line-height: 1.05;
        }

        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        .stTabs [data-baseweb="tab-panel"] {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.8rem;
        }

        .note {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .summary {
            border-left: 5px solid var(--blue);
            background: rgba(255, 255, 255, 0.74);
            padding: 0.85rem 1rem;
            border-radius: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_api_key() -> str:
    env_key = os.getenv("EXA_API_KEY", "")
    secret_key = ""
    try:
        secret_key = st.secrets.get("EXA_API_KEY", "")
    except Exception:
        secret_key = ""
    sidebar_key = st.sidebar.text_input("Exa API key", type="password", value="")
    return sidebar_key or env_key or secret_key


def normalize_text(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def generate_query_variations(query: str, selected_contexts: Iterable[str]) -> pd.DataFrame:
    rows = []
    clean_query = " ".join(query.split())
    for context_name in selected_contexts:
        context_terms = VARIATION_CONTEXTS.get(context_name, "")
        varied_query = clean_query if not context_terms else f"{clean_query} {context_terms}"
        rows.append(
            {
                "Context": context_name,
                "Query": varied_query,
                "Added terms": context_terms,
                "Token count": len(normalize_text(varied_query)),
            }
        )
    return pd.DataFrame(rows)


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def recency_score(published_date: str | None, half_life_days: int) -> float:
    parsed = parse_date(published_date)
    if parsed is None:
        return 0.45
    now = datetime.now(timezone.utc)
    age_days = max((now - parsed).days, 0)
    return float(np.exp(-np.log(2) * age_days / max(half_life_days, 1)))


def lexical_score(query: str, title: str, text: str) -> float:
    q_terms = normalize_text(query)
    if not q_terms:
        return 0.0
    body_terms = normalize_text(f"{title} {text}")
    overlap = len(q_terms & body_terms)
    return overlap / len(q_terms)


def probability_score(row: pd.Series, query: str, recency_weight: float, semantic_weight: float, half_life_days: int) -> float:
    exa_score = float(row.get("score", 0.5) or 0.5)
    lexical = lexical_score(query, str(row.get("title", "")), str(row.get("text", "")))
    freshness = recency_score(row.get("publishedDate"), half_life_days)
    semantic_component = semantic_weight * exa_score + (1 - semantic_weight) * lexical
    raw = recency_weight * freshness + (1 - recency_weight) * semantic_component
    return float(np.clip(raw, 0, 1))


def call_exa_search(config: SearchConfig) -> List[Dict[str, Any]]:
    if config.use_demo or not config.api_key:
        return DEMO_RESULTS[: config.result_count]

    payload = {
        "query": config.query,
        "numResults": config.result_count,
        "contents": {"text": True},
    }
    headers = {
        "x-api-key": config.api_key,
        "Content-Type": "application/json",
    }
    response = requests.post("https://api.exa.ai/search", json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])


def results_frame(results: List[Dict[str, Any]], config: SearchConfig) -> pd.DataFrame:
    rows = []
    for item in results:
        text_value = item.get("text", "")
        if isinstance(text_value, dict):
            text_value = text_value.get("text", "")
        rows.append(
            {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "publishedDate": item.get("publishedDate") or item.get("published_date"),
                "score": item.get("score", 0.5),
                "text": str(text_value)[:1200],
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["title", "url", "publishedDate", "score", "text", "probability", "rank"])
    df["probability"] = df.apply(
        probability_score,
        axis=1,
        query=config.query,
        recency_weight=config.recency_weight,
        semantic_weight=config.semantic_weight,
        half_life_days=config.freshness_half_life_days,
    )
    total = df["probability"].sum()
    if total > 0:
        df["probability"] = df["probability"] / total
    df["rank"] = df["probability"].rank(ascending=False, method="first").astype(int)
    return df.sort_values("probability", ascending=False)


def evaluate_results(df: pd.DataFrame, expected_terms: Iterable[str]) -> pd.DataFrame:
    terms = [term.lower() for term in expected_terms]
    if df.empty:
        return pd.DataFrame(
            [["Result availability", 0, ">= 3", "Fail"], ["Expected term coverage", 0, ">= 0.45", "Fail"]],
            columns=["Evaluation", "Value", "Target", "Result"],
        )
    combined = " ".join(df.head(5)[["title", "text"]].fillna("").agg(" ".join, axis=1).tolist()).lower()
    coverage = sum(1 for term in terms if term in combined) / max(len(terms), 1)
    probability_mass_top3 = df.head(3)["probability"].sum()
    diversity = df.head(5)["url"].map(lambda url: re.sub(r"^https?://(www\.)?", "", str(url)).split("/")[0]).nunique()
    rows = [
        ["Result availability", len(df), ">= 3", "Pass" if len(df) >= 3 else "Warn" if len(df) else "Fail"],
        ["Expected term coverage", coverage, ">= 0.45", "Pass" if coverage >= 0.45 else "Warn" if coverage >= 0.25 else "Fail"],
        ["Top-3 probability mass", probability_mass_top3, "0.45 to 0.85", "Pass" if 0.45 <= probability_mass_top3 <= 0.85 else "Warn"],
        ["Source diversity", diversity, ">= 2", "Pass" if diversity >= 2 else "Warn"],
    ]
    eval_df = pd.DataFrame(rows, columns=["Evaluation", "Value", "Target", "Result"])
    eval_df["Value"] = eval_df["Value"].map(lambda value: round(float(value), 3))
    return eval_df


def eval_quality_score(eval_df: pd.DataFrame) -> float:
    if eval_df.empty:
        return 0.0
    result_points = {"Pass": 1.0, "Warn": 0.55, "Fail": 0.0}
    result_score = eval_df["Result"].map(result_points).fillna(0).mean() * 100
    metric_bonus = 0.0
    for row in eval_df.itertuples(index=False):
        if row.Evaluation == "Expected term coverage":
            metric_bonus += min(float(row.Value), 1.0) * 12
        elif row.Evaluation == "Source diversity":
            metric_bonus += min(float(row.Value) / 5, 1.0) * 6
        elif row.Evaluation == "Top-3 probability mass":
            metric_bonus += (1 - abs(float(row.Value) - 0.65)) * 5
    return round(float(np.clip(result_score + metric_bonus, 0, 100)), 2)


def run_variation_harness(config: SearchConfig, selected_contexts: Iterable[str], expected_terms: Iterable[str]) -> pd.DataFrame:
    rows = []
    variations = generate_query_variations(config.query, selected_contexts)
    for variation in variations.to_dict("records"):
        varied_config = SearchConfig(
            query=variation["Query"],
            result_count=config.result_count,
            recency_weight=config.recency_weight,
            semantic_weight=config.semantic_weight,
            freshness_half_life_days=config.freshness_half_life_days,
            use_demo=config.use_demo,
            api_key=config.api_key,
        )
        try:
            df = results_frame(call_exa_search(varied_config), varied_config)
            eval_df = evaluate_results(df, expected_terms)
            top_title = "" if df.empty else str(df.iloc[0]["title"])
            rows.append(
                {
                    "Context": variation["Context"],
                    "Query": variation["Query"],
                    "Results": len(df),
                    "Top probability": round(float(df["probability"].max()) if not df.empty else 0, 3),
                    "Coverage": float(eval_df.loc[eval_df["Evaluation"] == "Expected term coverage", "Value"].iloc[0]),
                    "Diversity": float(eval_df.loc[eval_df["Evaluation"] == "Source diversity", "Value"].iloc[0]) if "Source diversity" in set(eval_df["Evaluation"]) else 0,
                    "Quality score": eval_quality_score(eval_df),
                    "Eval summary": eval_df["Result"].value_counts().to_dict(),
                    "Top result": top_title[:120],
                }
            )
        except Exception as error:
            rows.append(
                {
                    "Context": variation["Context"],
                    "Query": variation["Query"],
                    "Results": 0,
                    "Top probability": 0,
                    "Coverage": 0,
                    "Diversity": 0,
                    "Quality score": 0,
                    "Eval summary": str(error),
                    "Top result": "",
                }
            )
    return pd.DataFrame(rows).sort_values("Quality score", ascending=False)


def run_eval_suite(api_key: str, use_demo: bool) -> pd.DataFrame:
    rows = []
    for case in EVAL_QUERIES:
        config = SearchConfig(
            query=case["query"],
            result_count=6,
            recency_weight=0.25,
            semantic_weight=0.75,
            freshness_half_life_days=120,
            use_demo=use_demo,
            api_key=api_key,
        )
        try:
            df = results_frame(call_exa_search(config), config)
            eval_df = evaluate_results(df, case["expected_terms"])
            status = "Pass" if "Fail" not in set(eval_df["Result"]) else "Fail"
            rows.append(
                {
                    "Query": case["query"],
                    "Status": status,
                    "Results": len(df),
                    "Top probability": round(float(df["probability"].max()) if not df.empty else 0, 3),
                    "Eval summary": eval_df["Result"].value_counts().to_dict(),
                }
            )
        except Exception as error:
            rows.append(
                {
                    "Query": case["query"],
                    "Status": "Error",
                    "Results": 0,
                    "Top probability": 0,
                    "Eval summary": str(error),
                }
            )
    return pd.DataFrame(rows)


def plot_probabilities(df: pd.DataFrame) -> px.bar:
    frame = df.copy()
    frame["label"] = frame["title"].str.slice(0, 72)
    fig = px.bar(
        frame.sort_values("probability"),
        x="probability",
        y="label",
        orientation="h",
        color="probability",
        color_continuous_scale=[[0, PALETTE["red"]], [0.55, PALETTE["amber"]], [1, PALETTE["green"]]],
        title="Probabilistic return distribution",
    )
    fig.update_layout(xaxis_title="Probability mass", yaxis_title="", coloraxis_showscale=False, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def plot_eval(eval_df: pd.DataFrame) -> px.bar:
    fig = px.bar(
        eval_df,
        x="Value",
        y="Evaluation",
        orientation="h",
        color="Result",
        color_discrete_map={"Pass": PALETTE["green"], "Warn": PALETTE["amber"], "Fail": PALETTE["red"]},
        title="Search evaluation",
    )
    fig.update_layout(xaxis_title="Value", yaxis_title="", margin=dict(l=20, r=20, t=60, b=20))
    return fig


def plot_variations(variation_df: pd.DataFrame) -> px.bar:
    fig = px.bar(
        variation_df.sort_values("Quality score"),
        x="Quality score",
        y="Context",
        orientation="h",
        color="Coverage",
        color_continuous_scale=[[0, PALETTE["red"]], [0.55, PALETTE["amber"]], [1, PALETTE["green"]]],
        title="Query variation quality by context",
        hover_data=["Top probability", "Diversity", "Results"],
    )
    fig.update_layout(xaxis_title="Quality score", yaxis_title="", margin=dict(l=20, r=20, t=60, b=20))
    return fig


def get_config() -> SearchConfig:
    st.sidebar.header("Exa Search")
    api_key = get_api_key()
    use_demo = st.sidebar.toggle("Use demo data", value=not bool(api_key))
    query = st.sidebar.text_area(
        "Search query",
        value="AI data center power demand grid investment transformers switchgear",
        height=90,
    )
    result_count = st.sidebar.slider("Results", 3, 20, 8, 1)
    recency_weight = st.sidebar.slider("Recency weight", 0.0, 1.0, 0.25, 0.05)
    semantic_weight = st.sidebar.slider("Exa semantic score weight", 0.0, 1.0, 0.75, 0.05)
    freshness_half_life_days = st.sidebar.slider("Freshness half-life days", 7, 730, 120, 7)
    return SearchConfig(
        query=query,
        result_count=result_count,
        recency_weight=recency_weight,
        semantic_weight=semantic_weight,
        freshness_half_life_days=freshness_half_life_days,
        use_demo=use_demo,
        api_key=api_key,
    )


def main() -> None:
    inject_theme()
    config = get_config()

    st.title("Exa Probabilistic Search Lab")
    st.markdown(
        """
        Search with Exa, transform results into a probability-weighted return distribution, and evaluate
        whether the retrieved evidence covers the expected concepts. Use demo mode for local testing or
        provide `EXA_API_KEY` through the sidebar, environment, or Streamlit secrets.
        """
    )

    mode_label = "demo data" if config.use_demo or not config.api_key else "live Exa API"
    st.markdown(f"<div class='summary'>Current mode: <b>{mode_label}</b>. Query: <b>{config.query}</b></div>", unsafe_allow_html=True)
    st.write("")

    try:
        df = results_frame(call_exa_search(config), config)
        expected_terms = normalize_text(config.query)
        eval_df = evaluate_results(df, expected_terms)
    except Exception as error:
        st.error(f"Search failed: {error}")
        st.stop()

    selected_contexts = st.sidebar.multiselect(
        "Variation contexts",
        options=list(VARIATION_CONTEXTS.keys()),
        default=["Baseline", "Investor due diligence", "Macro regime", "Risk and counterargument"],
    )
    if not selected_contexts:
        selected_contexts = ["Baseline"]
    variation_df = run_variation_harness(config, selected_contexts, expected_terms)
    best_context = variation_df.iloc[0]["Context"] if not variation_df.empty else "n/a"

    metric_cols = st.columns(5)
    metric_cols[0].metric("Results", len(df))
    metric_cols[1].metric("Top probability", f"{df['probability'].max():.1%}" if not df.empty else "0.0%")
    metric_cols[2].metric("Eval pass", int((eval_df["Result"] == "Pass").sum()))
    metric_cols[3].metric("Best context", best_context)
    metric_cols[4].metric("Mode", "Demo" if config.use_demo or not config.api_key else "Live")

    tabs = st.tabs(["Search", "Probabilities", "Variations", "Evaluation", "Eval Suite", "Iteration Guide", "Data"])

    with tabs[0]:
        for row in df.itertuples(index=False):
            st.markdown(f"### {row.rank}. [{row.title}]({row.url})")
            st.caption(f"Published: {row.publishedDate or 'Unknown'} | Exa score: {float(row.score):.3f} | Probability: {row.probability:.1%}")
            st.write(str(row.text)[:500])

    with tabs[1]:
        if df.empty:
            st.info("No results to plot.")
        else:
            st.plotly_chart(plot_probabilities(df), width="stretch")
            st.dataframe(df[["rank", "title", "url", "publishedDate", "score", "probability"]], width="stretch", hide_index=True)

    with tabs[2]:
        st.plotly_chart(plot_variations(variation_df), width="stretch")
        st.dataframe(variation_df, width="stretch", hide_index=True)
        if not variation_df.empty:
            best = variation_df.iloc[0]
            st.markdown(
                f"<div class='summary'>Best variation: <b>{best['Context']}</b> with quality score "
                f"<b>{best['Quality score']:.1f}</b>. Use this query when coverage rises without collapsing "
                f"source diversity or over-concentrating probability mass.</div>",
                unsafe_allow_html=True,
            )

    with tabs[3]:
        st.plotly_chart(plot_eval(eval_df), width="stretch")
        st.dataframe(eval_df, width="stretch", hide_index=True)
        st.markdown(
            """
            <p class='note'>
            Probability is a normalized blend of Exa score, query-term overlap, and freshness. The eval checks
            result availability, expected concept coverage, probability concentration, and source diversity.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with tabs[4]:
        suite = run_eval_suite(config.api_key, config.use_demo or not bool(config.api_key))
        st.dataframe(suite, width="stretch", hide_index=True)

    with tabs[5]:
        st.subheader("How To Improve Results Over Iterations")
        st.markdown(
            """
            1. Start with a narrow baseline query that states the decision question.
            2. Add one context at a time: investor due diligence, macro regime, technical evidence, risk, or recency.
            3. Compare quality score, expected-term coverage, source diversity, and top-3 probability mass.
            4. Prefer variations that improve coverage while keeping top-3 probability mass below roughly 85%.
            5. If source diversity falls, remove overly specific brand names or add broader industry language.
            6. If coverage is low, add missing concepts from the eval terms rather than making the whole query longer.
            7. Save the winning query and rerun later with live Exa mode to compare stability over time.
            """
        )
        st.subheader("Iteration Template")
        st.code(
            """Question:
Baseline query:
Context added:
Expected concepts:
Best variation:
What improved:
What got worse:
Next query change:
Decision / research takeaway:""",
            language="text",
        )

    with tabs[6]:
        st.dataframe(df, width="stretch", hide_index=True)
        st.subheader("Variation harness output")
        st.dataframe(variation_df, width="stretch", hide_index=True)
        st.download_button(
            "Download search results",
            data=df.to_csv(index=False),
            file_name="exa_probabilistic_results.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download variation harness",
            data=variation_df.to_csv(index=False),
            file_name="exa_variation_harness.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()

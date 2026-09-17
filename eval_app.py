from __future__ import annotations

from streamlit.testing.v1 import AppTest

from app import EVAL_QUERIES, SearchConfig, call_exa_search, evaluate_results, results_frame, run_eval_suite


def run_model_eval() -> None:
    for case in EVAL_QUERIES:
        config = SearchConfig(
            query=case["query"],
            result_count=6,
            recency_weight=0.25,
            semantic_weight=0.75,
            freshness_half_life_days=120,
            use_demo=True,
            api_key="",
        )
        df = results_frame(call_exa_search(config), config)
        eval_df = evaluate_results(df, case["expected_terms"])

        assert not df.empty, f"{case['query']}: expected demo results"
        assert abs(df["probability"].sum() - 1) < 1e-6, f"{case['query']}: probabilities must sum to 1"
        assert set(eval_df["Result"]).issubset({"Pass", "Warn", "Fail"}), f"{case['query']}: invalid eval result"
        print(f"{case['query']}: top_probability={df['probability'].max():.3f}; eval={eval_df['Result'].value_counts().to_dict()}")

    suite = run_eval_suite("", True)
    assert len(suite) == len(EVAL_QUERIES), "Eval suite should run all queries"
    print("Eval suite: complete")


def run_streamlit_eval() -> None:
    app_test = AppTest.from_file("app.py")
    app_test.run(timeout=20)
    assert not app_test.exception, [exception.value for exception in app_test.exception]
    print("Streamlit execution: no exceptions")


if __name__ == "__main__":
    run_model_eval()
    run_streamlit_eval()

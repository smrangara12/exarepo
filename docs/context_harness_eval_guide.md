# Context, Harness, And Eval Guide

This project is more than a search UI. It is a small experimentation system for
improving AI-assisted research quality over repeated iterations.

The core idea is simple:

```text
Context variation -> measured harness run -> eval feedback -> next better query
```

Instead of guessing whether a search query is good, the app generates query
variations, scores the returned evidence, and shows which variation improved
coverage, diversity, freshness, and probability distribution.

## How Context Improves Outcomes

Context tells the model and search system what kind of evidence matters.

In this project, the same baseline question can be expanded through different
contexts:

- `Investor due diligence`: growth, free cash flow, valuation, margin, guidance,
  customer concentration.
- `Macro regime`: rates, inflation, recession risk, liquidity, credit spreads,
  dollar strength, oil, and market conditions.
- `Technical implementation`: method, data source, benchmark, model assumption,
  reproducibility.
- `Risk and counterargument`: downside case, uncertainty, sensitivity,
  constraints, criticism.
- `Recent market evidence`: current reports, latest data, recent trends.

Each context changes retrieval behavior. For example, a general query such as
`AI data center power demand` may find broad articles. Adding investor context
can surface valuation and cash-flow evidence. Adding risk context can surface
regulatory, financing, or local opposition concerns.

Good context improves outcomes by:

- Reducing ambiguity in the search intent.
- Making hidden requirements explicit.
- Pulling in missing dimensions such as risk, recency, or financial quality.
- Helping the eval determine whether the results answer the actual decision
  question.

## How The Harness Improves Outcomes

The harness is the repeatable test loop.

In the app, the variation harness:

1. Starts with the baseline query.
2. Generates context-specific query variants.
3. Runs each variant through the same scoring pipeline.
4. Measures result count, concept coverage, source diversity, top probability,
   and quality score.
5. Ranks variations so the user can see which query formulation works best.

This matters because individual search results are noisy. A single query can
look good by accident. A harness makes the process repeatable.

The harness improves outcomes by:

- Comparing variations under the same conditions.
- Preventing overreaction to one impressive result.
- Revealing when a query is too narrow or too broad.
- Making improvement measurable rather than subjective.
- Creating a record of what changed between iterations.

## How Evals Improve Outcomes

Evals turn output quality into observable signals.

This project uses simple but useful evals:

- `Result availability`: did the search return enough material?
- `Expected term coverage`: did top results include the core concepts?
- `Top-3 probability mass`: is probability too concentrated or too diffuse?
- `Source diversity`: are top results spread across multiple sources?
- `Quality score`: an aggregate signal for comparing query variations.

These evals are intentionally lightweight. They do not claim to prove truth.
They help answer a narrower question:

```text
Did this search formulation retrieve useful, diverse, relevant evidence?
```

Evals improve outcomes by:

- Catching weak or empty result sets quickly.
- Making missing concepts visible.
- Penalizing over-concentrated results.
- Encouraging broader evidence gathering.
- Giving the user a practical stopping rule.

## Improvement Loop In This Project

Use this loop when analyzing a topic:

1. Define the research question.
2. Run the baseline query.
3. Select several contexts in the sidebar.
4. Compare the `Variations` tab.
5. Pick the variation with the best quality score.
6. Inspect whether coverage improved without losing diversity.
7. Refine the query and rerun.
8. Save the best query, result table, and harness output.

Use this template after each iteration:

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

## What Better Looks Like

A better iteration usually has:

- Higher expected-term coverage.
- Enough results to compare evidence.
- Multiple source domains in the top results.
- A top-3 probability mass that is not overly concentrated.
- Clearer connection to the decision being researched.

A worse iteration often has:

- Higher top probability but lower source diversity.
- Many results that miss the core expected concepts.
- Results that are current but not relevant.
- Results that are relevant but stale.
- Query wording that accidentally overfits one source or phrase.

## Applying This Pattern Across AI Projects

The same pattern can improve many AI systems, not only search.

### Retrieval-Augmented Generation

Context:
Define user intent, domain, timeframe, source type, and risk sensitivity.

Harness:
Run a fixed set of representative questions through retrieval and generation.

Eval:
Measure citation relevance, answer coverage, hallucination risk, source
diversity, and answer completeness.

### Financial Analysis Agents

Context:
Add market regime, valuation discipline, risk appetite, sector, and investment
horizon.

Harness:
Run the same companies through multiple macro scenarios.

Eval:
Measure factor coverage, downside sensitivity, valuation consistency, FCF
discipline, and recommendation stability.

### Coding Agents

Context:
Add language, framework, architecture constraints, testing expectations, and
deployment environment.

Harness:
Run the agent against representative issues or feature requests.

Eval:
Measure test pass rate, code quality, regression risk, build success, security
issues, and diff size.

### Customer Support Agents

Context:
Add product area, customer tier, policy constraints, sentiment, and escalation
rules.

Harness:
Replay historical support tickets or synthetic test conversations.

Eval:
Measure correctness, policy compliance, empathy, resolution rate, escalation
accuracy, and response latency.

### Research Assistants

Context:
Add field, evidence standard, timeframe, source credibility, and opposing-view
requirements.

Harness:
Run repeated research prompts with controlled variations.

Eval:
Measure coverage, source quality, contradiction handling, novelty, and
traceability.

## General AI Project Recipe

For any AI project, use this recipe:

1. Define the desired outcome.
2. Identify the context dimensions that change quality.
3. Generate controlled variations across those dimensions.
4. Run each variation through a harness.
5. Evaluate outputs using measurable criteria.
6. Compare results, not impressions.
7. Keep the winning variant and document why it improved.
8. Add new eval cases when the system fails in a new way.

## Why This Matters

AI systems often fail because the prompt or query is under-specified, and the
team has no repeatable way to measure improvement. Context, harnesses, and evals
solve different parts of that problem:

- Context improves the input.
- The harness makes experiments repeatable.
- Evals make quality visible.

Together, they create an improvement system. That is the main lesson of this
project.

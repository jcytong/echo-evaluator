# What does Echo do?

Echo is an evaluation tool to assess B2B software companies in order to understand if there potential to build a company leveraging 2nd mover advantage. 

# How it works
-  Accept company data from a pre-enriched JSON blob
- Use LLM + web search to autonomously score each company across 7 strategic axes
- Output scores, rationale, and insights to a structured format (e.g. JSON)


# Inputs

JSON blob from PeopleDataLabs
 - Includes founding year, headcount growth, org structure, roles, tags, location, etc.

# Evaluation Dimensions & Rubrics

Each dimension returns:
- Score (0–3)
- Written rationale

## Dimensions
| Dimension | Description / Criteria |
|-----------|------------------------|
| Founder Edge | Do the founders have insider advantage (domain, access, prior success)? |
| Novel Wedge | Has the company discovered a new problem or go-to-market made possible by recent change (tech, cultural, regulatory)? |
| Customer Signal | Do public reviews, retention signals, or hiring patterns show clear pain & pull? |
| Sales Motion | Is there evidence of a repeatable, efficient GTM (product-led, SMB, etc.)? |
| Moat Potential | Does the product have signs of accumulating defensibility (workflow depth, data lock-in, etc.)? |
| Investor Behavior | Is the company attracting strong capital from tier-1 or strategically aligned funds? |
| Incumbent Blind Spot | Are larger incumbents ignoring this wedge due to legacy pricing, org structure, or strategic debt? |

# Key Functional Features
**Evaluation Agent (per company)**
- Loads JSON input
    - Using JSON blob from PeopleDataLabs
- Generates prompt per dimension with rubric
- Uses SerpAPI for supplementary web info (e.g., LinkedIn, founder bios, product pages)
- Returns structured scores + reasoning

### ⚙️ Repository Structure & Execution Flow

```text
.
├── main.py                  # Entry-point script – batch-runs evaluations and writes CSV
├── runners/
│   └── evaluate_company.py  # Orchestrates multi-dimension evaluation of a single company
├── agents/
│   ├── base_evaluator.py    # Shared logic for all dimension evaluators
│   ├── evaluators.py        # Concrete subclasses for each of the 7 dimensions
│   ├── rubrics.py           # Natural-language rubrics used by the LLM
│   └── founder_edge_agent.py# (Legacy) stand-alone evaluator example
├── tools/
│   └── search_tool.py       # Thin wrapper around SerpAPI / web search
└── companies.json           # Sample input data (pre-enriched)
```

The **high-level data flow** is:

1. **main.py** parses `companies.json`, normalises company names, and iterates through each record.
2. For every company it calls **runners.evaluate_company.run_evaluation**.
3. `run_evaluation` validates the input, instantiates seven subclasses from **agents.evaluators** (one per dimension), and aggregates their results.
4. Each subclass delegates shared logic to **agents.base_evaluator.BaseEvaluator** which:
   • trims the raw company payload to a compact context window,
   • issues domain-specific web search queries via **tools.search_tool**, and
   • crafts an LLM prompt containing rubric + calibration examples, finally parsing the LLM's textual reply into a numeric **score (1-5)** and **rationale**.
5. The combined results are returned to **main.py** where they are persisted as:
   • a JSON log under `logs/`, and
   • a row in `evaluation_summary.csv` together with selected metadata.

### 🗂️ Detailed File Walkthrough

| File | Purpose | Key Functions / Classes |
|------|---------|-------------------------|
| `main.py` | CLI / batch entry-point. Handles directory setup, loads companies, triggers evaluation, and writes aggregated CSV. | `get_simulated_bulk_data`, `normalize_name_for_file`, main loop |
| `runners/evaluate_company.py` | Single-company orchestrator. Performs validation, invokes all evaluators, times each dimension, and assembles the **Overall** score. | `run_evaluation`, `validate_company_data`, `save_evaluation_log` |
| `agents/base_evaluator.py` | Abstract superclass that encapsulates common evaluator behaviour (prompt construction, web search, LLM call, response parsing). Also holds rich *calibration examples* used inside prompts. | `evaluate`, `search_web`, `trim_company_data` |
| `agents/evaluators.py` | Houses seven concrete subclasses – one per evaluation dimension. Each subclass overrides `get_search_queries` and `trim_company_data` to tailor web searches and context pruning. | `FounderEdgeEvaluator`, `NovelWedgeEvaluator`, … |
| `agents/rubrics.py` | Pure data module with long multi-line strings that define the rubric text injected into prompts. | Constant strings such as `FOUNDER_EDGE_RUBRIC` |
| `agents/founder_edge_agent.py` | Stand-alone legacy script that demonstrates how to build a bespoke agent for a *single* dimension. Redundant now that `agents/evaluators.py` centralises them, but kept for reference. | `FounderEdgeEvaluator` (legacy), `evaluate` helper |
| `tools/search_tool.py` | Simple wrapper around SerpAPI / LangChain tool interface. Allows evaluators to perform live web searches that enrich the LLM context. | `search_tool` |

### 📊 Scoring Scale (updated)
Every dimension now returns **1 – 5** rather than 0 – 3:

| Score | Interpretation |
|-------|----------------|
| 1 | No clear evidence / extremely weak signal |
| 2 | Mild signal present |
| 3 | Solid, defensible evidence of strength |
| 4 | Strong & differentiated indication of advantage |
| 5 | Exceptional, category-defining strength |

The **Overall** score is the arithmetic mean of all successfully evaluated dimensions.

### 🚀 Running Locally

```bash
# Install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Ensure .env contains OPENAI_API_KEY and SERPAPI_API_KEY

# Execute batch evaluation (writes logs/ and evaluation_summary.csv)
python main.py
```

### 📝 Extending or Customising Evaluations
1. **Add a new dimension** – create a new rubric in `agents/rubrics.py`, then subclass `BaseEvaluator` in a new file or extend `agents/evaluators.py` similar to existing evaluators.
2. **Modify prompt logic** – tweak `BaseEvaluator.evaluate` to adjust calibration examples, prompt structure, or parsing heuristics.
3. **Swap search backend** – implement a new tool in `tools/` and replace `search_tool` import in `BaseEvaluator`.

### ℹ️ FAQ
*Why are some scores defaulted to 1?* → Defensive coding: on errors or missing data we return the lowest score to avoid inflating.

*What if the LLM returns an unexpected format?* → Regex-based parsing inside `BaseEvaluator.evaluate` attempts multiple fallbacks and logs warnings.

---

> **Echo** – empowering data-driven, second-mover investment theses.
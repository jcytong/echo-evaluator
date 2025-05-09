🧩 Objective

Build an internal AI agent that takes structured company data (via JSON), performs supplementary web research (via SerpAPI), and scores the company across seven strategic dimensions to assess fast-follower opportunities in B2B SaaS.
🎯 Primary Goals

    Accept company data from a pre-enriched JSON blob

    Use LLM + web search to autonomously score each company across 7 strategic axes

    Output scores, rationale, and insights to a structured format (e.g., Google Sheet or JSON)

👤 Users

    Internal venture studio operators

    Strategic analysts validating startup theses

    Technical founders identifying entry points into emerging markets

📥 Inputs
Field	Description
JSON blob	Includes founding year, headcount growth, org structure, roles, tags, location, etc.
(Optional) notes	Analyst-provided notes or focus areas (e.g. "focus on wedge around async hiring")
🧠 Evaluation Dimensions & Rubrics

Each dimension returns:

    Score (0–3)

    1–2 sentence rationale

Dimension	Description / Criteria
1. Founder Edge	Do the founders have insider advantage (domain, access, prior success)?
2. Novel Wedge	Has the company discovered a new problem or go-to-market made possible by recent change (tech, cultural, regulatory)?
3. Customer Signal	Do public reviews, retention signals, or hiring patterns show clear pain & pull?
4. Sales Motion	Is there evidence of a repeatable, efficient GTM (product-led, SMB, etc.)?
5. Moat Potential	Does the product have signs of accumulating defensibility (workflow depth, data lock-in, etc.)?
6. Investor Behavior	Is the company attracting strong capital from tier-1 or strategically aligned funds?
7. Incumbent Blind Spot	Are larger incumbents ignoring this wedge due to legacy pricing, org structure, or strategic debt?
🛠️ Key Functional Features
🎯 Evaluation Agent (per company)

    Loads JSON input

    Generates prompt per dimension with rubric

    Uses SerpAPI for supplementary web info (e.g., LinkedIn, founder bios, product pages)

    Returns structured scores + reasoning
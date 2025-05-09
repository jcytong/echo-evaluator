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

## Dimension  Description / Criteria
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
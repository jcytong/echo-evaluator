from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI
from tools.search_tool import search_tool
import os

def extract_score(response):
    # crude scoring parser, can improve with regex or LLM
    if "3" in response: return 3
    if "2" in response: return 2
    if "1" in response: return 1
    return 0

def evaluate(company_data):
    llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent="zero-shot-react-description",
        verbose=True
    )
    prompt = f"""
    You are a startup analyst evaluating the 'Founder Edge' of a B2B SaaS company.

    Definition:
    Founder Edge is the unique combination of factors that give a founder an advantage over other founders in the same space. The following are examples of Founder Edges:
    - Deep domain expertise
    - Prior startup/operating experience in the same space
    - Significant network access to potential customers, investors, talent and partners
    - Strong personal brand
    - Fundraising credibility
    - Unique cultural fit
    - Exceptional execution skills
    - Unique technical insights
    - Unique customer acquisition insights
    
    Use this rubric:
    - 0: No clear advantage
    - 1: Mild advantage
    - 2: Clear domain edge
    - 3: Strong & unique edge (repeat founder, elite fit)

    Use the provided company information and web search to research founding team and return:
    1. A score for each founder based on the rubric above
    2. A rationale for each score
    3. A short 3-5 sentence summary

    Company Info:
    {company_data}
    """
    result = agent.run(prompt)
    return {
        "score": extract_score(result),
        "rationale": result.strip()
    }

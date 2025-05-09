from agents.founder_edge_agent import evaluate as evaluate_founder_edge

def run_evaluation(company_data):
    return {
        "Founder Edge": evaluate_founder_edge(company_data)
    }

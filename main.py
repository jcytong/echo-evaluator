import sys
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from runners.evaluate_company import run_evaluation

if __name__ == "__main__":
    path = sys.argv[1]
    with open(path) as f:
        company_data = json.load(f)
    results = run_evaluation(company_data)
    print(json.dumps(results, indent=2))

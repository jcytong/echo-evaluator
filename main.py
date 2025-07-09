import sys
import json
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Added imports
import os
import csv

from runners.evaluate_company import run_evaluation

# Added helper function to simulate database fetch
def get_simulated_bulk_data(companies_file_path="companies.json"):
    """
    Simulates fetching bulk data from a database by reading from the specified JSON file.
    The file is expected to be a JSON list, where each element is an object
    containing a "data" key, which in turn holds the company data dictionary.
    This function returns the list of wrapper objects.
    """
    wrapped_company_data_list = []
    try:
        with open(companies_file_path, 'r') as f:
            content_list = json.load(f)

        if not isinstance(content_list, list):
            print(f"Error: Content of {companies_file_path} is not a list as expected.")
            return []

        for item_wrapper in content_list:
            if isinstance(item_wrapper, dict) and "data" in item_wrapper:
                company_data = item_wrapper["data"]
                if isinstance(company_data, dict) and "name" in company_data:
                    wrapped_company_data_list.append(item_wrapper)
                elif isinstance(company_data, dict):
                    print(f"Warning: Company data item in {companies_file_path} is missing a 'name' field: {company_data}")
                else:
                    print(f"Warning: 'data' field in an item in {companies_file_path} is not a dictionary: {item_wrapper}")
            else:
                print(f"Warning: Item in {companies_file_path} does not have the expected structure (object with a 'data' key): {item_wrapper}")
        
        return wrapped_company_data_list

    except FileNotFoundError:
        print(f"Error: {companies_file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {companies_file_path}.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading {companies_file_path}: {e}")
        return []

# Added helper to normalize names for file system
def normalize_name_for_file(name: str) -> str:
    """Normalizes a company name for use as a filename stem."""
    return name.lower().replace(" ", "_").replace(".", "").replace(",", "")


if __name__ == "__main__":
    # Get input filename from command line argument, default to companies.json
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        input_filename = "companies.json"
    
    # Generate output filename based on input filename
    base_name = os.path.splitext(input_filename)[0]  # Remove extension
    csv_output_filename = f"{base_name}_evaluation_summary.csv"
    
    # Create data and logs directories if they don't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    companies_data_list = get_simulated_bulk_data(input_filename)
    all_csv_rows = []

    # Define the fields to be extracted for the CSV, based on Problem.md
    # "name" will be added separately as the first column.
    score_and_rationale_fields = [
        "overall_score",
        "founder_edge_score", "novel_wedge_score", "customer_signal_score",
        "sales_motion_score", "moat_potential_score", "investor_behavior_score",
        "incumbent_blind_spot_score",
        "founder_edge_rationale", "novel_wedge_rationale", "customer_signal_rationale",
        "sales_motion_rationale", "moat_potential_rationale",
        "investor_behavior_rationale", "incumbent_blind_spot_rationale"
    ]

    metadata_fields = [
        "website", "linkedin_url"
    ]

    # Process companies based on slicing (e.g., companies_data_list[2:12])
    for company_data_wrapper in companies_data_list:
        company_data_item = company_data_wrapper.get("data")
        if not company_data_item:
            print("Skipping item due to missing 'data' field:", company_data_wrapper)
            continue
            
        original_name = company_data_item.get("name")
        if not original_name:
            print("Skipping item due to missing 'name':", company_data_item)
            continue

        normalized_base_name = normalize_name_for_file(original_name)

        # Run evaluation
        try:
            evaluation_results = run_evaluation(company_data_item)
        except Exception as e:
            print(f"Error running evaluation for {original_name}: {e}")
            evaluation_results = {field: "ERROR" for field in score_and_rationale_fields}
            if "overall_score" in score_and_rationale_fields: # Ensure overall_score is handled if defined
                 evaluation_results["overall_score"] = "ERROR"
            else: # Fallback if overall_score wasn't in the list for some reason
                 evaluation_results["Overall"] = {"score": "ERROR"} 

        # Save the evaluation results to logs/
        log_file_path = f"logs/{normalized_base_name}.json"
        with open(log_file_path, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        print(f"Saved evaluation log for '{original_name}' to '{log_file_path}'")

        # Prepare data for CSV
        csv_row = {"name": original_name}

        # Extract metadata fields
        for field in metadata_fields:
            csv_row[field] = company_data_item.get(field, "")

        if evaluation_results and isinstance(evaluation_results, dict):
            csv_row["overall_score"] = evaluation_results.get("Overall", {}).get("score")

            def get_nested_value(results_dict, main_key, sub_key):
                return results_dict.get(main_key, {}).get(sub_key)

            csv_row["founder_edge_score"] = get_nested_value(evaluation_results, "Founder Edge", "score")
            csv_row["founder_edge_rationale"] = get_nested_value(evaluation_results, "Founder Edge", "rationale")
            csv_row["novel_wedge_score"] = get_nested_value(evaluation_results, "Novel Wedge", "score")
            csv_row["novel_wedge_rationale"] = get_nested_value(evaluation_results, "Novel Wedge", "rationale")
            csv_row["customer_signal_score"] = get_nested_value(evaluation_results, "Customer Signal", "score")
            csv_row["customer_signal_rationale"] = get_nested_value(evaluation_results, "Customer Signal", "rationale")
            csv_row["sales_motion_score"] = get_nested_value(evaluation_results, "Sales Motion", "score")
            csv_row["sales_motion_rationale"] = get_nested_value(evaluation_results, "Sales Motion", "rationale")
            csv_row["moat_potential_score"] = get_nested_value(evaluation_results, "Moat Potential", "score")
            csv_row["moat_potential_rationale"] = get_nested_value(evaluation_results, "Moat Potential", "rationale")
            csv_row["investor_behavior_score"] = get_nested_value(evaluation_results, "Investor Behavior", "score")
            csv_row["investor_behavior_rationale"] = get_nested_value(evaluation_results, "Investor Behavior", "rationale")
            csv_row["incumbent_blind_spot_score"] = get_nested_value(evaluation_results, "Incumbent Blind Spot", "score")
            csv_row["incumbent_blind_spot_rationale"] = get_nested_value(evaluation_results, "Incumbent Blind Spot", "rationale")
        else:
            for field in score_and_rationale_fields:
                if field not in csv_row: 
                    csv_row[field] = evaluation_results.get(field, "ERROR_FALLBACK") if isinstance(evaluation_results, dict) else "ERROR_UNEXPECTED_RESULTS_TYPE"
        
        all_csv_rows.append(csv_row)

    # Write the compiled CSV file
    csv_headers = ["name"] + metadata_fields + score_and_rationale_fields

    with open(csv_output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_csv_rows)

    print(f"\nProcessing complete. Summary CSV generated: '{csv_output_filename}'")
    print(f"Processed {len(all_csv_rows)} companies.")

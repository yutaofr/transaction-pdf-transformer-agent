import json
import os
from PIL import Image
from pdf2image import convert_from_path

def pdf_to_images(pdf_path):
    """Converts a PDF file to a list of PIL Image objects."""
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF {pdf_path}: {e}")
        return []

def load_existing_results(path="results.json"):
    """Loads existing results from a JSON file if it exists."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing results: {e}")
    return []

def deduplicate_and_merge(existing_data, new_transactions):
    """
    Merges new transactions into existing grouped data, 
    ensuring no duplicate transaction references.
    """
    # Create a set of existing references for fast lookup
    existing_refs = set()
    for account in existing_data:
        for tx in account.get("transactions", []):
            if "reference" in tx:
                existing_refs.add(tx["reference"])

    # Filter out new transactions that already exist
    unique_new = []
    for tx in new_transactions:
        ref = tx.get("reference")
        if ref and ref not in existing_refs:
            unique_new.append(tx)
            existing_refs.add(ref)
        elif not ref:
            # If no reference, we can't safely deduplicate, so we include it
            # (Though the prompt says they should have one)
            unique_new.append(tx)

    print(f"Deduplication: {len(new_transactions) - len(unique_new)} duplicates skipped.")

    # Group the unique new transactions
    if not unique_new:
        return existing_data

    # Add unique_new to existing_data
    merged_map = {acc["account_number"]: acc for acc in existing_data}
    
    for tx in unique_new:
        account_number = tx.get("account_number", "Unknown")
        if account_number not in merged_map:
            merged_map[account_number] = {
                "bank_name": tx.get("bank_name", "Unknown"),
                "account_number": account_number,
                "account_type": tx.get("account_type", "Unknown"),
                "is_pea": tx.get("is_pea", False),
                "transactions": []
            }
        # Update is_pea if not already set (just in case)
        if not merged_map[account_number].get("is_pea") and tx.get("is_pea"):
            merged_map[account_number]["is_pea"] = True
            
        merged_map[account_number]["transactions"].append(tx)

    return list(merged_map.values())

def save_results(data, output_path="results.json"):
    """Saves data to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {output_path}")

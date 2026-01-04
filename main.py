import os
import sys
import argparse
from agent import TransactionParserAgent
from utils import load_existing_results, deduplicate_and_merge, save_results

def main():
    parser = argparse.ArgumentParser(description="PDF Transaction Parser Agent")
    parser.add_argument("--dir", default="./data", help="Directory containing PDF files")
    parser.add_argument("--output", default="results.json", help="Output JSON file")
    args = parser.parse_args()

    input_dir = args.dir
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist. Creating it...")
        os.makedirs(input_dir)
        print(f"Please place PDF files in {input_dir} and run again.")
        return

    # Load existing results for deduplication
    existing_data = load_existing_results(args.output)
    print(f"Loaded {len(existing_data)} account(s) from existing results.")

    # Initialize Agent
    agent = TransactionParserAgent()
    
    all_new_transactions = []

    # Iterate over PDF files
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not files:
        print(f"No PDF files found in {input_dir}.")
        return

    print(f"Found {len(files)} PDF files. Starting processing...")

    for filename in files:
        pdf_path = os.path.join(input_dir, filename)
        print(f"\nProcessing {filename}...")
        transactions = agent.run(pdf_path)
        all_new_transactions.extend(transactions)

    # Deduplicate and merge with existing results
    final_results = deduplicate_and_merge(existing_data, all_new_transactions)

    # Save final JSON
    save_results(final_results, args.output)
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()

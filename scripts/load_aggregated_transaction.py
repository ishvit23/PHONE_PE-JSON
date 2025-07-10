"""
Script to load aggregated transaction data from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts transaction type, count, and amount
- Inserts into aggregated_transactions table
"""
import os
import json
import pymysql  # assuming you're now using PyMySQL

# Establish database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",  # replace with your actual password
    database="phone_pe"
)
cursor = conn.cursor()

# Path to the base directory containing state-wise transaction data
base_path = r"C:\PHONE_PE_INSIGHTS\data\aggregated\transaction\country\india\state"

# Loop through each state directory
for state in os.listdir(base_path):
    state_path = os.path.join(base_path, state)
    if not os.path.isdir(state_path):
        continue  # skip files if any

    # Loop through each year directory within the state
    for year in os.listdir(state_path):
        year_path = os.path.join(state_path, year)
        if not os.path.isdir(year_path):
            continue

        # Loop through each quarter JSON file
        for file in os.listdir(year_path):
            if not file.endswith(".json"):
                continue  # Skip non-JSON files

            try:
                quarter = int(file.replace(".json", ""))
            except ValueError:
                print(f"Skipping invalid file: {file}")
                continue

            file_path = os.path.join(year_path, file)
            with open(file_path, "r") as f:
                try:
                    # Load transaction data from JSON
                    transaction_data = json.load(f)["data"]["transactionData"]
                    for item in transaction_data:
                        txn_type = item["name"]
                        for inst in item["paymentInstruments"]:
                            count = inst["count"]
                            amount = inst["amount"]

                            # Insert data into the aggregated_transactions table
                            cursor.execute("""
                                INSERT INTO aggregated_transactions (
                                    year, quarter, state, transaction_type, transaction_count, transaction_amount
                                ) VALUES (%s, %s, %s, %s, %s, %s)
                            """, (int(year), quarter, state.title(), txn_type, count, amount))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

# Commit all inserts and close the connection
conn.commit()
cursor.close()
conn.close()
print("Aggregated transaction data loaded successfully.")

"""
Script to load aggregated insurance data from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts insurance count and amount
- Inserts into aggregated_insurances table
"""
import os
import json
import pymysql

# Establish database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="phone_pe"
)
cursor = conn.cursor()

# Path to the base directory containing state-wise insurance data
base_path = r"C:\PHONE_PE_INSIGHTS\data\aggregated\insurance\country\india\state"

# Loop through each state directory
for state in os.listdir(base_path):
    state_path = os.path.join(base_path, state)
    if not os.path.isdir(state_path):
        continue  # Skip if not a directory

    # Loop through each year directory within the state
    for year in os.listdir(state_path):
        year_path = os.path.join(state_path, year)
        # Loop through each quarter JSON file
        for file in os.listdir(year_path):
            if not file.endswith(".json"):
                continue  # Skip non-JSON files

            quarter = int(file.replace(".json", ""))
            file_path = os.path.join(year_path, file)

            try:
                with open(file_path, "r") as f:
                    # Load transaction data from JSON
                    data = json.load(f)["data"]["transactionData"]
                    for item in data:
                        for inst in item["paymentInstruments"]:
                            count = inst["count"]
                            amount = inst["amount"]

                            # Insert data into the aggregated_insurances table
                            cursor.execute("""
                                INSERT INTO aggregated_insurances (
                                    year, quarter, state, insurance_count, insurance_amount
                                ) VALUES (%s, %s, %s, %s, %s)
                            """, (
                                int(year), quarter, state.title(), count, amount
                            ))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Commit all inserts and close the connection
conn.commit()
cursor.close()
conn.close()
print("Aggregated insurance data loaded successfully.")
# This script loads aggregated insurance data into the database.
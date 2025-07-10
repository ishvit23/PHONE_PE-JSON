"""
Script to load top transaction data (by pincode) from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts transaction count and amount for top pincodes
- Inserts into top_transactions table
"""
import os
import json
import pymysql

# Connect to MySQL
db_config = dict(
    host="localhost",
    user="root",
    password="root",
    database="phone_pe"
)
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# Path to the base directory containing top transaction data
base_path = r"C:\PHONE_PE_INSIGHTS\data\top\transaction\country\india\state"
seen = set()  # To avoid duplicate inserts

# Loop through each state directory
for state in os.listdir(base_path):
    for year in os.listdir(os.path.join(base_path, state)):
        for file in os.listdir(os.path.join(base_path, state, year)):
            if not file.endswith(".json"):
                continue  # Skip non-JSON files

            try:
                quarter = int(file.replace(".json", ""))
                file_path = os.path.join(base_path, state, year, file)

                with open(file_path, "r") as f:
                    content = json.load(f)

                top_txns = content.get("data", {}).get("pincodes", [])

                for entry in top_txns:
                    region = entry.get("entityName")
                    metric = entry.get("metric", {})
                    count = metric.get("count")
                    amount = metric.get("amount")
                    level_type = "Pincode"

                    key = (year, quarter, state, region)
                    if key in seen or region is None:
                        continue  # Skip duplicates or missing region
                    seen.add(key)

                    # Insert data into the top_transactions table
                    cursor.execute("""
                        INSERT INTO top_transactions (
                            year, quarter, state_or_district_or_pincode,
                            level_type, transaction_count, transaction_amount
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (int(year), quarter, region, level_type, count, amount))

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Commit all inserts and close the connection
conn.commit()
cursor.close()
conn.close()
print(" top_transactions loaded successfully.")
# Note: Ensure the database schema matches the insert statements.
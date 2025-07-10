"""
Script to load top user data (by pincode) from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts registered users for top pincodes
- Inserts into top_users table
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

# Path to the base directory containing top user data
base_path = r"C:\PHONE_PE_INSIGHTS\data\top\user\country\india\state"
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

                top_users = content.get("data", {}).get("pincodes", [])

                for user in top_users:
                    region = user.get("name")
                    count = user.get("registeredUsers")
                    level_type = "Pincode"

                    key = (year, quarter, state, region)
                    if key in seen or region is None or count is None:
                        continue  # Skip duplicates or missing region/count
                    seen.add(key)

                    # Insert data into the top_users table
                    cursor.execute("""
                        INSERT INTO top_users (
                            year, quarter, state_or_district_or_pincode,
                            level_type, registered_users
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (int(year), quarter, region, level_type, count))

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Commit all inserts and close the connection
conn.commit()
cursor.close()
conn.close()
print("top_users loaded successfully.")
# Note: Ensure the database schema matches the insert statements.
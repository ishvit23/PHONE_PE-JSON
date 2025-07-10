"""
Script to load district-level user hover data from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts registered users and app opens for each district
- Inserts into map_users table
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

# Path to the base directory containing user hover data
base_path = r"C:\PHONE_PE_INSIGHTS\data\map\user\hover\country\india\state"

# Loop through each state directory
for state in os.listdir(base_path):
    state_path = os.path.join(base_path, state)
    if not os.path.isdir(state_path):
        continue  # Skip if not a directory

    # Loop through each year directory within the state
    for year in os.listdir(state_path):
        year_path = os.path.join(state_path, year)
        for file in os.listdir(year_path):
            if not file.endswith(".json"):
                continue  # Skip non-JSON files

            quarter = int(file.replace(".json", ""))
            file_path = os.path.join(year_path, file)

            try:
                with open(file_path, "r") as f:
                    # Load hover data for each district
                    hover_data = json.load(f)["data"]["hoverData"]
                    for district, stats in hover_data.items():
                        registered_users = stats["registeredUsers"]
                        app_opens = stats["appOpens"]

                        # Insert data into the map_users table
                        cursor.execute("""
                            INSERT INTO map_users (
                                year, quarter, state, registered_users, app_opens
                            ) VALUES (%s, %s, %s, %s, %s)
                        """, (int(year), quarter, district.title(), registered_users, app_opens))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Commit all inserts and close the connection
conn.commit()
cursor.close()
conn.close()
print("Map user data loaded successfully.")

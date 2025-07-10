"""
Script to load aggregated user data from JSON files into the PhonePe MySQL database.
- Traverses state/year/quarter directories
- Extracts registered users, app opens, and device brand data
- Inserts into aggregated_users table
"""
import os
import json
import pymysql

# Connect to MySQL
db_config = dict(
    host="localhost",
    user="root",
    password="root",  # Replace with your actual password if needed
    database="phone_pe"
)
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# Path to the base directory containing state-wise user data
base_path = r"C:\PHONE_PE_INSIGHTS\data\aggregated\user\country\india\state"

insert_count = 0  # to track inserted rows

# Loop through each state directory
for state in os.listdir(base_path):
    state_path = os.path.join(base_path, state)
    if not os.path.isdir(state_path):
        continue  # Skip if not a directory

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
                file_path = os.path.join(year_path, file)

                with open(file_path, "r") as f:
                    content = json.load(f)

                data = content.get("data", {})
                aggregated = data.get("aggregated", {})
                users_by_device = data.get("usersByDevice", [])

                # Skip files that don't have device data
                if not users_by_device or not isinstance(users_by_device, list):
                    print(f" Skipped: {file_path} (No usersByDevice data)")
                    continue

                reg_users = aggregated.get("registeredUsers", 0)
                app_opens = aggregated.get("appOpens", 0)

                for device in users_by_device:
                    brand = device.get("brand")
                    count = device.get("count", 0)
                    percentage = device.get("percentage", 0.0)

                    # Debug print for each insert
                    print(
                        f"Inserting: Year={year}, Q={quarter}, State={state.title()}, "
                        f"Brand={brand}, Count={count}, %={percentage}"
                    )

                    try:
                        # Insert data into the aggregated_users table
                        cursor.execute("""
                            INSERT INTO aggregated_users (
                                year, quarter, state, registered_users, app_opens,
                                device_brand, device_count, device_percentage
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            int(year), quarter, state.title(),
                            reg_users, app_opens, brand, count, percentage
                        ))
                        insert_count += 1
                    except Exception as e:
                        print(f" Insert failed for {state}, Q{quarter}, {brand}: {e}")

            except Exception as e:
                print(f" Error reading {file_path}: {e}")

# Finalize DB operations
conn.commit()
cursor.close()
conn.close()
print(f"\n Aggregated user data load complete. Total rows inserted: {insert_count}")

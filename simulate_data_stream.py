# simulate_data_stream.py
import csv
import random
import time
import os
from datetime import datetime

file_path = r'C:\Users\user\OneDrive\Desktop\Green Audit report project\energy_data.csv'

# Overwrite the file and write header
with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "Vrms", "Irms"])  # Header in first row

print("Started data simulation... Writing to CSV.")

# Start appending data from second row
while True:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Vrms = round(random.uniform(210, 250), 2)        # Simulated voltage
    Irms = round(random.uniform(0.5, 8.0), 2)        # Simulated current

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, Vrms, Irms])     # Data from 2nd row onwards

    print(f"Logged: {timestamp}, Vrms: {Vrms}, Irms: {Irms}")
    time.sleep(5)  # Log every 5 second

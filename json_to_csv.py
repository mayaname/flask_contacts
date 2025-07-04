"""
Program: Extensions
Author: Maya Name
Creation Date: 05/31/2025
Revision Date: 
Description: Converts a JSON file to a CSV file


Revisions:

"""

import json
import csv

def convert_json_to_csv(json_filepath:str, csv_filepath:str) -> None:
    """
    Converts a JSON file to a CSV file.

    Param: json_filepath - The path to the input JSON file.
    Param: csv_filepath - The path to the output CSV file.
    Return: None

    """
    try:
        with open(json_filepath, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
         print(f"Error: JSON file not found at '{json_filepath}'")
         return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_filepath}'")
        return
    
    if not data:
        print("Error: JSON file is empty.")
        return

    if isinstance(data, dict):
        data = [data]
    
    if not isinstance(data, list):
        print("Error: JSON data should be a list of dictionaries or a dictionary.")
        return

    try:
        with open(csv_filepath, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"An error occurred while writing to the CSV file: {e}")

def main():
    json_filepath = 'employees.json'  
    csv_filepath = 'employees.csv' 

    convert_json_to_csv(json_filepath, csv_filepath)

if __name__ == "__main__":
    main()
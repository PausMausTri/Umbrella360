# This script is used to create an Excel file with Wialon data.
# It logs into Wialon, retrieves unit data, and writes it to an Excel file.
#
# Import necessary libraries
# -*- coding: utf-8 -*-
import requests
import json
from base import wialon_login, wialon_logout, search_units

import openpyxl
from openpyxl import Workbook
import os
import sys

# Define constants
API_URL = "https://hst-api.wialon.com/wialon/ajax.html"
WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc3483B3EF18BC9DEBD2579FA3B321977AF6006F166" # Wialon token
OUTPUT_FILE = "wialon_data.xlsx"  # Output Excel file name
DEPOSITO = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito"


def create_excel_file(data, file_name):
    """
    Create an Excel file and write the data to it.

    Args:
        data (list): List of dictionaries containing unit data.
        file_name (str): Name of the output Excel file.
    """
    # Create a new workbook and select the active worksheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Wialon Data"

    # Write header row
    headers = ["ID", "Name", "Type", "Status"]
    sheet.append(headers)

    # Write data rows
    for unit in data:
        row = [unit.get("id"), unit.get("name"), unit.get("type"), unit.get("status")]
        sheet.append(row)

    # Save the workbook to the specified file
    workbook.save(file_name)
    print(f"INFO: Excel file '{file_name}' created successfully.")
    


#main function to execute the script
def main():
    # print("INFO: Starting Wialon data retrieval...")
    # Log into Wialon and retrieve session ID
    session_id = wialon_login(WIALON_TOKEN)
    if session_id is None:
        print("ERROR: Failed to log into Wialon.")
        sys.exit(1)

    else:
        print(f"INFO: Logged into Wialon with session ID: {session_id}")
    
        # Retrieve unit data from Wialon
        units = search_units(session_id)
        if units is None:
            print("ERROR: Failed to retrieve units.")
            wialon_logout(session_id)
            sys.exit(1)
        else:
            print(f"INFO: Retrieved {len(units)} units from Wialon.")
            # Print unit details for debugging
            for unit in units:
                print(f"Unit ID: {unit.get('id')}, Name: {unit.get('name')}, Type: {unit.get('type')}, Status: {unit.get('status')}")
            # Optionally, you can filter or process the units here
            # For example, you can filter units based on a specific condition
            # units = [unit for unit in units if unit.get('status') == 'active']
            # Return the list of units
            # Create an Excel file and write the unit data to it
            create_excel_file(units, OUTPUT_FILE)
            print(f"INFO: Excel file '{OUTPUT_FILE}' created successfully.")
            # Logout from Wialon
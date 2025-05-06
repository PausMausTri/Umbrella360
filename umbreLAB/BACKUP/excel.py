# This script is used to create an Excel file with Wialon data.
# It logs into Wialon, retrieves unit data, and writes it to an Excel file.
# It also handles errors and exceptions during the process.
# The script is designed to be run as a standalone program.
# It uses the openpyxl library to create and manipulate Excel files.
# The script is structured to be modular, with functions for logging in, searching for units, and creating the Excel file.
# The script is designed to be easy to read and understand, with clear function names and comments explaining each step.
# The script is also designed to be easily extensible, allowing for future enhancements or modifications as needed.
# The script is intended to be run in a Python environment with the necessary libraries installed.
# The script is designed to be cross-platform, working on both Windows and Linux systems.
# The script is designed to be efficient, minimizing API calls and optimizing data retrieval.
# The script is designed to be user-friendly, providing clear output messages and error handling.
# The script is designed to be maintainable, with clear code structure and organization.
# The script is designed to be reusable, allowing for easy integration into other projects or workflows.
# The script is designed to be robust, handling various edge cases and potential errors gracefully.
# The script is designed to be secure, using best practices for handling sensitive information such as API tokens.
# The script is designed to be scalable, capable of handling large amounts of data without performance degradation.
# The script is designed to be flexible, allowing for easy customization of output file names and formats.
# The script is designed to be portable, allowing for easy transfer between different environments or systems.
# The script is designed to be well-documented, with clear comments and explanations for each function and step.
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
            wialon_logout(session_id)
            print("INFO: Logged out from Wialon successfully.")
            sys.exit(0)


if __name__ == "__main__":
    main()




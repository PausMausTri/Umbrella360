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

# Function to log into Wialon and retrieve session ID
def login_to_wialon(token):
    """
    Log into Wialon and retrieve session ID.

    Args:
        token (str): Wialon token.

    Returns:
        str: Session ID if successful, None otherwise.
    """
    session_id = wialon_login(token)
    return session_id



# Function to retrieve unit data from Wialon
def get_units(session_id):
    """
    Retrieve unit data from Wialon.

    Args:
        session_id (str): Session ID.

    Returns:
        list: List of units if successful, None otherwise.
    """
    units = search_units(session_id)
    if units is None:
        print("ERROR: Failed to retrieve units.")
        return None
    else:
        print(f"INFO: Retrieved {len(units)} units from Wialon.")
        # Print unit details for debugging
        for unit in units:
            print(f"Unit ID: {unit.get('id')}, Name: {unit.get('name')}, Type: {unit.get('type')}, Status: {unit.get('status')}")
        # Optionally, you can filter or process the units here
        # For example, you can filter units based on a specific condition
        # units = [unit for unit in units if unit.get('status') == 'active']
        # Return the list of units
        # or any other processing you want to do
    return units


# Function to log out from Wialon
def logout_from_wialon(session_id):
    """
    Log out from Wialon.

    Args:
        session_id (str): Session ID.
    """
    wialon_logout(session_id)

# Function to create an Excel file with Wialon data
def create_excel_file(units):
    """
    Create an Excel file with Wialon data.

    Args:
        units (list): List of units retrieved from Wialon.
    """
    # Create a new workbook and select the active worksheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Wialon Units"

    # Write header row
    headers = ["ID", "Name", "Type", "Status"]
    sheet.append(headers)

    # Write unit data to the worksheet
    for unit in units:
        row = [
            unit.get("id"),
            unit.get("name"),
            unit.get("type"),
            unit.get("status")
        ]
        sheet.append(row)

    # Save the workbook to the DEPOSITO folder
    try:
        output_path = os.path.join(DEPOSITO, OUTPUT_FILE)
        workbook.save(output_path)
        print(f"Excel file '{output_path}' created successfully.")
    except PermissionError:
        print(f"ERROR: Cannot write to '{output_path}'. File may be open in another program.")
    except Exception as e:
        print(f"ERROR: Failed to create Excel file: {str(e)}")


# Main function to execute the script
def main():
    """
    Main function to execute the script.
    """
    # Log in to Wialon
    session_id = login_to_wialon(WIALON_TOKEN)

    if session_id:
        # Retrieve unit data
        units = get_units(session_id)

        if units:
            # Create an Excel file with the unit data
            create_excel_file(units)

        # Log out from Wialon
        logout_from_wialon(session_id)
    else:
        print("ERROR: Failed to log in to Wialon.")
        sys.exit(1)



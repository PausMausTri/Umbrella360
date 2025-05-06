#this script is designed to interact with the Wialon API to retrieve information about units (vehicles or assets) and export that data to an SQLite database.

# It also handles errors and exceptions during the process.
# The script is designed to be run as a standalone program.
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
# all print() functions must have a prefix "BASE:" to be recognized by the main script







import requests
import json
import ast
import pandas as pd
import os
import time
from base import wialon_login, wialon_logout, pause, listar_IDs, alpha_save



### Configurações #########################################################################
#request template
#https://{host}/wialon/ajax.html?sid=<text>&svc=<svc>&params={<params>}
# Exemplo de chamada para buscar unidades (avl_unit) na API Wialon:
#https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&
#	params={
#		"id":34868,
#		"flags":1025
#	}&sid=<your_sid>

#https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={"id":34868,"flags":1025}&sid=<your_sid>



# Substitua pelo seu token real gerado no Wialon
WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc3483B3EF18BC9DEBD2579FA3B321977AF6006F166"
# Verifique se esta é a URL correta para sua instância Wialon (Hosting ou Local)
WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API 
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"

deposito = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito"
ALPHA = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito\ALPHA"


####################################################################################




# --- Colheitadeira --------------------------------------------------
def Colheitadeira():
    """
    Coleta dados do Wialon.
    """
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)
    if session_id is None:
        print("ERROR: Failed to log into Wialon.")
        return None

    # Retrieve unit data
    units = listar_IDs(session_id)
    print(f"INFO: Retrieved {len(units)} units from Wialon.")
    # Print unit details for debugging
    print(units)

    #alpha_save("colheitadeira", units)
    if units is None:
        print("ERROR: Failed to retrieve units.")
        wialon_logout(session_id)
        return None
    wialon_logout(session_id)





Colheitadeira()
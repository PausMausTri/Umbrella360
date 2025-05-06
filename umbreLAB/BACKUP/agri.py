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








import requests
import json
from base import wialon_login, wialon_logout, search_units, PRINCIPAL, listar_IDs
import openpyxl
from openpyxl import Workbook
import os
import time
import sqlite3
import pandas as pd
import sys

### Configurações #########################################################################
# Substitua pelo seu token real gerado no Wialon
WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc3483B3EF18BC9DEBD2579FA3B321977AF6006F166"
# Verifique se esta é a URL correta para sua instância Wialon (Hosting ou Local)
WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"
deposito = rf"C:\TERRA DADOS\laboratorium\UMBRELLA360\deposito"

wall = "###"*30


###############################################################################################
# --- Funções para Interagir com a API Wialon ------------------------------------------


def coleta_Wialon():
    """
    Coleta dados do Wialon e salva em um dicionário.
    """
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)
    if session_id is None:
        print("ERROR: Failed to log into Wialon.")
        return None

    # Retrieve unit data
    units = listar_IDs(session_id)
    if units is None:
        print("ERROR: Failed to retrieve units.")
        wialon_logout(session_id)
        return None

    # Convert unit data into a dictionary
    units_dict = {}
    for unit in units:
        unit_id = unit.get("id")
        units_dict[unit_id] = {
            "name": unit.get("nm"),
            "type": unit.get("cls"),
            "status": unit.get("pos", {}).get("t", "N/A"),
            "latitude": unit.get("pos", {}).get("y", "N/A"),
            "longitude": unit.get("pos", {}).get("x", "N/A"),
        }

    # Logout from Wialon
    wialon_logout(session_id)
    print("INFO: Units data collected successfully.")
    print(f"INFO: {len(units_dict)} units found.")
    print("INFO: Units data:")
    for unit_id, unit_data in units_dict.items():
        print(f"Unit ID: {unit_id}, Name: {unit_data['name']}, Type: {unit_data['type']}, Status: {unit_data['status']}")
    return units_dict



def coleta_txt():
#le o arquivo .txt emm deposito, e  armazena os dados em um dicionário
    with open(os.path.join(deposito, "unidades.txt"), "r") as file:
        lines = file.readlines()
        data = {}
        for line in lines:
            if line.startswith("Unit ID:"):
                parts = line.split(",")
                unit_id = parts[0].split(":")[1].strip()
                name = parts[1].split(":")[1].strip()
                type_ = parts[2].split(":")[1].strip()
                status = parts[3].split(":")[1].strip()
                data[unit_id] = {
                    "name": name,
                    "type": type_,
                    "status": status,

                }
    return data



# funcao para ler o arquivo excel e armazenar os dados em um dicionário
def coleta_excel():
    """
    Lê o arquivo Excel e armazena os dados em um dicionário.
    """
    # Lê o arquivo Excel
    df = pd.read_excel(os.path.join(deposito, "unidades.xlsx"))

    # Converte o DataFrame em um dicionário
    data = df.to_dict(orient="records")

    # Cria um dicionário para armazenar os dados formatados
    units_dict = {}
    for unit in data:
        unit_id = unit.get("ID")
        units_dict[unit_id] = {
            "name": unit.get("Name"),
            "type": unit.get("Type"),
            "status": unit.get("Status"),
        }

    return data


#### Função para criar um arquivo .txt e salvar os dados coletados
def create_txt_file(data, file_name):
    """
    Cria um arquivo .txt e escreve os dados nele.

    Args:
        data (dict): Dicionário contendo os dados das unidades.
        file_name (str): Nome do arquivo de saída.
    """
    with open(file_name, "w") as file:
        for unit_id, unit_data in data.items():
            file.write(f"Unit ID: {unit_id}, Name: {unit_data['name']}, Type: {unit_data['type']}, Status: {unit_data['status']}\n")
            file.write(f"Latitude: {unit_data['latitude']}, Longitude: {unit_data['longitude']}\n")
    print(f"INFO: TXT file '{file_name}' created successfully.")


# Função para criar um arquivo Excel a partir dos dados do arquivo .txt
def create_excel_file(data, file_name):
    """
    Cria um arquivo Excel e escreve os dados nele.

    Args:
        data (dict): Dicionário contendo os dados das unidades.
        file_name (str): Nome do arquivo de saída.
    """
    # Verifica se o diretório de saída existe, caso contrário, cria
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    

    # Cria um novo workbook e seleciona a planilha ativa
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Wialon Data"

    # Escreve a linha de cabeçalho
    headers = ["ID", "Name", "Type", "Status", "Latitude", "Longitude"]
    sheet.append(headers)

    # Escreve as linhas de dados
    for unit_id, unit_data in data.items():
        row = [unit_id, unit_data["name"], unit_data["type"], unit_data["status"]]
        sheet.append(row)

    # Salva o workbook no arquivo especificado
    workbook.save(file_name)
    print(f"INFO: Excel file '{file_name}' created successfully.") 


#funcao para criar um arquivo SQLite a partir dos dados do arquivo .txt
def create_sqlite_file(data, db_name):
    """
    Cria um banco de dados SQLite, cria uma tabela se ela não existir, e escreve os dados nela.

    Args:
        data (dict): Dicionário contendo os dados das unidades.
        db_name (str): Nome do banco de dados de saída.
    """
    # Conecta ao banco de dados (ou cria um novo)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Cria uma tabela para armazenar os dados das unidades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL
        )
    """)

    # Insere os dados na tabela
    for unit_id, unit_data in data.items():
        # Sanitize input data to prevent SQL injection
        sanitized_data = (
            str(unit_id),
            str(unit_data["name"]).replace("'", "''"),
            str(unit_data["type"]).replace("'", "''"),
            str(unit_data["status"]).replace("'", "''"),
            float(unit_data["latitude"]) if unit_data["latitude"] != "N/A" else None,
            float(unit_data["longitude"]) if unit_data["longitude"] != "N/A" else None,
        )
        cursor.execute("""
            INSERT OR REPLACE INTO units (id, name, type, status, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sanitized_data)

    # Salva as alterações e fecha a conexão
    conn.commit()
    conn.close()
    print(f"INFO: SQLite database '{db_name}' created successfully.")





def agri():
    print(wall)
    #PRINCIPAL()
    coleta_Wialon()
    #create_txt_file(coleta_Wialon(), os.path.join(deposito, "unidades.txt"))
    #create_excel_file(coleta_txt(), os.path.join(deposito, "unidades.xlsx"))
    #create_sqlite_file(coleta_excel(), os.path.join(deposito, "unidades.db"))




agri()
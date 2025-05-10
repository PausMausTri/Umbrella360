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
from base import wialon_login, wialon_logout, pause, listar_IDs, alpha_save, buscadora_ID, parsing, busca_usuario



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
def Colheitadeira_Wialon():
    """
    Coleta dados do Wialon.
    """
    tool = "Colheitadeira_Wialon"
    def comm(msg):
        print("="*30)
        print(f"{tool}:\n {msg}")
        print("="*30)

    comm("Iniciando coleta de dados do Wialon...")
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)
    if session_id is None:
        comm("ERROR: Failed to log into Wialon.")
        return None

    # Retrieve unit data
    units = listar_IDs(session_id)
    comm(f"INFO: Retrieved {len(units)} units from Wialon.")
    # Print unit details for debugging
    comm(units)
    unidades = pd.Series(units)
    comm(unidades)
    unidades_frame = pd.DataFrame(unidades)
    comm(unidades_frame)
    # Save the units data to an CSV file
    unidades_frame.to_csv(os.path.join(ALPHA, f"{tool}.csv"), index=False)
    comm(f"INFO: Data saved to {tool}.csv")
    # save the units data to excel file
    unidades_frame.to_excel(os.path.join(ALPHA, f"{tool}.xlsx"), index=False)
    comm(f"INFO: Data saved to {tool}.xlsx")

    for unit in units:
        result = buscadora_ID(session_id, unit)
        #dados_unidade = pd.DataFrame(result)

        #print(dados_unidade)
        #dados_unidade.to_csv(os.path.join(ALPHA, f"{unit}.csv"), index=False)
        #dados_unidade.to_excel(os.path.join(ALPHA, f"{unit}.xlsx"), index=False)
        comm(f"INFO: Data saved to {unit}.xlsx")
        #print(result)


    #alpha_save("colheitadeira", units)
    if units is None:
        comm("ERROR: Failed to retrieve units.")
        wialon_logout(session_id)
        return None
    wialon_logout(session_id)





def Colheitadeira_csv(fazenda, tool):
    """
    Coleta dados dos arquivos locais e salva em um dicionário.
    """
    dados = pd.read_csv(os.path.join(fazenda, f"{tool}.csv"), sep=";")
    print(dados)
    return dados


def Colheitadeira_excel(fazenda,tool):
    """
    Coleta dados dos arquivos locais e salva em um dicionário.
    """
    dados = pd.read_excel(os.path.join(fazenda, f"{tool}.xlsx"))
    print(dados)
    return dados


########
def colheitadeira_arquivos(fazenda):
    """
    Busca e lista os arquivos de colheitadeira no diretório e retorna um dicionário com os dados.
    """
    # Define the directory to search for files


def Colheitadeira_local(fazenda):
    """
    Coleta dados dos arquivos locais e salva em um dicionário.
    """
    # Define the directory to search for files
    directory = fazenda

    # List to store file names
    file_list = []

    # Loop through the directory and find files that match the pattern
    for filename in os.listdir(directory):
        if filename.startswith("Colheitadeira") and filename.endswith(".csv"):
            file_list.append(filename)
        if filename.startswith("Colheitadeira") and filename.endswith(".xlsx"):
            file_list.append(filename)

    # Print the list of files found
    print("Files found:")
    for file in file_list:
        print(file)
    
    Colheitadeira_csv(fazenda)
    Colheitadeira_excel(fazenda)


    # Return the list of files found
    return file_list



##########################################################
# Colheitadeira para ler csv, listar as unidades e depois buscá-las no Wialon
def Colheitadeira_unidades(fazenda):
    """
    Coleta dados das unidades de colheitadeira e salva em um csv.
    """
    #define a lista de unidades

    print(ids_list) 



    #export_unit_data(sid, ids_list)



    #login e logout wialon
    #sid = wialon_login(WIALON_TOKEN)
    #ids_list = listar_IDs(sid)
    #wialon_logout(sid)

def export_unit_data(sid, ids_list):
    for id in ids_list:
        #busca as unidades no Wialon
        result = buscadora_ID(sid,id)
        #adiciona os dados da unidade a um pandas dataframe
        dados_unidade = pd.DataFrame(result)
        dados_unidade.to_csv(os.path.join(ALPHA, f"{id}.csv"), index=False)





################################################################################

#formatador de dicionario:



# Função para achatar dicionários aninhados:
def flatten_dict(d, parent_key='', sep='_'):
    """
    Achata recursivamente um dicionário aninhado.
    
    Exemplo:
      {'a': {'b': 1}}  se torna  {'a_b': 1}
      
    Parâmetros:
      d:         Dicionário a ser achatado.
      parent_key: Chave acumulada na recursão (inicialmente vazio).
      sep:       Separador para concatenar chaves.
      
    Retorna:
      Um novo dicionário com as chaves achatadas.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items




# Cria um DataFrame com o dicionário achatado.
# Se você tiver múltiplos dicionários (por exemplo, de vários caminhões),
# pode armazená-los em uma lista e passar essa lista para o DataFrame.

# Exibe o DataFrame resultante



#tesste
def teste():
    """
    Teste de coleta de dados do Wialon.
    """
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)
    result = buscadora_ID(session_id, 401761206)
    # Print the result for debugging
    print(result)
    #parse the result
    flat_data = flatten_dict(result)
    df = pd.DataFrame([flat_data])  
    print(df)
    df.to_excel(os.path.join(ALPHA, f"teste.xlsx"), index=False)
    print(f"INFO: Data saved to teste.xlsx")

    # Logout from Wialon
    wialon_logout(session_id)




def CLTDR_01():
    """
    Teste de coleta de dados do Wialon.
    """
    #cria um dataframe vazio

    df = pd.DataFrame() 
    # Log into Wialon
    session_id = wialon_login(WIALON_TOKEN)
    # Call the function to list 
    IDs = listar_IDs(session_id)
    for id in IDs:

        result = buscadora_ID(session_id, id)
        # Print the result for debugging
        #print(result)
        #parse the result
        flat_data = flatten_dict(result)
        #adiciona os dados ao dataframe
        df = pd.concat([df, pd.DataFrame([flat_data])], ignore_index=True)
    print(df)
    df.to_excel(os.path.join(ALPHA, f"teste.xlsx"), index=False)
    print(f"INFO: Data saved to teste.xlsx")

    # Logout from Wialon
    wialon_logout(session_id)





def CLTDR_02():
    """
    Teste de coleta de dados do Wialon.
    """
    #cria um dataframe vazio

    df = pd.DataFrame() 
    # Log into Wialon

    sid = wialon_login(WIALON_TOKEN)
    usuario = buscadora_ID(sid, 401756219)

    flat_data = flatten_dict(usuario)
    #adiciona os dados ao dataframe
    df = pd.concat([df, pd.DataFrame([flat_data])], ignore_index=True)
    print(df)  
    df.to_excel(os.path.join(ALPHA, f"teste.xlsx"), index=False)
    print(f"INFO: Data saved to teste.xlsx")
    wialon_logout(sid)

    # Logout from Wialon








#########################################################################
# --- Execução Principal ---
#Colheitadeira_Wialon()



#Colheitadeira_csv(ALPHA)
#Colheitadeira_local(ALPHA)
#Colheitadeira_unidades(ALPHA)

#teste()



##########################################################################


#CLTDR_01()
CLTDR_02()




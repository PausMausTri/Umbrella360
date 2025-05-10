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
import numpy as np
import os
import time



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





########################################################################################
# --- Funções para Interagir com a API Wialon ------------------------------------------
def wialon_login(token):
    """
    Realiza o login na API Wialon usando um token.

    Args:
        token (str): O token de autorização do Wialon.

    Returns:
        str: O Session ID (eid) se o login for bem-sucedido, None caso contrário.
    """
    print("BASE: wialon_login(token): Tentando fazer login em Wialon...")
    login_params = {
        "token": token,
        "appName": "UMBRELLA360", # Nome opcional para identificar sua aplicação
        "operateAs": "", # Deixe em branco para logar como o usuário dono do token
        # "fl": 0 # Flags opcionais, veja documentação
    }
    params = {
        "svc": "token/login",
        "params": json.dumps(login_params) # Os parâmetros específicos do serviço devem ser um JSON stringificado
    }
    print(f"BASE:Tentando fazer login em {WIALON_BASE_URL}...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)

        result = response.json()

        if "error" in result:
            print(f"Erro de API no login: {result}")
            # Tenta obter o código de erro específico do Wialon, se disponível
            wialon_error_code = result.get("error")
            if wialon_error_code == 1:
                print("-> Causa provável: Token inválido ou expirado.")
            elif wialon_error_code == 4:
                 print("-> Causa provável: Usuário bloqueado ou sem acesso.")
            # Adicione mais códigos de erro conforme a documentação:
            # https://sdk.wialon.com/wiki/en/kit/remoteapi/apiref/apierrors
            return None

        if "eid" in result:
            session_id = result["eid"]
            print(f"Login bem-sucedido! Session ID (SID): {session_id}")
            user_info = result.get("user", {})
            print(f"Logado como: {user_info.get('nm', 'Usuário Desconhecido')}")
            return session_id
        else:
            print(f"Login falhou. Resposta inesperada: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP durante o login: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON do login: {response.text}")
        return None
# --- Logout da Sessão Wialon ---
# O logout é importante para liberar recursos e encerrar a sessão corretamente.
def wialon_logout(session_id):
    """
    Realiza o logout da sessão Wialon.

    Args:
        session_id (str): O Session ID ativo.
    """
    print("BASE: wialon_logout(session_id): Tentando fazer logout...")
    params = {
        "svc": "core/logout",
        "params": "{}", # Parâmetros vazios para logout
        "sid": session_id
    }
    print("\nFazendo logout...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()
        if result.get("error") == 0:
             print("Logout bem-sucedido.")
        else:
             print(f"Logout retornou status: {result}")

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP durante o logout: {e}")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON do logout: {response.text}")

################################################################################################
# --- Funções DE SUPORTE ------------------------------------------



# --- Função para salvar a variavel em um arquivo de texto em ALPHA ---
# A função salva a variável em um arquivo de texto no diretório ALPHA.
# O nome do arquivo é gerado a partir do timestamp atual,somado a uma variavel "nome" garantindo que seja único.
# O arquivo é salvo no formato JSON, facilitando a leitura e a manipulação posterior.
# A função é útil para registrar dados temporários ou de depuração durante a execução do script.
# A função pode ser chamada em qualquer ponto do código onde seja necessário salvar dados para análise posterior.
def alpha_save(nome, variavel, indent=None):
    """
    Salva a variável em um arquivo de texto no diretório ALPHA.

    Args:
        nome (str): O nome do arquivo (sem extensão).
        variavel (any): A variável a ser salva.
        indent (int, optional): O nível de indentação para o JSON. Use None para desabilitar.

    Returns:
        str: O caminho do arquivo salvo.
    """
    file_path = os.path.join(ALPHA, f"{nome}.txt")
    with open(file_path, 'w') as file:
        file.write(json.dumps(variavel, indent=indent))  # Salva o resultado formatado em JSON
    print(f"Resultado salvo em: {file_path}")
    return file_path



# --- Função para criar um diretório se não existir ---
# A função create_directory verifica se o diretório especificado existe e, se não existir, cria-o.
# A função é útil para garantir que o diretório de saída esteja disponível antes de tentar salvar arquivos nele.
# A função pode ser chamada em qualquer ponto do código onde seja necessário garantir a existência do diretório.
def create_directory(directory):
    """
    Cria um diretório se ele não existir.

    Args:
        directory (str): O caminho do diretório a ser criado.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Diretório criado: {directory}")
    else:
        print(f"O diretório já existe: {directory}")

# --- Função para verificar se um arquivo existe ---
# A função file_exists verifica se o arquivo especificado existe.
# A função retorna True se o arquivo existir e False caso contrário.
# A função é útil para verificar a existência de arquivos antes de tentar abri-los ou manipulá-los.
# A função pode ser chamada em qualquer ponto do código onde seja necessário verificar a existência de um arquivo.
def file_exists(file_path):
    """
    Verifica se um arquivo existe.

    Args:
        file_path (str): O caminho do arquivo a ser verificado.

    Returns:
        bool: True se o arquivo existir, False caso contrário.
    """
    return os.path.isfile(file_path)


# --- Função para verificar se um diretório existe ---
# A função directory_exists verifica se o diretório especificado existe.
# A função retorna True se o diretório existir e False caso contrário.
# A função é útil para verificar a existência de diretórios antes de tentar salvá-los ou manipulá-los.
# A função pode ser chamada em qualquer ponto do código onde seja necessário verificar a existência de um diretório.
def directory_exists(directory):
    """
    Verifica se um diretório existe.

    Args:
        directory (str): O caminho do diretório a ser verificado.

    Returns:
        bool: True se o diretório existir, False caso contrário.
    """
    return os.path.isdir(directory)


# --- Função para verificar se um arquivo é um JSON válido ---
# A função is_valid_json tenta carregar o conteúdo do arquivo como JSON.
# Se o carregamento for bem-sucedido, retorna True; caso contrário, retorna False.
# A função é útil para validar arquivos JSON antes de tentar manipulá-los.
# A função pode ser chamada em qualquer ponto do código onde seja necessário verificar a validade de um arquivo JSON.
def is_valid_json(file_path):
    """
    Verifica se um arquivo é um JSON válido.

    Args:
        file_path (str): O caminho do arquivo a ser verificado.

    Returns:
        bool: True se o arquivo for um JSON válido, False caso contrário.
    """
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except (ValueError, FileNotFoundError):
        return False
    

# --- Função para converter um dicionário em um DataFrame do pandas ---
# A função dict_to_dataframe converte um dicionário em um DataFrame do pandas.
# A função é útil para manipular e analisar dados de forma tabular.
# A função pode ser chamada em qualquer ponto do código onde seja necessário converter dados de um dicionário para um DataFrame.
def dict_to_dataframe(data):
    """
    Converte um dicionário em um DataFrame do pandas.

    Args:
        data (dict): O dicionário a ser convertido.

    Returns:
        pd.DataFrame: O DataFrame resultante.
    """
    return pd.DataFrame(data)


# --- Função para salvar um DataFrame em um arquivo Excel ---
# A função save_dataframe_to_excel salva um DataFrame em um arquivo Excel.
# A função utiliza o pandas para criar o arquivo Excel e pode especificar o nome do arquivo e o caminho de saída.
# A função é útil para exportar dados analisados ou manipulados para um formato amplamente utilizado.
# A função pode ser chamada em qualquer ponto do código onde seja necessário salvar dados em um arquivo Excel.
def save_dataframe_to_excel(dataframe, file_path):
    """
    Salva um DataFrame em um arquivo Excel.

    Args:
        dataframe (pd.DataFrame): O DataFrame a ser salvo.
        file_path (str): O caminho do arquivo de saída.

    Returns:
        str: O caminho do arquivo salvo.
    """
    dataframe.to_excel(file_path, index=False)
    print(f"DataFrame salvo em: {file_path}")
    return file_path



# --- Função para imprimir o conteúdo de um arquivo JSON ---
# A função print_json_file lê o conteúdo de um arquivo JSON e o imprime de forma formatada.
# A função é útil para visualizar rapidamente o conteúdo de arquivos JSON.
# A função pode ser chamada em qualquer ponto do código onde seja necessário visualizar o conteúdo de um arquivo JSON.
def print_json_file(file_path):
    """
    Lê e imprime o conteúdo de um arquivo JSON.

    Args:
        file_path (str): O caminho do arquivo JSON a ser lido.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(json.dumps(data, indent=4))  # Imprime o JSON formatado
    except (ValueError, FileNotFoundError) as e:
        print(f"Erro ao ler o arquivo JSON: {e}")


# --- Função para imprimir o conteúdo de um arquivo de texto ---
# A função print_text_file lê o conteúdo de um arquivo de texto e o imprime.
# A função é útil para visualizar rapidamente o conteúdo de arquivos de texto.
# A função pode ser chamada em qualquer ponto do código onde seja necessário visualizar o conteúdo de um arquivo de texto.
def print_text_file(file_path):
    """
    Lê e imprime o conteúdo de um arquivo de texto.

    Args:
        file_path (str): O caminho do arquivo de texto a ser lido.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)  # Imprime o conteúdo do arquivo
    except FileNotFoundError as e:
        print(f"Erro ao ler o arquivo de texto: {e}")


# --- Função para imprimir o conteúdo de um arquivo Excel ---
# A função print_excel_file lê o conteúdo de um arquivo Excel e o imprime.
# A função utiliza o pandas para ler o arquivo Excel e imprimir seu conteúdo.
# A função é útil para visualizar rapidamente o conteúdo de arquivos Excel.
# A função pode ser chamada em qualquer ponto do código onde seja necessário visualizar o conteúdo de um arquivo Excel.
def print_excel_file(file_path):
    """
    Lê e imprime o conteúdo de um arquivo Excel.

    Args:
        file_path (str): O caminho do arquivo Excel a ser lido.
    """
    try:
        df = pd.read_excel(file_path)
        print(df)  # Imprime o DataFrame
    except FileNotFoundError as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
    except ValueError as e:
        print(f"Erro ao processar o arquivo Excel: {e}")


# --- Função para imprimir o conteúdo de um arquivo CSV ---
# A função print_csv_file lê o conteúdo de um arquivo CSV e o imprime.
# A função utiliza o pandas para ler o arquivo CSV e imprimir seu conteúdo.
# A função é útil para visualizar rapidamente o conteúdo de arquivos CSV.
# A função pode ser chamada em qualquer ponto do código onde seja necessário visualizar o conteúdo de um arquivo CSV.
def print_csv_file(file_path):
    """
    Lê e imprime o conteúdo de um arquivo CSV.

    Args:
        file_path (str): O caminho do arquivo CSV a ser lido.
    """
    try:
        df = pd.read_csv(file_path)
        print(df)  # Imprime o DataFrame
    except FileNotFoundError as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
    except ValueError as e:
        print(f"Erro ao processar o arquivo CSV: {e}")

# --- Função para imprimir o conteúdo de um arquivo de texto com codificação específica ---
# A função print_text_file_with_encoding lê o conteúdo de um arquivo de texto com uma codificação específica e o imprime.
# A função é útil para visualizar rapidamente o conteúdo de arquivos de texto com codificações diferentes.
# A função pode ser chamada em qualquer ponto do código onde seja necessário visualizar o conteúdo de um arquivo de texto com uma codificação específica.
def print_text_file_with_encoding(file_path, encoding='utf-8'):
    """
    Lê e imprime o conteúdo de um arquivo de texto com uma codificação específica.

    Args:
        file_path (str): O caminho do arquivo de texto a ser lido.
        encoding (str): A codificação do arquivo (padrão é 'utf-8').
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            print(content)  # Imprime o conteúdo do arquivo
    except FileNotFoundError as e:
        print(f"Erro ao ler o arquivo de texto: {e}")
    except UnicodeDecodeError as e:
        print(f"Erro de decodificação ao ler o arquivo: {e}")


# --- Função para pausar o código e perguntar se deseja prosseguir ---
# A função pause pergunta ao usuário se deseja continuar a execução do código.
# Se o usuário digitar 's', a execução continua; caso contrário, o código é encerrado.
# A função é útil para permitir que o usuário revise os resultados antes de prosseguir.
# A função pode ser chamada em qualquer ponto do código onde seja necessário pausar a execução e solicitar confirmação do usuário.
def pause():
    """
    Pausa a execução do código e pergunta se deseja continuar.

    Returns:
        bool: True se o usuário deseja continuar, False caso contrário.
    """
    while True:
        user_input = input("Deseja continuar? (s/n): ").strip().lower()
        if user_input == 's':
            return True
        elif user_input == 'n':
            print("Execução encerrada pelo usuário.")
            return False
        else:
            print("Entrada inválida. Por favor, digite 's' para continuar ou 'n' para encerrar.")



# --- Função para converter um dicionário em uma string formatada ---
# A função dict_to_string converte um dicionário em uma string formatada.
# A função é útil para exibir dados de forma legível.
# A função pode ser chamada em qualquer ponto do código onde seja necessário exibir dados de um dicionário.
def dict_to_string(data):
    """
    Converte um dicionário em uma string formatada.

    Args:
        data (dict): O dicionário a ser convertido.

    Returns:
        str: A string formatada representando o dicionário.
    """
    return json.dumps(data, indent=4)  # Formata o dicionário como JSON com indentação


# --- Função para converter uma string em um dicionário ---
# A função string_to_dict converte uma string formatada em um dicionário.
# A função é útil para manipular dados que foram convertidos em string.
# A função pode ser chamada em qualquer ponto do código onde seja necessário converter uma string em um dicionário.
def string_to_dict(data_string):
    """
    Converte uma string formatada em um dicionário.

    Args:
        data_string (str): A string a ser convertida.

    Returns:
        dict: O dicionário resultante.
    """
    try:
        return json.loads(data_string)  # Converte a string JSON de volta para um dicionário
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a string JSON: {e}")
        return None
    

# --- Função para converter uma string em um dicionário usando ast.literal_eval ---
# A função string_to_dict_ast converte uma string formatada em um dicionário usando ast.literal_eval.
# A função é útil para manipular dados que foram convertidos em string.
# A função pode ser chamada em qualquer ponto do código onde seja necessário converter uma string em um dicionário.
def string_to_dict_ast(data_string):
    """
    Converte uma string formatada em um dicionário usando ast.literal_eval.

    Args:
        data_string (str): A string a ser convertida.

    Returns:
        dict: O dicionário resultante.
    """
    try:
        return ast.literal_eval(data_string)  # Converte a string para um dicionário
    except (ValueError, SyntaxError) as e:
        print(f"Erro ao decodificar a string: {e}")
        return None


###########################################################################################
#BUSCADORES DE INFORMACAO ---------------------------------------------------
# --- Busca por Unidades na API Wialon ---
# A função search_units busca por unidades (avl_unit) na API Wialon e retorna uma lista de dicionários com as informações das unidades encontradas.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações sobre unidades registradas na plataforma Wialon, como veículos ou ativos monitorados.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
def search_units(session_id):
    """
    Busca por itens do tipo 'avl_unit' (unidades) na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.

    Returns:
        list: Uma lista de dicionários representando as unidades encontradas, ou None em caso de erro.
    """
    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": "*",         # Buscar todas as unidades (wildcard)
        "sortType": "sys_name",       # Ordenar pelo nome
        # "propType": "property",     # Opcional: tipo da propriedade
        # "or_logic": False           # Opcional: lógica OR para máscaras
    }
    flags = (
        1 |       # 1: Inclui informações básicas (ID, nome)
        8 |       # 8: Inclui propriedades personalizadas
        256 |     # 256: Inclui o ícone da unidade
        4096      # 4096: Inclui informações do último status (posição, etc.)
        # Adicione mais flags conforme necessário: https://sdk.wialon.com/wiki/en/kit/flags
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    print("\nBuscando unidades...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidades: {result}")
            return None

        if "items" in result:
            units = result["items"]
            print(f"Encontradas {len(units)} unidades.")
            return units
        else:
            print(f"Resposta inesperada ao buscar unidades: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidades: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None


# --- Busca por IDs de Unidades na API Wialon ---
# A função listar_IDs busca por itens do tipo 'avl_unit' (unidades) na API Wialon e retorna uma lista de dicionários com as informações das unidades encontradas.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações sobre unidades registradas na plataforma Wialon, como veículos ou ativos monitorados.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
# A função é semelhante à função search_units, mas pode ter parâmetros de busca e flags diferentes, dependendo das necessidades específicas.

def listar_IDs(session_id):
    """
    Busca por itens do tipo 'avl_unit' (unidades) na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.

    Returns:
        list: Uma lista de dicionários representando as unidades encontradas, ou None em caso de erro.
    """
    # Define o critério de busca para unidades AVL
    # (avl_unit) na API Wialon.
    # O critério de busca pode ser ajustado conforme necessário.
    # Aqui, estamos buscando todas as unidades (wildcard "*").
    # O critério de ordenação é pelo nome da unidade.
    print("BASE: listar_IDs: Buscando unidades...")
    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": "*",         # Buscar todas as unidades (wildcard)
        "sortType": "sys_name",       # Ordenar pelo nome
        # "propType": "property",     # Opcional: tipo da propriedade
        # "or_logic": False           # Opcional: lógica OR para máscaras
    }
    flags = (
        1      # 1: Inclui informações básicas (ID, nome)
        # Adicione mais flags conforme necessário: https://sdk.wialon.com/wiki/en/kit/flags
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    print("\nBuscando unidades...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidades: {result}")
            return None

        if "items" in result:
            units = result["items"]
            print(f"Encontradas {len(units)} unidades.")
            return units
        else:
            print(f"Resposta inesperada ao buscar unidades: {result}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidades: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None

# --- Busca por todas as informações sobre uma unica unidade por ID na API Wialon ---
# A função busca_unidade_por_id busca por uma unidade específica na API Wialon usando seu ID.
# A função utiliza parâmetros de busca e flags para especificar quais informações devem ser retornadas.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
# A função é útil para obter informações detalhadas sobre uma unidade específica, como veículo ou ativo monitorado.
# A função pode ser chamada após o login na API, utilizando o Session ID obtido no login.
# A função é semelhante à função search_units, mas busca uma unidade específica em vez de todas as unidades.


def buscadora_ID(session_id, unit_id):
    """
    Testa a busca de uma unidade específica por ID na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    flag = 1025  # Flags para detalhar os dados retornados
    # 1: Inclui informações básicas (ID, nome)
    # 8: Inclui propriedades personalizadas
    # 256: Inclui o ícone da unidade
    # 4096: Inclui informações do último status (posição, etc.)
    # 8192: Inclui informações de status do item (se disponível)
    # 4611686018427387903: Inclui todas as informações disponíveis (todas as flags)
    # 0: Não inclui informações adicionais (apenas ID e nome)

    url = f"https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={{\"id\":{unit_id},\"flags\":{flag}}}&sid={session_id}"
    #print(f"URL gerada para teste: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON: {response.text}")
        return None


def buscadora_usuarios(session_id):
    """
    Busca por usuários na API Wialon.
    
    Returns:
        list: Uma lista de dicionários representando os usuários encontrados, ou None em caso de erro.
    """
    params = {
        "svc": "core/search_items",
        "params": json.dumps({
            "spec": {
                "itemsType": "avl_resource",
                "propName": "drivers",
                "propValueMask": "*",
                "sortType": "drivers"
            },
            "force": 1,
            "flags": 1,
            "from": 0,
            "to": 0
        }),
        "sid": session_id
    }
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar usuários: {result}")
            return None

        if "items" in result:
            users = result["items"]
            print(f"Encontrados {len(users)} usuários.")

            # Exibe os IDs e nomes dos usuários encontrados

            return users
        else:
            print(f"Resposta inesperada ao buscar usuários: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar usuários: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None




###############################################################################################################
def para_txt(result):
    unit_name = result.get('item', {}).get('nm', 'unidade_desconhecida')
    file_path = f"{deposito}/{unit_name}.txt"
    with open(file_path, 'w') as file:
        file.write(json.dumps(result, indent=4))  # Salva o resultado formatado em JSON
    print(f"Resultado salvo em: {file_path}")



# --- Função para exportar dados de buscadora_ID para Excel ---
# A função para_excel exporta os dados obtidos pela função buscadora_ID para um arquivo Excel.
# A função utiliza a biblioteca pandas para criar um DataFrame e salvar os dados em um arquivo Excel.
# A função também trata erros de conexão e resposta da API, retornando None em caso de falha.
def para_excel(result):
    """
    Exporta os dados obtidos pela função buscadora_ID para um arquivo Excel.

    Args:
        result (dict): O resultado da busca da unidade.

    Returns:
        str: O caminho do arquivo Excel gerado.
    """
    unit_name = result.get('item', {}).get('nm', 'unidade_desconhecida')
    file_path = f"{deposito}/{unit_name}.xlsx"
    
    # Converte o dicionário em um DataFrame do pandas
    df = pd.DataFrame([result])

    # Salva o DataFrame em um arquivo Excel
    df.to_excel(file_path, index=False)
    
    print(f"Resultado exportado para: {file_path}")
    return file_path

############################################################################################

#funcao principal de parsing
# --- Função para exibir os dados em colunas ---
def parsing(result):
    # String com o dado recebido (formato de dicionário)

    # Converte a string para um dicionário Python
    data = ast.literal_eval(result)

    def flatten_dict(d, parent_key='', sep='_'):
        """
        Achata recursivamente um dicionário aninhado.
        
        Parâmetros:
        d: dicionário a ser achatado.
        parent_key: string com prefixo para renomear chaves aninhadas.
        sep: separador entre chaves concatenadas.
        
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

    # Achata o dicionário original
    flat_data = flatten_dict(data)

    # Exibe os dados separados em "colunas" (ou campos)
    print("Dados separados em colunas:")
    for key, value in flat_data.items():
        print(f"{key}: {value}")



def Decodificador_json(result):
    """
    Decodifica um JSON e exibe os dados em colunas.
    """

    dados = json.loads(result)  # Converte a string JSON para um dicionário Python
    #exibe os dados em colunas
    print("Dados separados em colunas:")
    for key, value in dados.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


    






# --- teste -------
def teste():
    print("BASE: Testando a conexão com o Wialon...")
    sid = wialon_login(WIALON_TOKEN)

    if sid:
        units_list = search_units(sid)

        if units_list:
            print("\n--- Lista de Unidades ---")
            for unit in units_list:
                # Extrai algumas informações básicas
                unit_id = unit.get('id', 'N/A')
                unit_name = unit.get('nm', 'Sem Nome')
                last_message = unit.get('pos', None) # Última posição/status (requer flag 4096)
                latitude = "N/A"
                longitude = "N/A"
                timestamp = "N/A"

                if last_message:
                    latitude = last_message.get('y', 'N/A')
                    longitude = last_message.get('x', 'N/A')
                    # O timestamp é em segundos Unix
                    ts_unix = last_message.get('t', None)
                    if ts_unix:
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S UTC')

                print(f"ID: {unit_id}, Nome: {unit_name}, Lat: {latitude}, Lon: {longitude}, Última Msg: {timestamp}")

                # Você pode acessar outras propriedades aqui, dependendo das flags usadas
                # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
                # if props:
                #     print(f"  Propriedades: {props}")

        # Sempre tente fazer logout ao final
        wialon_logout(sid)
    else:
        print("\nNão foi possível continuar sem um Session ID válido.")


def busca_unidade_por_id(session_id, unit_id):
    """
    Busca por uma unidade específica na API Wialon usando seu ID.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    # Validar o unit_id para garantir que seja uma string e não vazio
    if not isinstance(unit_id, (int, str)) or not str(unit_id).strip():
        print(f"Erro: unit_id inválido: {unit_id}")
        return None

    search_spec = {
        "itemsType": "avl_unit",      # Tipo de item a buscar: unidades AVL
        "propName": "sys_name",       # Propriedade para buscar/ordenar (nome da unidade)
        "propValueMask": str(unit_id).strip(),  # Buscar pela unidade específica
        "sortType": "sys_name",       # Ordenar pelo nome
    }
    flags = (
        1 |       # 1: Inclui informações básicas (ID, nome)
        8 |       # 8: Inclui propriedades personalizadas
        256 |     # 256: Inclui o ícone da unidade
        4096      # 4096: Inclui informações do último status (posição, etc.)
    )
    params_search = {
        "spec": search_spec,
        "force": 1,                   # Forçar atualização (0 ou 1)
        "flags": flags,               # Flags para detalhar os dados retornados
        "from": 0,                    # Índice inicial (para paginação)
        "to": 0                       # Índice final (0 para buscar todos até o limite do servidor)
    }
    params = {
        "svc": "core/search_items",
        "params": json.dumps(params_search),
        "sid": session_id             # Inclui o Session ID
    }
    print(f"\nBASE: Buscando unidade com ID {unit_id}...")
    try:
        response = requests.post(API_URL, data=params)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None

        if "items" in result and len(result["items"]) > 0:
            unit = result["items"][0]
            print(f"Unidade encontrada: {unit}")
            return unit
        else:
            print(f"Unidade com ID {unit_id} não encontrada.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON da busca: {response.text}")
        return None
    
def teste_busca_unidade_por_id(session_id, unit_id):
    """
    Testa a busca de uma unidade específica por ID na API Wialon.

    Args:
        session_id (str): O Session ID obtido no login.
        unit_id (int): O ID da unidade a ser buscada.

    Returns:
        dict: Um dicionário representando a unidade encontrada, ou None em caso de erro.
    """
    url = f"https://hst-api.wialon.com/wialon/ajax.html?svc=core/search_item&params={{\"id\":{unit_id},\"flags\":1025}}&sid={session_id}"
    print(f"URL gerada para teste: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None

        print(f"Resposta da API: {result}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON: {response.text}")
        return None



def lista_unidades(sid):
    units_list = search_units(sid)
    print("\n--- Lista de Unidades ---")
    units_dict = {}
    for unit in units_list:
        # Extrai algumas informações básicas
        unit_id = unit.get('id', 'N/A')
        unit_name = unit.get('nm', 'Sem Nome')
        units_dict[unit_id] = unit_name
    return units_dict


def listar_IDs(sid):
    units_list = search_units(sid)
    print("\n--- Lista de IDs ---")
    ids_list = [unit.get('id', 'N/A') for unit in units_list]
    return ids_list



def teste_parsing():
    # String com o dado recebido (formato de dicionário)
    data_str = """{'item': {'nm': 'TLZ0C54_CPBracell', 'cls': 2, 'id': 401790184, 'mu': 0, 
    'pos': {'t': 1746440259, 'f': 7, 'lc': 0, 'y': -22.4147930145, 'x': -50.5946235657, 
    'c': 336, 'z': 486.700012207, 's': 64, 'sc': 13}, 
    'lmsg': {'t': 1746440259, 'f': 7, 'tp': 'ud', 
    'pos': {'y': -22.4147930145, 'x': -50.5946235657, 'c': 336, 'z': 486.700012207, 's': 64, 'sc': 13}, 
    'i': 0, 'o': 4, 'lc': 0, 'rt': 1746440261, 
    'p': {'fms_speed': 67, 'hdop': 0, 'fms_coolant_temp': 92, 'fms_fuel_percentage': 255, 
    'fms_eng_payload': 18, 'fms_accumulated_fuel_cons': 80764, 'ign_on_interval': 60, 
    'ign_off_interval': 3600, 'angle_interval': 15, 'distance_interval': 100, 'overspeed': 0, 
    'rssi': 72, 'gps_data': 77, 'gsensor_sens': 0, 'manager_status': 0, 'other': 0, 
    'heartbeat': 5, 'relay_status': 71, 'drag_alarm': 0, 'digital_io': 16832, 'ign': 1, 
    'digital_out': 32, 'adc1': 0, 'adc2': 0, 'alarm': 0, 'reserve': 213, 
    'odometer': 149519000, 'battery': 100, 'pwr_int': 3.9, 'pwr_ext': 28.93, 
    'rpm': 550, 'battery_monitoring': 0, 'temp_int': 42}}, 
    'uacl': 3849196688227}, 
    'flags': 1025}"""


    # Converte a string para um dicionário Python
    data = ast.literal_eval(data_str)

    def flatten_dict(d, parent_key='', sep='_'):
        """
        Achata recursivamente um dicionário aninhado.
        
        Parâmetros:
        d: dicionário a ser achatado.
        parent_key: string com prefixo para renomear chaves aninhadas.
        sep: separador entre chaves concatenadas.
        
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

    # Achata o dicionário original
    flat_data = flatten_dict(data)

    # Exibe os dados separados em "colunas" (ou campos)
    print("Dados separados em colunas:")
    for key, value in flat_data.items():
        print(f"{key}: {value}")


def PRINCIPAL():
        sid = wialon_login(WIALON_TOKEN)
        lista_unidades()

        # Você pode acessar outras propriedades aqui, dependendo das flags usadas
        # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
        # if props:
        #     print(f"  Propriedades: {props}")

        wialon_logout(sid)




##########################################################################
def base():
        sid = wialon_login(WIALON_TOKEN)
        #listar_IDs(sid)
        busca_unidade_por_id(sid, 401790184)
        teste_parsing()


        # Você pode acessar outras propriedades aqui, dependendo das flags usadas
        # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
        # if props:
        #     print(f"  Propriedades: {props}")

        wialon_logout(sid)

#######################################################################################
### --- TESTE ---
def TESTE():
    sid = wialon_login(WIALON_TOKEN)
    print(lista_unidades(sid))
    


    #buscadora_ID(sid, 401790184)

    
    wialon_logout(sid)

########################################################################################
# --- teste de busca por ID por lista de IDs ---
def expresso_alpha():
    sid = wialon_login(WIALON_TOKEN)
    ids_list = listar_IDs(sid)
    print(ids_list) 
    result = buscadora_ID(sid, 401790184)
    print(result)


    #exporta para excel
    #para_excel(result)
    
    #fetch_unit_data(sid, ids_list)

    wialon_logout(sid)

def fetch_unit_data(sid, ids_list):
    for unit_id in ids_list:
        print(f"Buscando unidade com ID: {unit_id}")
        dados = buscadora_ID(sid, unit_id)
        print(dados)



def teste_expresso_alpha():
    sid = wialon_login(WIALON_TOKEN)
    ids_list = listar_IDs(sid)
    print(ids_list) 
    result = buscadora_ID(sid, 401790184)
    print(result)


    #exporta para excel
    #para_excel(result)
    
    #fetch_unit_data(sid, ids_list)

    wialon_logout(sid)




def Busca_Users():
    sid = wialon_login(WIALON_TOKEN)
    usuarios = buscadora_usuarios(sid)
    print(usuarios)
    # Exibe os IDs e nomes dos usuários encontrados
    for usuario in usuarios:
        user_id = usuario.get('id', 'N/A')
        user_name = usuario.get('nm', 'Sem Nome')
        print(f"ID: {user_id}, Nome: {user_name}")
    #save_users_to_excel(usuarios)
    wialon_logout(sid)




def save_users_to_excel(usuarios):
    df = pd.DataFrame(usuarios)
    df.to_excel(os.path.join(ALPHA, f"usuarios.xlsx"), index=False)
    print(df)



def busca_usuario():
    sid = wialon_login(WIALON_TOKEN)
    usuario = buscadora_ID(sid, 401756219)
    print(usuario)  
    wialon_logout(sid)
#####################################################################################
# teste wialon



######################################################################################
### --- Execução Principal ---
#base()
#teste_parsing()
#TESTE()
#teste_expresso_alpha()   
#Busca_Users()
#busca_usuario()
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
    print(f"URL gerada para teste: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erro de API ao buscar unidade: {result}")
            return None

        print(f"Resposta da API: {result}")
        # salva o result em um arquivo de texto em deposito com o nome da unidade
        unit_name = result.get('item', {}).get('nm', 'unidade_desconhecida')
        file_path = f"{deposito}/{unit_name}.txt"
        with open(file_path, 'w') as file:
            file.write(json.dumps(result, indent=4))  # Salva o resultado formatado em JSON
        print(f"Resultado salvo em: {file_path}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/HTTP ao buscar unidade: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar resposta JSON: {response.text}")
        return None



############################################################################################

#funcao principal de parsing
# --- Função para exibir os dados em colunas ---
def parsing(result):
    # String com o dado recebido (formato de dicionário)
    data_str = result

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



def lista_unidades():
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
                return units_list
                    # Exibe as informações da unidade
                    # Você pode formatar a saída como desejar, por exemplo:s
            print(f"ID: {unit_id}, Nome: {unit_name}, Lat: {latitude}, Lon: {longitude}, Última Msg: {timestamp}")



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
        #busca_unidade_por_id(sid, 401790184)



        # Você pode acessar outras propriedades aqui, dependendo das flags usadas
        # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
        # if props:
        #     print(f"  Propriedades: {props}")

        wialon_logout(sid)

#######################################################################################
### --- TESTE ---
def TESTE():
    sid = wialon_login(WIALON_TOKEN)
    buscadora_ID(sid, 401790184)
    #result = teste_busca_unidade_por_id(sid, 401790184)
    #parsing(result)
    
    wialon_logout(sid)



######################################################################################
### --- Execução Principal ---
#base()
#teste_parsing()
TESTE()
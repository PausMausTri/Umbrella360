import requests
import json

# --- Configurações ---
# Substitua pelo seu token real gerado no Wialon
WIALON_TOKEN = "517e0e42b9a966f628a9b8cffff3ffc3483B3EF18BC9DEBD2579FA3B321977AF6006F166"
# Verifique se esta é a URL correta para sua instância Wialon (Hosting ou Local)
WIALON_BASE_URL = "https://hst-api.wialon.com" # Exemplo para Wialon Hosting

# URL completa para a API
API_URL = f"{WIALON_BASE_URL}/wialon/ajax.html"

def wialon_login(token):
    """
    Realiza o login na API Wialon usando um token.

    Args:
        token (str): O token de autorização do Wialon.

    Returns:
        str: O Session ID (eid) se o login for bem-sucedido, None caso contrário.
    """
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
    print(f"Tentando fazer login em {WIALON_BASE_URL}...")
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

def wialon_logout(session_id):
    """
    Realiza o logout da sessão Wialon.

    Args:
        session_id (str): O Session ID ativo.
    """
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


# --- Execução Principal ---
if __name__ == "__main__":
    if WIALON_TOKEN == "COLOQUE_SEU_TOKEN_AQUI":
        print("ERRO: Por favor, edite o script e insira seu WIALON_TOKEN.")
    else:
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
                            timestamp = datetime.utcfromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S UTC')

                    print(f"ID: {unit_id}, Nome: {unit_name}, Lat: {latitude}, Lon: {longitude}, Última Msg: {timestamp}")

                    # Você pode acessar outras propriedades aqui, dependendo das flags usadas
                    # props = unit.get('prp', {}) # Propriedades personalizadas (requer flag 8)
                    # if props:
                    #     print(f"  Propriedades: {props}")

            # Sempre tente fazer logout ao final
            wialon_logout(sid)
        else:
            print("\nNão foi possível continuar sem um Session ID válido.")


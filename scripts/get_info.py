import requests
from datetime import datetime

def get_subscription_info(api_key):
    base_url = "https://api.elevenlabs.io/v1/user/subscription"
    
    # Cabeçalho com a chave da API
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Realiza a requisição GET para a API
        response = requests.get(base_url, headers=headers)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            data = response.json()

            # Extraindo informações desejadas
            character_count = data.get("character_count")
            character_limit = data.get("character_limit")
            next_reset = data.get("next_character_count_reset_unix")

            # Convertendo o timestamp para data legível
            next_reset_date = datetime.utcfromtimestamp(next_reset).strftime('%Y-%m-%d %H:%M:%S')

            # Imprimindo os resultados
            print(f"Uso atual de caracteres: {character_count}")
            print(f"Limite máximo de caracteres permitido: {character_limit}")
            print(f"Timestamp para quando a contagem de caracteres será redefinida: {next_reset_date} (UTC)")
        else:
            print(f"Erro na requisição: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Um erro ocorreu: {e}")

# Exemplo de uso
api_key = ""  # Substitua pela sua chave da API
get_subscription_info(api_key)

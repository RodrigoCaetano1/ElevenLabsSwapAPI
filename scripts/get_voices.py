import json
from elevenlabs.client import ElevenLabs
from api import all_api

# Função para tentar acessar a API
def access_api(all_api):
    for user, api_key, _, _ in all_api:
        try:
            client = ElevenLabs(api_key=api_key)  # Tenta criar um cliente com a chave atual
            response = client.voices.get_all()    # Tenta obter as vozes
            return response  # Se bem-sucedido, retorna a resposta
        except Exception as e:
            print(f"Erro ao acessar a API com {user}: {e}")  # Exibe erro e tenta a próxima API
    return None  # Se nenhuma API funcionar, retorna None

# Tenta acessar a API usando as chaves na lista
response = access_api(all_api)

if response:  # Verifica se a resposta foi recebida
    # Converter a resposta para uma lista de dicionários (JSON serializável)
    voices_data = []
    for voice in response.voices:
        voice_dict = {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "samples": voice.samples,
            "category": voice.category,
            "fine_tuning": {
                "is_allowed_to_fine_tune": voice.fine_tuning.is_allowed_to_fine_tune,
                "state": voice.fine_tuning.state,
                "verification_failures": voice.fine_tuning.verification_failures,
                "verification_attempts_count": voice.fine_tuning.verification_attempts_count,
                "manual_verification_requested": voice.fine_tuning.manual_verification_requested,
                "language": voice.fine_tuning.language,
                "progress": voice.fine_tuning.progress,
                "message": voice.fine_tuning.message
            },
            "labels": voice.labels,
            "description": voice.description,
            "preview_url": voice.preview_url
        }
        voices_data.append(voice_dict)

    # Salvar em arquivo JSON
    with open('all_voices.json', 'w') as json_file:
        json.dump(voices_data, json_file, indent=4)

    print("Arquivo all_voices.json gerado com sucesso!")
else:
    print("Nenhuma API funcionou.")

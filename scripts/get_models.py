import json
from elevenlabs import ElevenLabs
from api import all_api  # Assumindo que esta lista contenha as APIs como no exemplo anterior

# Função para tentar acessar a API
def access_api(all_api):
    for user, api_key, _, _ in all_api:
        try:
            client = ElevenLabs(api_key=api_key)  # Tenta criar um cliente com a chave atual
            response = client.models.get_all()    # Tenta obter os modelos
            return response  # Se bem-sucedido, retorna a resposta
        except Exception as e:
            print(f"Erro ao acessar a API com {user}: {e}")  # Exibe erro e tenta a próxima API
    return None  # Se nenhuma API funcionar, retorna None

# Tenta acessar a API usando as chaves na lista
response = access_api(all_api)

if response:  # Verifica se a resposta foi recebida
    # Converter a resposta para uma lista de dicionários (JSON serializável)
    models_data = []
    for model in response:
        model_dict = {
            "model_id": model.model_id,
            "name": model.name,
            "can_be_finetuned": model.can_be_finetuned,
            "can_do_text_to_speech": model.can_do_text_to_speech,
            "can_do_voice_conversion": model.can_do_voice_conversion,
            "can_use_style": model.can_use_style,
            "can_use_speaker_boost": model.can_use_speaker_boost,
            "serves_pro_voices": model.serves_pro_voices,
            "token_cost_factor": model.token_cost_factor,
            "description": model.description,
            "requires_alpha_access": model.requires_alpha_access,
            "max_characters_request_free_user": model.max_characters_request_free_user,
            "max_characters_request_subscribed_user": model.max_characters_request_subscribed_user,
            "maximum_text_length_per_request": model.maximum_text_length_per_request,
            "languages": [
                {"language_id": lang.language_id, "name": lang.name} for lang in model.languages
            ],
            "model_rates": model.model_rates,
            "concurrency_group": model.concurrency_group
        }
        models_data.append(model_dict)

    # Salvar em arquivo JSON
    with open('all_models.json', 'w') as json_file:
        json.dump(models_data, json_file, indent=4)

    print("Arquivo all_models.json gerado com sucesso!")
else:
    print("Nenhuma API funcionou.")

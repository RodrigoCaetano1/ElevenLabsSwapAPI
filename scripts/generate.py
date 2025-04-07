import os
import re
import sys
import json
import aiohttp
import requests
from pathlib import Path
from datetime import datetime
import gradio as gr
import asyncio
from scripts.api import all_api

results_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results')))
if not results_dir.exists():
    results_dir.mkdir()

api_status_path = "api_status.json"

async def check_api_status(api_key: str) -> dict:
    """Check the API subscription status and return usage information"""
    base_url = "https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    character_count = data.get("character_count", 0)
                    character_limit = data.get("character_limit", 0)
                    next_reset = data.get("next_character_count_reset_unix")
                    next_reset_date = datetime.utcfromtimestamp(next_reset).strftime('%Y-%m-%d %H:%M:%S')

                    return {
                        "status": "available" if character_count < character_limit else "exhausted",
                        "character_count": character_count,
                        "character_limit": character_limit,
                        "next_reset": next_reset_date,
                        "remaining_chars": character_limit - character_count
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"API Error: {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def update_api_status():
    """Update the status of all APIs"""
    api_status = {}
    for name, api_key, _, _ in all_api:
        status_info = await check_api_status(api_key)
        api_status[name] = {
            "last_used": datetime.now().isoformat(),
            "status": status_info["status"],
            "character_count": status_info.get("character_count"),
            "character_limit": status_info.get("character_limit"),
            "next_reset": status_info.get("next_reset"),
            "remaining_chars": status_info.get("remaining_chars")
        }
    
    with open(api_status_path, 'w') as f:
        json.dump(api_status, f, indent=2)
    
    return api_status

class ElevenLabsTTS:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

    async def generate_tts(self, text: str, voice_id: str, output_filename: str, model_id: str = "eleven_turbo_v2_5", stability: float = 0.5, style: float = 0, similarity_boost: float = 0.75, quality: str = "192") -> tuple:
        # Check if there's enough character limit available
        status_info = await check_api_status(self.api_key)
        if status_info["status"] == "error":
            return False, f"Error checking API status: {status_info['message']}"
        
        if status_info["status"] == "exhausted":
            return False, f"API limit exhausted. Next reset at {status_info['next_reset']}"
        
        # Check if the text length exceeds remaining characters
        if len(text) > status_info["remaining_chars"]:
            return False, f"Text too long for remaining character limit ({status_info['remaining_chars']} characters left)"

        url = f"{self.base_url}/text-to-speech/{voice_id}"
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "style": style,
                "similarity_boost": similarity_boost,
                "use_speaker_boost": True,
                "audio_quality": quality
            }
        }

        output_path = results_dir / output_filename
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                if response.status == 200:
                    audio_content = await response.read()
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    print(f"Áudio gerado com sucesso e salvo em {output_path}")
                    # Update API status after successful generation
                    await update_api_status()
                    return True, str(output_path)
                else:
                    print(f"Erro ao gerar áudio: {response.status}, {await response.text()}")
                    return False, None

async def generate_audio_for_gradio(text: str, voice_id: str, model_id: str, stability: float, style: float, similarity_boost: float) -> tuple:
    sufix_text = re.sub(r'[<>:"/\\|?*]', '_', text[:50]).strip()

    # Get current API status
    api_status = await update_api_status()

    for name, api_key, _, _ in all_api:
        # Check if API has available characters
        current_status = api_status[name]
        if current_status["status"] == "available":
            print(f"\nTentando usar a API: {name} (Caracteres restantes: {current_status['remaining_chars']})")
            tts = ElevenLabsTTS(api_key=api_key)

            output_filename = f'output_{sufix_text}.mp3'

            success, result = await tts.generate_tts(
                text=text,
                voice_id=voice_id,
                output_filename=output_filename,
                model_id=model_id,
                stability=stability,
                style=style,
                similarity_boost=similarity_boost
            )

            if success:
                return True, result, name  # Adicionado o nome da API que teve sucesso
        else:
            print(f"Pulando API {name} - Status: {current_status['status']}")
            print(f"Próxima redefinição em: {current_status['next_reset']}")

    return False, "Todas as APIs falharam ao gerar o áudio.", None

async def generate_audio(text, voice_name, model_id, stability, style, similarity_boost):
    voice_id = voice_dict.get(voice_name)

    if not voice_id:
        raise gr.Error("Erro: voz não encontrada.")

    try:
        for api in all_api:  # Crie uma lista de APIs
            api_key = api[1]
            try:
                success, result = await generate_audio_for_gradio(
                    text=text,
                    voice_id=voice_id,
                    model_id=model_id,
                    stability=stability,
                    style=style,
                    similarity_boost=similarity_boost  # Certifique-se de que esta variável é passada
                )
                return gr.Audio(value=result)
            except Exception as e:
                print(f"Erro ao usar {api[0]}: {str(e)}")
                # Se a API falhar, continua com a próxima API
                continue

        # Se todas as APIs falharem, dê erro
        raise gr.Error("Erro: todas as APIs falharam ao gerar o áudio.")

    except KeyError as e:
        # Captura o erro relacionado à API
        raise gr.Error("Erro: problema com as suas APIs.")

    except Exception as e:
        # Para outros erros, exiba uma mensagem genérica
        raise gr.Error("Erro inesperado. Por favor, tente novamente.")

if __name__ == '__main__':
    asyncio.run(main())

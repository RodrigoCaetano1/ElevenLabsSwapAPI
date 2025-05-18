import json
import subprocess
import asyncio
from scripts.generate import generate_audio_for_gradio, update_api_status
from scripts.api import all_api
import os
import shutil
import gradio as gr

# Função para carregar vozes
def load_voices():
    with open('all_voices.json', 'r') as f:
        voices = json.load(f)

    voice_ids = {voice['name']: voice['voice_id'] for voice in voices}
    return voice_ids

# Função para carregar informações adicionais sobre as vozes
def load_voice_info():
    with open('all_voices.json', 'r') as f:
        voices = json.load(f)

    voice_info = {}
    for voice in voices:
        labels = voice.get('labels', {})
        label_values = [value for key, value in labels.items()]
        full_name = voice['name']
        voice_info[full_name] = {
            "voice_id": voice['voice_id'],
            "labels": label_values,
            "preview_url": voice.get('preview_url', '')
        }

    return voice_info

# Função para exibir informações da voz selecionada
def display_selected_voice(selected_voice):
    voice_info = load_voice_info()

    if isinstance(selected_voice, list):
        selected_voice = selected_voice[0] if selected_voice else None

    if selected_voice and selected_voice in voice_info:
        labels = voice_info[selected_voice]["labels"]
        preview_url = voice_info[selected_voice]["preview_url"]

        info = f"<div style='display: flex; justify-content: space-between; width: 100%;'>" \
               f"<span style='text-align: left;'>{selected_voice}</span>" \
               f"<span style='text-align: right;'>{' | '.join(labels)}</span>" \
               f"</div>"
        return info

    return ""

# Função para atualizar vozes
def update_voices():
    subprocess.run(['python', 'scripts/get_voices.py'])
    return list(load_voices().keys())

# Função para gerar áudio
async def generate_audio(text, voice_name, model_selector, stability, style, similarity_boost):
    print(f"\n=== Iniciando geração de áudio ===")
    print(f"Texto: {text}")
    print(f"Nome da voz: {voice_name}")
    print(f"Modelo selecionado: {model_selector}")
    print(f"Estabilidade: {stability}")
    print(f"Estilo: {style}")
    print(f"Semelhança (similarity boost): {similarity_boost}")

    voice_id = voice_dict.get(voice_name)
    if not voice_id:
        raise gr.Error("Erro: voz não encontrada.")

    try:
        apis = load_apis()
        if not apis:
            raise gr.Error("Erro: nenhuma API configurada.")

        global all_api
        all_api = apis

        print("\n=== APIs disponíveis ===")
        for api_name, api_key, _, _ in apis:
            print(f"API: {api_name}")

        api_status = await update_api_status()

        success, result, successful_api = await generate_audio_for_gradio(
            text=text,
            voice_id=voice_id,
            model_id=model_selector,
            stability=stability,
            style=style,
            similarity_boost=similarity_boost
        )

        if success and successful_api:
            print(f"\n✅ Áudio gerado com sucesso usando API: {successful_api}")
            await update_api_status()
            return gr.Audio(value=result)
        else:
            print("\n❌ Todas as APIs falharam.")
            raise gr.Error("Erro: todas as APIs falharam ao gerar o áudio.")

    except Exception as e:
        error_msg = str(e)
        if "api.py" in error_msg:
            raise gr.Error("Erro ao carregar arquivo de APIs. Verifique as configurações.")
        else:
            raise gr.Error(f"Erro inesperado: {error_msg}")

# Função corrigida para carregar APIs de forma segura
def load_apis():
    with open('scripts/api.py', 'r', encoding='utf-8') as f:
        content = f.read()

    namespace = {}
    try:
        exec(content, namespace)
        return namespace.get('all_api', [])
    except Exception as e:
        raise gr.Error(f"Erro ao carregar API do arquivo api.py: {e}")

# Função para salvar APIs formatadas corretamente
def save_apis(apis):
    with open('scripts/api.py', 'w', encoding='utf-8') as f:
        f.write("all_api = [\n")
        for item in apis:
            f.write(f"    {repr(item)},\n")
        f.write("]\n")

# Função para remover uma API
def remove_api_entry(api_entry):
    if not api_entry:
        raise gr.Error("Selecione uma API para remover")

    apis = load_apis()
    api_name = api_entry.split(": ")[0]

    if not any(name == api_name for name, _, _, _ in apis):
        raise gr.Error("API não encontrada")

    apis = [api for api in apis if api[0] != api_name]
    save_apis(apis)

    api_entries = [f"{name}: {api}" for name, api, _, _ in apis]
    api_list_str = "\n".join(api_entries)

    return (
        gr.update(value=api_list_str),
        gr.update(choices=api_entries, value=None)
    )

def update_api_list():
    api_list = load_apis()
    api_entries = [f"{name}: {api}" for name, api, _, _ in api_list]
    return api_entries, "\n".join(api_entries)

def listar_audios():
    arquivos = [f for f in os.listdir("results") if f.endswith(('.mp3', '.wav'))]
    return arquivos

def tocar_audio(arquivo):
    return f"results/{arquivo}"

def apagar_audios():
    for arquivo in os.listdir("results"):
        file_path = os.path.join("results", arquivo)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return listar_audios(), None

def atualizar_lista():
    return listar_audios()

voice_dict = load_voices()

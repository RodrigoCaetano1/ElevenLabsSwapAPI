import gradio as gr
import json
import subprocess
import asyncio
from scripts.generate import generate_audio_for_gradio, check_api_status
from scripts.api import all_api
import ast
import os
import shutil
from scripts.ui import load_voices, load_voice_info, display_selected_voice, update_voices, generate_audio, load_apis, save_apis, remove_api_entry, update_api_list, listar_audios, tocar_audio, apagar_audios, atualizar_lista

async def update_api_info(text):
    """Atualiza as informações da API atual com base no texto inserido"""
    try:
        chars_count = len(text) if text else 0
        
        # Verifica o status de todas as APIs para encontrar a primeira disponível
        for api_name, api_key, _, _ in all_api:
            api_status = await check_api_status(api_key)
            
            if api_status["status"] == "error":
                continue
                
            used_chars = api_status["character_count"]
            char_limit = api_status["character_limit"]
            remaining_chars = char_limit - used_chars
            
            # Se esta API tem caracteres suficientes disponíveis, use-a
            if remaining_chars >= chars_count:
                info = f"<center>Nome api atual: {api_name} | {chars_count} caracteres | Restante: {remaining_chars} | Uso: {used_chars} | Limite: {char_limit}</center>"
                return info
            else:
                pass
        
        # Se nenhuma API estiver disponível
        return "Nenhuma API com caracteres suficientes disponível"
    except Exception as e:
        return f"Erro ao atualizar informações: {str(e)}"
        
# Modelos disponíveis
AVAILABLE_MODELS = [
    "eleven_monolingual_v1",
    "eleven_multilingual_v1",
    "eleven_multilingual_v2",
    "eleven_turbo_v2",
    "eleven_turbo_v2_5"
]

# Carregar vozes
voice_dict = load_voices()

def tts_tabs():
    gr.Markdown("## Elevenlabs - Gerar Áudio")
            
    with gr.Row():
        text_input = gr.Textbox(
            label="Texto de entrada",
            placeholder="Digite seu texto aqui...",
            lines=5
        )
    
    api_info = gr.Markdown("")
    
    with gr.Row():
        with gr.Column():
            voice_selector = gr.Dropdown(
                label="Selecione a voz",
                choices=list(voice_dict.keys()),
                value=list(voice_dict.keys())[0]
            )
        with gr.Column():
            model_selector = gr.Dropdown(
                label="Selecione o modelo",
                choices=AVAILABLE_MODELS,
                value="eleven_turbo_v2_5"
            )
                
    voice_info = gr.Markdown()
    voice_selector.change(display_selected_voice, inputs=voice_selector, outputs=voice_info)
    
    advanced_toggle = gr.Checkbox(label="Configurações avançadas")
    
    with gr.Row(visible=False) as advanced_settings:
        stability_slider = gr.Slider(
            label="Stability",
            minimum=0.0,
            maximum=1.0,
            value=0.5,
            step=0.01
        )
        style_slider = gr.Slider(
            label="Style",
            minimum=0.0,
            maximum=1.0,
            value=0,
            step=0.01
        )
        similarity_boost_slider = gr.Slider(
            label="Similarity Boost",
            minimum=0.0,
            maximum=1.0,
            value=0.75,
            step=0.01
        )
    
    generate_button = gr.Button("Gerar Áudio")
    output_audio = gr.Audio(label="Áudio Gerado")
    
    def toggle_advanced_settings(show_advanced):
        return gr.update(visible=show_advanced)
    
    text_input.change(
        fn=update_api_info,
        inputs=[text_input],
        outputs=[api_info]
    )

    generate_button.click(
        generate_audio, 
        inputs=[
            text_input,
            voice_selector,
            model_selector,
            stability_slider,
            style_slider,
            similarity_boost_slider
        ],
        outputs=[output_audio]
    ).then(
        fn=update_api_info,
        inputs=[text_input],
        outputs=[api_info]
    )

    with gr.Row():
        update_button = gr.Button("Atualizar vozes")
        send_to_s2s_button = gr.Button("Enviar para S2S")
        
    update_button.click(
        fn=update_voices,
        outputs=voice_selector,
        show_progress=True
    )
    
    advanced_toggle.change(
        toggle_advanced_settings,
        inputs=advanced_toggle,
        outputs=advanced_settings
    )

    return output_audio, send_to_s2s_button
import os
import gradio as gr
from pathlib import Path
import asyncio
from scripts.api import all_api
import aiohttp
import json
from scripts.ui import load_voices, display_selected_voice, update_voices

# Create outputs2s directory if it doesn't exist
outputs2s_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'results')))
if not outputs2s_dir.exists():
    outputs2s_dir.mkdir(parents=True)

# Modelos disponíveis para S2S
AVAILABLE_MODELS = [
    "eleven_english_sts_v2",
    "eleven_multilingual_sts_v2"
]

async def generate_s2s_for_gradio(audio_file, voice_name, model_id, stability, similarity_boost, style):
    """Função principal para gerar áudio usando Speech-to-Speech"""
    try:
        print(f"Starting S2S generation with audio file: {audio_file}")
        
        # Get voice_id from voice_name using the shared load_voices function
        voices = load_voices()
        voice_id = voices.get(voice_name)
        if not voice_id:
            raise gr.Error(f"Voice '{voice_name}' not found")

        # Handle both string paths and UploadedFile objects
        audio_path = audio_file.name if hasattr(audio_file, 'name') else audio_file
        print(f"Processing audio path: {audio_path}")
        
        output_filename = f"s2s_output_{os.path.basename(audio_path)}"
        
        for name, api_key, _, _ in all_api:
            print(f"\nTrying API: {name}")
            
            url = f"https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}/stream"
            
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": api_key
            }

            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }

            # Prepare form data
            form_data = aiohttp.FormData()
            form_data.add_field('model_id', model_id)
            form_data.add_field('voice_settings', json.dumps(voice_settings))
            
            try:
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                    form_data.add_field('audio', audio_data, filename='audio.mp3')
            except Exception as e:
                print(f"Error reading audio file: {e}")
                continue

            output_path = outputs2s_dir / output_filename
            print(f"Output path will be: {output_path}")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=form_data) as response:
                        if response.status == 200:
                            with open(output_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(1024):
                                    f.write(chunk)
                            print(f"Audio generated successfully using API: {name}")
                            return str(output_path)
                        else:
                            error_text = await response.text()
                            print(f"Error with API {name}: {error_text}")
                            continue
            except Exception as e:
                print(f"Error using API {name}: {str(e)}")
                continue

        raise gr.Error("All APIs failed to generate audio")
        
    except Exception as e:
        print(f"Detailed error: {str(e)}")
        raise gr.Error(f"Error generating audio: {str(e)}")

def handle_new_audio_input(audio):
    """Handle incoming audio from TTS tab"""
    print(f"Received new audio in S2S tab: {audio}")
    return audio

def s2s_tab():
    gr.Markdown("## Speech to Speech - Converter Áudio")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="Upload Audio",
                type="filepath",
                interactive=True
            )
            print("S2S audio input component created")

    with gr.Row():
        with gr.Column():
            voice_selector = gr.Dropdown(
                label="Selecione a voz",
                choices=load_voices().keys(),
                value=list(load_voices().keys())[0]
            )
        with gr.Column():
            model_selector = gr.Dropdown(
                label="Selecione o modelo",
                choices=AVAILABLE_MODELS,
                value=AVAILABLE_MODELS[1]
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
            value=0.0,
            step=0.01
        )
        similarity_boost_slider = gr.Slider(
            label="Similarity Boost",
            minimum=0.0,
            maximum=1.0,
            value=0.75,
            step=0.01
        )

    convert_btn = gr.Button("Converter Áudio")
    output_audio = gr.Audio(label="Áudio Convertido")

    def toggle_advanced_settings(show_advanced):
        return gr.update(visible=show_advanced)

    convert_btn.click(
        fn=generate_s2s_for_gradio,
        inputs=[
            audio_input,
            voice_selector,
            model_selector,
            stability_slider,
            similarity_boost_slider,
            style_slider
        ],
        outputs=[output_audio]
    )

    audio_input.change(
        fn=lambda x: print(f"Audio input changed in S2S: {x}"),
        inputs=[audio_input],
        outputs=None
    )

    update_button = gr.Button("Atualizar vozes")
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

    return audio_input, output_audio
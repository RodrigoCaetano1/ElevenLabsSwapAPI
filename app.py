import gradio as gr
from tabs.config.config import config_tab, add_api_entry
from tabs.audio_player.audio_player import audio_player_tab
from tabs.tts.tts import tts_tabs
from tabs.s2s.s2s import s2s_tab
import json

def load_voices():
    try:
        with open('all_voices.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading voices: {e}")
        return []

def handle_audio_transfer(audio):
    """Function to handle audio transfer between tabs"""
    print(f"Transferring audio from TTS to S2S: {audio}")
    if audio is None:
        raise gr.Error("Please generate audio first")
    return audio

# Interface Gradio
with gr.Blocks(theme=gr.themes.Default(primary_hue=gr.themes.colors.green, secondary_hue=gr.themes.colors.pink)) as interface:
    # Load voices once at startup
    voices = load_voices()
    
    with gr.Tabs():
        with gr.TabItem("TTS"):
            output_audio_tts, send_button = tts_tabs()

        with gr.TabItem("S2S"):
            audio_input_s2s, output_audio_s2s = s2s_tab()

        with gr.TabItem("Configurações"):
            config_tab()
       
        with gr.TabItem("Áudio Player"):
            audio_player_tab()
    
    # Connect the TTS send button to S2S audio input with proper handling and debug prints
    send_button.click(
        fn=handle_audio_transfer,
        inputs=[output_audio_tts],
        outputs=[audio_input_s2s],
        show_progress=True
    )
        
interface.launch()
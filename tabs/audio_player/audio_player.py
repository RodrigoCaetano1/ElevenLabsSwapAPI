import gradio as gr
import os
from scripts.ui import tocar_audio, listar_audios

def audio_player_tab():
    with gr.Row():
        # Lista de arquivos de áudio
        arquivos_audio = gr.Dropdown(
            label="Escolha um áudio",
            choices=listar_audios(),
            interactive=True
        )
        tocar_btn = gr.Button("Tocar Áudio")
        apagar_btn = gr.Button("Apagar Todos os Áudios")
        atualizar_btn = gr.Button("Atualizar Lista")

    # Área para tocar o áudio selecionado
    audio_player = gr.Audio(label="Player de Áudio")

    # Modificar a função apagar_audios para limpar corretamente
    def apagar_audios():
        for arquivo in os.listdir("results"):
            file_path = os.path.join("results", arquivo)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return gr.update(choices=[], value=None), None

    # Função atualizada para atualizar a lista
    def atualizar_lista():
        arquivos = listar_audios()
        return gr.update(choices=arquivos)

    # Ação ao clicar em "Tocar Áudio"
    tocar_btn.click(
        fn=tocar_audio,
        inputs=arquivos_audio,
        outputs=audio_player
    )

    # Ação ao clicar em "Apagar Todos os Áudios"
    apagar_btn.click(
        fn=apagar_audios,
        inputs=None,
        outputs=[arquivos_audio, audio_player]
    )

    # Ação ao clicar em "Atualizar Lista"
    atualizar_btn.click(
        fn=atualizar_lista,
        inputs=None,
        outputs=arquivos_audio
    )
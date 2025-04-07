import gradio as gr
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.api import all_api
from scripts.ui import remove_api_entry, update_api_list, load_apis, save_apis

def add_api_entry(name, api, api_selector, api_textbox):
    if not name or not api:  # Validação básica
        raise gr.Error("Nome e API são obrigatórios")
        
    apis = load_apis()
    # Verificar se o nome já existe
    if any(entry[0] == name for entry in apis):
        raise gr.Error("Nome da API já existe")
    
    global all_api    
    new_entry = (name, api, 'Data', 'MM/DD/AAAA HH:MM:SS')
    all_api.append(new_entry)
    apis.append(new_entry)
    save_apis(apis)

    # Verificar se api_selector não é None antes de tentar acessar suas propriedades
    if api_selector is not None:
        api_selector.choices = [api[0] for api in all_api]  # Atualizando o seletor com novas APIs
    else:
        print("api_selector não está definido corretamente!")
    
    # Atualizar o textbox com a nova lista de APIs
    api_list_str = str(all_api)
    print(f"API {name} adicionada com sucesso!")
    
    # Atualizar a interface
    api_entries = [f"{name}: {api}" for name, api, _, _ in apis]
    api_list_str = "\n".join(api_entries)
    
    # Limpar os campos de entrada e atualizar a interface
    return (
        gr.update(value=""),  # Limpa o campo nome
        gr.update(value=""),  # Limpa o campo API
        gr.update(value=api_list_str),  # Atualiza o textbox com a lista de APIs
        gr.update(choices=api_entries, value=None)  # Atualiza o dropdown
    )

def config_tab():
    gr.Markdown("## Configurações")
    
    # Exibir APIs atuais
    api_entries, api_list_str = update_api_list()
    
    api_textbox = gr.Textbox(
        label="APIs Atuais",
        value=api_list_str,
        lines=len(api_entries) + 1,
        interactive=False
    )

    with gr.Row():
        name_input = gr.Textbox(
            label="Nome da API",
            placeholder="Digite o nome da API"
        )
        api_input = gr.Textbox(
            label="Identificador da API",
            placeholder="Digite o identificador da API"
        )
        
    with gr.Row():
        api_selector = gr.Dropdown(
            label="Selecionar API para remover",
            choices=api_entries,
            value=None
        )

    with gr.Row():
        # Botão para adicionar nova API
        add_button = gr.Button("Adicionar Nova API", variant="primary")
        # Botão para remover API
        remove_button = gr.Button("Remover API", variant="stop")

    # Eventos dos botões
    add_button.click(
        add_api_entry,
        inputs=[name_input, api_input, api_selector, api_textbox],
        outputs=[name_input, api_input, api_textbox, api_selector]
    )

    remove_button.click(
        remove_api_entry,
        inputs=[api_selector],
        outputs=[api_textbox, api_selector]
    )
    
    return api_selector

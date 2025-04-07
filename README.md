# ElevenLabsSwapAPI

Uma aplicação em Python que utiliza a API da ElevenLabs para geração de texto-para-fala (TTS) e fala-para-fala (S2S) com suporte a rodízio de chaves de API. Construída com Gradio para uma interface web interativa, esta ferramenta permite aos usuários gerar áudios a partir de texto, gerenciar chaves de API e reproduzir arquivos de áudio gerados. O projeto é organizado com scripts modulares e abas para uma experiência de usuário limpa.

## Funcionalidades
- **Texto-para-Fala (TTS):** Converte texto em áudio usando diversos modelos e configurações de voz da ElevenLabs.
- **Fala-para-Fala (S2S):** Transforma áudio de entrada em uma voz diferente usando as capacidades S2S da ElevenLabs.
- **Rodízio de API:** Faz rodízio automaticamente entre várias chaves de API da ElevenLabs para gerenciar limites de uso e evitar esgotamento.
- **Gerenciamento de Vozes:** Carrega e exibe vozes disponíveis do arquivo `all_voices.json` com metadados adicionais como rótulos e URLs de pré-visualização.
- **Reprodutor de Áudio:** Reproduz, lista e exclui arquivos de áudio gerados armazenados no diretório `results`.
- **Configurações Ajustáveis:** Ajusta estabilidade, estilo e aumento de similaridade para geração de áudio.
- **Interface Gradio:** Uma interface web amigável com abas para TTS, S2S, configuração e reprodução de áudio.

## Estrutura do Projeto
```
ElevenLabsSwapAPI/
├── app.py               # Script principal com a interface Gradio
├── scripts/
│   ├── api.py          # Armazenamento e gerenciamento de chaves de API
│   ├── generate.py     # Lógica de geração de áudio com rotação de API
│   ├── get_voices.py   # Script para buscar e salvar vozes em all_voices.json
│   ├── outros.py       # Utilitários diversos (se aplicável)
│   └── ...             # Outros scripts conforme necessário
├── tabs/
│   ├── audio_player/   # Lógica da aba de reprodutor de áudio
│   │   └── audio_player.py
│   ├── config/         # Lógica da aba de configuração
│   │   └── config.py
│   ├── s2s/            # Lógica da aba de fala-para-fala
│   │   └── s2s.py
│   └── tts/            # Lógica da aba de texto-para-fala
│       └── tts.py
├── results/            # Diretório para armazenar arquivos de áudio gerados
├── all_voices.json     # Arquivo JSON contendo dados de vozes
├── all_models.json     # Arquivo JSON contendo dados de modelos (opcional)
├── api_status.json     # Arquivo JSON rastreando o status de uso das APIs
└── README.md           # Este arquivo
```

## Pré-requisitos
- Python 3.8+
- Chave(s) de API da ElevenLabs (Inscreva-se em [ElevenLabs](https://elevenlabs.io) para obter uma)
- Pode ter quantas chaves quiser, cada conta que você cria, libera 10 mil, e todo mês ela reseta, então guarde a conta, se tiver 10 contas, terá 100 mil, se usar turbo v2.5, tera 200mil tokens.
- Recomendo usar de 2 em 2 api pelo google colab, pois troca o IP de dificilmente irá dar ban.

## Instalação

1. **Clonar o Repositório**
   ```bash
   git clone https://github.com/RafaelGodoyEbert/ElevenLabsSwapAPI.git
   cd ElevenLabsSwapAPI
   ```

2. **Instalar Dependências**
   Instale os pacotes Python necessários usando pip:
   ```bash
   pip install gradio requests aiohttp elevenlabs
   ```

3. **Configurar Chaves de API**
   - Abra `scripts/api.py` e adicione suas chaves de API da ElevenLabs na lista `all_api`:
     ```python
     all_api = [
         ("usuário1", "sua_chave_api_1", "Data", "DD/MM/AAAA HH:MM:SS"),
         ("usuário2", "sua_chave_api_2", "Data", "DD/MM/AAAA HH:MM:SS"),
     ]
     ```
   - Alternativamente, use a interface Gradio para adicionar chaves dinamicamente.

4. **Obter Vozes**
   Execute o script para preencher `all_voices.json` com as vozes disponíveis:
   ```bash
   python scripts/get_voices.py
   ```

## Uso

1. **Executar a Aplicação**
   Inicie a interface Gradio:
   ```bash
   python app.py
   ```
   Isso iniciará um servidor web, geralmente em `http://127.0.0.1:7860`.

2. **Navegar na Interface**
   - **Aba TTS:** Insira texto, selecione uma voz e modelo, ajuste configurações e gere áudio. Use o botão "Enviar para S2S" para transferir o áudio para a aba S2S.
   - **Aba S2S:** Faça upload de um arquivo de áudio ou use o áudio transferido, selecione uma voz e gere um novo arquivo de áudio.
   - **Aba Configurações:** Adicione, remova ou visualize chaves de API e seu status.
   - **Aba Áudio Player:** Reproduza, liste ou exclua arquivos de áudio do diretório `results`.

3. **Rotação de API**
   - A aplicação verifica automaticamente os limites de uso da API e rotaciona para uma chave disponível se uma estiver esgotada.
   - O status da API é salvo em `api_status.json` e atualizado após cada geração.

## Exemplo
Para gerar áudio a partir de texto:
1. Vá para a aba TTS.
2. Insira um texto (ex.: "Olá, este é um teste!").
3. Selecione uma voz no menu suspenso (ex.: "Rachel").
4. Escolha um modelo (ex.: "Eleven Turbo v2.5").
5. Ajuste os controles deslizantes para estabilidade, estilo e aumento de similaridade.
6. Clique em "Gerar" para criar e baixar o áudio.

## Notas
- **Dados de Voz:** Certifique-se de que `all_voices.json` esteja preenchido executando `scripts/get_voices.py` com uma chave de API válida.
- **Armazenamento de Áudio:** Os arquivos de áudio gerados são salvos no diretório `results`.
- **Tratamento de Erros:** A aplicação exibe erros Gradio para problemas como limites de API esgotados ou vozes ausentes.

## Contribuição
Sinta-se à vontade para enviar issues ou pull requests para melhorar o projeto. Contribuições são bem-vindas!

## Agradecimentos
- Construído com [Gradio](https://gradio.app) para a interface de usuário.
- Alimentado por [ElevenLabs](https://elevenlabs.io) para capacidades de TTS e S2S. 

"Esta ferramenta foi desenvolvida para fins legítimos e educacionais. O autor não se responsabiliza por qualquer uso indevido, ilegal ou antiético da aplicação, incluindo violações de direitos autorais, privacidade ou termos de serviço da ElevenLabs. O uso responsável é de exclusiva responsabilidade do usuário."

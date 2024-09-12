# OBLIVION-LOADER - Bot de Confirmação de Pagamento

Este repositório contém o código para o OBLIVION-LOADER, um bot do Discord projetado para gerenciar pedidos e confirmar pagamentos automaticamente. Ele oferece recursos como exibição de carrinho, geração de QR Codes para pagamentos via PIX e envio de notificações para um canal designado.

## 🔑 Funcionalidades
- 🛒 **Gerenciamento de Carrinho**: Apresenta os itens e detalhes do pedido de forma clara.
- 💳 **Confirmação de Pagamento**: Atualiza o status do pedido e confirma a entrega.
- 🔄 **Geração de QR Code para PIX**: Gera automaticamente um QR Code de pagamento para facilitar o processo.
- 📤 **Envio de Mensagens ao Canal Específico**: Envia atualizações para um canal de logs definido.

## 🛠️ Pré-requisitos
Antes de rodar o bot, certifique-se de ter os seguintes itens instalados:
- **Python 3.x**
- As bibliotecas listadas no arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### Dependências principais:
- `discord.py`: Para interação com a API do Discord.
- `qrcode[pil]`: Para gerar o QR Code de pagamento.

## 📂 Estrutura do Projeto
```bash
.
├── bot.py               # Arquivo principal com a lógica do bot
├── requirements.txt     # Dependências do projeto
├── config.json          # Configurações do bot (token, IDs de canais)
└── README.md            # Descrição do projeto (você está aqui)

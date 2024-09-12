import discord
import os
import random
from discord.ext import commands
from discord.ui import Button, View, Select
from dotenv import load_dotenv
import logging
import asyncio
from datetime import datetime

# Configurar o logging
logging.basicConfig(level=logging.INFO)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar o bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Definindo os produtos e o carrinho
products = [
    {
        'label': 'KEY',
        'description': '```**🔑KEY DEADLOCK🔑**\n- 📞ENTREGA POR CALL \n- 🛒 COMPRA AUTOMATICA\n- 💠 APENAS PAGAMENTO PIX 💠\n- DEMORA DE 2HRS A 48HRS PARA CAIR NA CONTA \n- 🚀 ENVIO RAPIDO 🚀\n- (VERSÃO PC 🖥️)```',
        'stock': 49,
        'image': 'https://media.discordapp.net/attachments/1276550595582623822/1283494536177385472/deadlock-08-23-24-1-1.png?ex=66e332ef&is=66e1e16f&hm=e162c5ed47ae9100de23e12a342f03041cf0965a077e144c1b2f66155823ee8a&=&format=webp&quality=lossless&width=994&height=559',
        'footer': 'OBLIVION-LOADER Todos os direitos reservados',
        'subproducts': [
            
            {'label': '1 keys deadlock', 'price': 8},
        ]
    }
]

carts = {}
orders = {}

def generate_order_number():
    return str(random.randint(100000, 999999))

class SubproductSelect(Select):
    def __init__(self, product):
        options = [discord.SelectOption(label=sub['label'], value=sub['label']) for sub in product['subproducts']]
        super().__init__(placeholder='SELECIONE AQUI! ', options=options)
        self.product = product
    
    async def callback(self, interaction: discord.Interaction):
        selected_label = self.values[0]
        user_id = interaction.user.id

        if user_id not in carts:
            carts[user_id] = []

        # Adiciona o produto ao carrinho
        subproduct = next((sub for sub in self.product['subproducts'] if sub['label'] == selected_label), None)
        if not subproduct:
            await interaction.response.send_message("❌ Subproduto não encontrado!", ephemeral=True)
            return

        carts[user_id].append({'product': self.product, 'selected_subproduct': subproduct})

        total_price = subproduct['price']
        order_number = generate_order_number()
        orders[order_number] = {
            'user_id': user_id,
            'products': carts[user_id],
            'total_price': total_price,
            'timestamp': datetime.now()
        }

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🛒 Carrinho Atualizado",
                description=f"Você selecionou o subproduto: **{selected_label}**\nValor: R${total_price},00\n\nO carrinho foi criado e você pode finalizar a compra lá.",
                color=0x2ecc71
            ).add_field(name="Número do Pedido", value=order_number)
        )
        
        finalizar_button = Button(label="💳 Finalizar Compra", style=discord.ButtonStyle.primary, custom_id="finalizar_compra")
        finalizar_view = View()
        finalizar_view.add_item(finalizar_button)
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Não foi possível encontrar o servidor.", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="🛒Carrinho")
        if not category:
            category = await guild.create_category(name="🛒Carrinho")

        channel_name = f"carrinho-{interaction.user.display_name} 🛒"
        channel = await guild.create_text_channel(name=channel_name, category=category)

        # Definir permissões do canal
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        cart_embed = discord.Embed(title="🛒 Carrinho Atualizado", description="Confira os itens do seu carrinho:", color=0x2ecc71)
        total_price = sum(p['selected_subproduct']['price'] for p in carts[user_id])
        cart_embed.add_field(name="💰 Total", value=f"R${total_price},00", inline=False)

        for p in carts[user_id]:
            product = p['product']
            subproduct = p['selected_subproduct']
            cart_embed.add_field(name=f"📦 {product['label']} - {subproduct['label']}", value=f"R${subproduct['price']},00", inline=True)
            cart_embed.set_image(url=product['image'])

        cart_embed.add_field(name="Número do Pedido", value=order_number, inline=False)

        await channel.send(embed=cart_embed)
        await channel.send(
            "💠",  # Mensagem de carregamento fora do embed
            view=finalizar_view
        )

@bot.event
async def on_ready():
    logging.info(f'Bot iniciado como {bot.user}')

@bot.command()
async def enviar(ctx, *, product_name: str):
    logging.info(f'Comando !enviar recebido com: {product_name}')
    product_name = product_name.strip().lower()
    product = next((p for p in products if p['label'].lower() == product_name), None)

    if not product:
        await ctx.send(embed=discord.Embed(title="❌ Produto Não Encontrado", description=f'O produto **{product_name}** não foi encontrado.', color=0xff0000))
        return

    logging.info(f'Produto encontrado: {product}')
    embed = discord.Embed(title=f"🛒 {product['label']}", description=product['description'], color=0x2ecc71)
    embed.add_field(name="📦 Estoque", value=f"{product['stock']}", inline=True)
    embed.set_image(url=product['image'])
    embed.set_footer(text=product['footer'], icon_url="https://exemplo.com/icon.png")

    subproduct_select = SubproductSelect(product)
    select_view = View()
    select_view.add_item(subproduct_select)

    await ctx.send(embed=embed, view=select_view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data['custom_id']

        if custom_id == "finalizar_compra":
            user_id = interaction.user.id
            if user_id not in carts or not carts[user_id]:
                await interaction.response.send_message(embed=discord.Embed(title="❌ Carrinho Vazio", description="Seu carrinho está vazio!", color=0xff0000), ephemeral=True)
                return

            order_number = generate_order_number()
            total_price = sum(p['selected_subproduct']['price'] for p in carts[user_id])
            orders[order_number] = {
                'user_id': user_id,
                'products': carts[user_id],
                'total_price': total_price,
                'timestamp': datetime.now()
            }

            pix_code_path = "qrpix.png"

            if not os.path.exists(pix_code_path):
                await interaction.response.send_message(embed=discord.Embed(title="❌ Erro", description="QR Code PIX não encontrado!", color=0xff0000), ephemeral=True)
                return

            await interaction.response.send_message(" 💠↓", ephemeral=True)
            await interaction.followup.send(file=discord.File(pix_code_path, "pix_qr.png"))

            # Excluir o canal após 10 minutos
            channel = discord.utils.get(interaction.guild.text_channels, name=f"carrinho-{interaction.user.display_name} 🛒")
            if channel:
                await asyncio.sleep(600)
                await channel.delete()

            # Limpar o carrinho do usuário
            carts[user_id] = []

@bot.command()
async def pay(ctx, *, order_number: str):
    logging.info(f'Comando !pay recebido com: {order_number}')
    if not order_number:
        await ctx.send(embed=discord.Embed(title="❌ Erro", description="Número do pedido não fornecido!", color=0xff0000))
        return

    if order_number not in orders:
        await ctx.send(embed=discord.Embed(title="❌ Erro", description=f"Pedido **{order_number}** não encontrado!", color=0xff0000))
        return

    order = orders.pop(order_number)

    # Criar o embed de confirmação de pagamento
    embed = discord.Embed(title="🛒 Confirmação de Pagamento", color=0x2ecc71)
    embed.add_field(name="Número do Pedido", value=order_number, inline=False)
    embed.add_field(name="Produto", value="Key-deadlock", inline=False)
    embed.add_field(name="Total", value=f"R${order['total_price']},00", inline=False)
    embed.add_field(name="Data", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Status do Pedido", value="✅PAGAMENTO CONFIRMADO E 📦PRODUTO ENTREGUE OBRIGADO PELA COMPRA", inline=False)

    for p in order['products']:
        product = p['product']
        subproduct = p['selected_subproduct']
        embed.add_field(name=f"📦 {product['label']} - {subproduct['label']}", value=f"R${subproduct['price']},00", inline=True)
        embed.set_image(url=product['image'])

    embed.set_footer(text="OBLIVION-LOADER Todos os direitos reservados para este canal id 1283492923052392458")

    # Enviar a mensagem de confirmação para o canal especificado
    channel = bot.get_channel(1283492923052392458)  # Substitua pelo ID do canal desejado
    if channel:
        await channel.send(embed=embed)
        await channel.send("")  # Mensagem de carregamento fora do embed
    else:
        await ctx.send(embed=discord.Embed(title="❌ Erro", description="Canal de confirmação não encontrado!", color=0xff0000))

# Iniciar o bot
bot.run(os.getenv('DISCORD_TOKEN'))

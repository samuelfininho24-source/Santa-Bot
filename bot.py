import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from pathlib import Path

# ============================================================
# SANTA RP — BOT DE WHITELIST, META RP E APROVAÇÃO DE PERSONAGEM
# Requer Python 3.10+ e discord.py 2.x
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

# IDs DO SEU SERVIDOR — TROQUE PELOS IDs REAIS
GUILD_ID = 0
CATEGORIA_WHITELIST_ID = 0

# Cargo que todo jogador sem whitelist possui
CARGO_SEM_REGISTRO_ID = 0

# Os 2 cargos recebidos quando a whitelist for aprovada
CARGO_WHITELIST_1_ID = 0
CARGO_WHITELIST_2_ID = 0

# Cargo usado no /aprovarpersonagem
CARGO_PERSONAGEM_APROVADA_ID = 0

# Link do servidor Roblox informado por você.
# Coloque o link do seu servidor aqui.
ROBLOX_SERVER_LINK = "COLE_AQUI_O_LINK_DO_SERVIDOR_ROBLOX"

# Arquivo simples para guardar o número da whitelist e votos
DATA_FILE = Path("santa_data.json")

# Sistema de ID — primeiro novo ID: 84
ID_FILE = Path("santa_ids.json")
ID_INICIAL = 84

def carregar_ids():
    if not ID_FILE.exists():
        return {"proximo_id": ID_INICIAL, "usuarios": {}}
    try:
        with open(ID_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"proximo_id": ID_INICIAL, "usuarios": {}}

def salvar_ids(ids):
    with open(ID_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

ids = carregar_ids()

BLACK = 0x000000

QUESTOES = [
    {
        "pergunta": "O que é RDM?",
        "opcoes": {
            "A": "Matar outro jogador sem uma situação de RP que justifique",
            "B": "Roubar um veículo durante uma perseguição",
            "C": "Sair do servidor depois de uma cena",
            "D": "Conversar fora do personagem"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é VDM?",
        "opcoes": {
            "A": "Usar um veículo para atropelar/matar alguém sem contexto de RP",
            "B": "Usar voz no jogo",
            "C": "Entrar em uma empresa",
            "D": "Fazer uma abordagem policial"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Metagaming?",
        "opcoes": {
            "A": "Usar uma informação obtida fora do RP dentro do RP",
            "B": "Criar um personagem novo",
            "C": "Comprar uma casa",
            "D": "Trabalhar como médico"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Powergaming?",
        "opcoes": {
            "A": "Forçar ações ou situações impossíveis/sem dar chance de reação ao outro jogador",
            "B": "Trabalhar em uma empresa",
            "C": "Fazer uma corrida",
            "D": "Usar um veículo oficial"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que significa RP?",
        "opcoes": {
            "A": "Roleplay: interpretar um personagem dentro da situação proposta",
            "B": "Regras Públicas",
            "C": "Ranking de Polícia",
            "D": "Registro de Pessoa"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Anti-RP?",
        "opcoes": {
            "A": "Uma atitude que quebra a interpretação e as regras da situação de RP",
            "B": "Uma profissão dentro da cidade",
            "C": "Um tipo de veículo",
            "D": "Uma forma de ganhar dinheiro"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Combat Logging?",
        "opcoes": {
            "A": "Sair do jogo para evitar uma situação de RP",
            "B": "Trocar de roupa",
            "C": "Entrar em uma casa",
            "D": "Mudar de profissão"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Fear RP?",
        "opcoes": {
            "A": "Valorizar a vida do personagem diante de uma situação de perigo",
            "B": "Ter medo de entrar no servidor",
            "C": "Usar uma roupa escura",
            "D": "Fugir de uma profissão"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é OOC?",
        "opcoes": {
            "A": "Algo dito ou feito fora da interpretação do personagem",
            "B": "Uma corporação policial",
            "C": "Uma empresa",
            "D": "Um veículo"
        },
        "resposta": "A"
    },
    {
        "pergunta": "Durante uma situação de RP, qual é a melhor atitude?",
        "opcoes": {
            "A": "Respeitar as regras, interpretar a situação e dar continuidade ao RP",
            "B": "Abandonar a situação sempre que perder",
            "C": "Usar informações externas para ganhar vantagem",
            "D": "Ignorar os outros jogadores"
        },
        "resposta": "A"
    }
]


def carregar_dados():
    if not DATA_FILE.exists():
        return {"proximo_numero": 1, "votos_sim": [], "votos_nao": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"proximo_numero": 1, "votos_sim": [], "votos_nao": []}


def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


dados = carregar_dados()


def embed_preto(titulo, descricao):
    return discord.Embed(
        title=titulo,
        description=descricao,
        color=BLACK
    )


intents = discord.Intents.default()
intents.guilds = True
intents.members = True


def cargo(guild, role_id):
    return guild.get_role(role_id)


class MetaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Sim",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="santa_meta_sim"
    )
    async def sim(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        if user_id in dados["votos_sim"] or user_id in dados["votos_nao"]:
            await interaction.response.send_message(
                "❌ Você já votou nessa meta.",
                ephemeral=True
            )
            return

        dados["votos_sim"].append(user_id)
        salvar_dados(dados)
        await atualizar_meta(interaction.message)
        await interaction.response.send_message(
            "✅ Seu voto foi registrado como **Sim**.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Não",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="santa_meta_nao"
    )
    async def nao(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        if user_id in dados["votos_sim"] or user_id in dados["votos_nao"]:
            await interaction.response.send_message(
                "❌ Você já votou nessa meta.",
                ephemeral=True
            )
            return

        dados["votos_nao"].append(user_id)
        salvar_dados(dados)
        await atualizar_meta(interaction.message)
        await interaction.response.send_message(
            "❌ Seu voto foi registrado como **Não**.",
            ephemeral=True
        )


async def atualizar_meta(message):
    sim = len(dados["votos_sim"])
    nao = len(dados["votos_nao"])

    embed = embed_preto(
        "🌆 META RP — CIDADE ON 🌆",
        f"""👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**

━━━━━━━━━━━━━━━━━━━━

📢 **A cidade deve abrir o RP?**

🗳️ **Votos:** {sim + nao} VOTOS

━━━━━━━━━━━━━━━━━━━━"""
    )

    embed.set_footer(text=f"✅ {sim} votos a favor • ❌ {nao} votos contra")
    await message.edit(embed=embed, view=MetaView())


class AbrirWhitelistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Whitelist",
        emoji="📋",
        style=discord.ButtonStyle.primary,
        custom_id="santa_abrir_whitelist"
    )
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        membro = interaction.user

        categoria = guild.get_channel(CATEGORIA_WHITELIST_ID)
        if categoria is None or not isinstance(categoria, discord.CategoryChannel):
            await interaction.response.send_message(
                "❌ A categoria da whitelist não foi configurada corretamente.",
                ephemeral=True
            )
            return

        # Evita duas whitelists simultâneas da mesma pessoa.
        for canal in categoria.channels:
            if canal.topic == f"whitelist:{membro.id}":
                await interaction.response.send_message(
                    f"❌ Você já possui uma whitelist aberta: {canal.mention}",
                    ephemeral=True
                )
                return

        numero = dados["proximo_numero"]
        dados["proximo_numero"] += 1
        salvar_dados(dados)

        nome = f"whitelist-{numero:03d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            membro: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                read_message_history=True
            )
        }

        # Permite a equipe com Manage Channels ver os canais.
        for role in guild.roles:
            if role.permissions.manage_channels:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        canal = await guild.create_text_channel(
            nome,
            category=categoria,
            overwrites=overwrites,
            topic=f"whitelist:{membro.id}"
        )

        await interaction.response.send_message(
            f"✅ Sua whitelist **#{numero:03d}** foi criada: {canal.mention}",
            ephemeral=True
        )

        embed = embed_preto(
            f"📋 WHITELIST #{numero:03d}",
            f"""Olá, {membro.mention}!

Responda às **10 perguntas** abaixo usando os botões **A, B, C ou D**.

🎯 **Aprovação:** 8/10 ou mais
❌ Menos de 8 acertos = reprovado

Boa sorte!"""
        )
        await canal.send(embed=embed)
        await enviar_pergunta(canal, membro, 0, 0)


async def enviar_pergunta(canal, membro, indice, acertos):
    if indice >= len(QUESTOES):
        if acertos >= 8:
            resultado = "🎉 **WHITELIST APROVADA!**"
            descricao = f"Você acertou **{acertos}/10** perguntas."

            sem_registro = cargo(canal.guild, CARGO_SEM_REGISTRO_ID)
            cargo1 = cargo(canal.guild, CARGO_WHITELIST_1_ID)
            cargo2 = cargo(canal.guild, CARGO_WHITELIST_2_ID)

            erros = []
            if sem_registro:
                try:
                    await membro.remove_roles(sem_registro, reason="Whitelist aprovada")
                except discord.Forbidden:
                    erros.append("Não consegui remover o cargo Sem Registro.")

            for r in (cargo1, cargo2):
                if r:
                    try:
                        await membro.add_roles(r, reason="Whitelist aprovada")
                    except discord.Forbidden:
                        erros.append(f"Não consegui adicionar o cargo {r.name}.")
                else:
                    erros.append("Um dos cargos de aprovação não foi configurado.")

            if erros:
                descricao += "\n\n⚠️ " + "\n".join(erros)

            await canal.send(embed=embed_preto(resultado, descricao))
        else:
            await canal.send(
                embed=embed_preto(
                    "❌ WHITELIST REPROVADA",
                    f"Você acertou **{acertos}/10**.\n\nÉ necessário acertar **8/10** para ser aprovado."
                )
            )

        await canal.send(
            embed=embed_preto(
                "🔒 FINALIZADO",
                "Esta whitelist foi finalizada. A equipe pode apagar este canal quando quiser."
            )
        )
        return

    q = QUESTOES[indice]

    class QuestaoView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        async def responder(self, interaction, escolha):
            if interaction.user.id != membro.id:
                await interaction.response.send_message(
                    "❌ Esta whitelist pertence a outro jogador.",
                    ephemeral=True
                )
                return

            novo_acerto = acertos + (1 if escolha == q["resposta"] else 0)

            if escolha == q["resposta"]:
                texto = "✅ Resposta correta!"
            else:
                texto = f"❌ Resposta incorreta. A resposta certa era **{q['resposta']}**."

            await interaction.response.edit_message(
                embed=embed_preto(
                    f"📝 PERGUNTA {indice + 1}/10",
                    f"{texto}\n\nCarregando a próxima pergunta..."
                ),
                view=None
            )

            await enviar_pergunta(canal, membro, indice + 1, novo_acerto)

        @discord.ui.button(label="A", style=discord.ButtonStyle.secondary)
        async def a(self, interaction, button):
            await self.responder(interaction, "A")

        @discord.ui.button(label="B", style=discord.ButtonStyle.secondary)
        async def b(self, interaction, button):
            await self.responder(interaction, "B")

        @discord.ui.button(label="C", style=discord.ButtonStyle.secondary)
        async def c(self, interaction, button):
            await self.responder(interaction, "C")

        @discord.ui.button(label="D", style=discord.ButtonStyle.secondary)
        async def d(self, interaction, button):
            await self.responder(interaction, "D")

    opcoes = "\n".join(
        f"**{letra})** {texto}" for letra, texto in q["opcoes"].items()
    )

    embed = embed_preto(
        f"📝 PERGUNTA {indice + 1}/10",
        f"**{q['pergunta']}**\n\n{opcoes}"
    )
    embed.set_footer(text=f"Acertos atuais: {acertos}")

    await canal.send(embed=embed, view=QuestaoView())


class SantaBot(commands.Bot):
    async def setup_hook(self):
        self.add_view(MetaView())
        self.add_view(AbrirWhitelistView())

        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()


bot = SantaBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Santa Bot conectado como {bot.user}.")


@bot.tree.command(name="metarp", description="Envia a votação para abrir o RP.")
@app_commands.checks.has_permissions(administrator=True)
async def metarp(interaction: discord.Interaction):
    dados["votos_sim"] = []
    dados["votos_nao"] = []
    salvar_dados(dados)

    embed = embed_preto(
        "🌆 META RP — CIDADE ON 🌆",
        """👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**
🗳️ Votos: **0 VOTOS**

━━━━━━━━━━━━━━━━━━━━

📢 **A cidade deve abrir o RP?**

━━━━━━━━━━━━━━━━━━━━"""
    )
    embed.set_footer(text="✅ 0 votos a favor • ❌ 0 votos contra")

    await interaction.response.send_message(embed=embed, view=MetaView())


@bot.tree.command(name="rpsanta", description="Envia o aviso de RP online.")
@app_commands.checks.has_permissions(administrator=True)
async def rpsanta(interaction: discord.Interaction):
    embed = embed_preto(
        "🟢 RP ON — CIDADE ONLINE",
        """👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**
🚕 Táxis: **ATIVOS**
⛽ Postos: **ABERTOS**

━━━━━━━━━━━━━━━━━━━━

📢 **ATENÇÃO, CIDADÃOS!**

O RP está oficialmente ON! Entrem em personagem, respeitem a imersão e aproveitem a cidade.

🔥 **BOM RP A TODOS!**"""
    )

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="ENTRAR NO RP",
            emoji="🎮",
            style=discord.ButtonStyle.success,
            url=ROBLOX_SERVER_LINK
        )
    )

    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="id", description="Receba seu ID do servidor.")
async def id_command(interaction: discord.Interaction):
    usuario = str(interaction.user.id)
    if usuario in ids["usuarios"]:
        meu_id = ids["usuarios"][usuario]
        await interaction.response.send_message(embed=embed_preto("🆔 SANTA RP — SEU ID", f"👤 **Membro:** {interaction.user.mention}\n\n🆔 **Seu ID:** `{meu_id}`"), ephemeral=True)
        return
    novo_id = ids["proximo_id"]
    if novo_id > 1000:
        await interaction.response.send_message(embed=embed_preto("❌ IDs ESGOTADOS", "O limite de IDs é **1000**."), ephemeral=True)
        return
    meu_id = f"{novo_id:02d}" if novo_id < 100 else str(novo_id)
    ids["usuarios"][usuario] = meu_id
    ids["proximo_id"] = novo_id + 1
    salvar_ids(ids)
    try:
        nome = interaction.user.display_name
        if "|" in nome:
            nome = nome.split("|", 1)[1].strip()
        await interaction.user.edit(nick=f"{meu_id} | {nome}"[:32])
    except (discord.Forbidden, discord.HTTPException):
        pass
    await interaction.response.send_message(embed=embed_preto("🆔 SANTA RP — ID REGISTRADO", f"👤 **Membro:** {interaction.user.mention}\n\n🆔 **ID atribuído:** `{meu_id}`\n\n✅ Seu ID foi registrado e ficará salvo."))


@bot.tree.command(name="whitelist", description="Envia o painel para abrir a whitelist.")
@app_commands.checks.has_permissions(administrator=True)
async def whitelist(interaction: discord.Interaction):
    embed = embed_preto(
        "📋 SANTA RP — WHITELIST",
        """Clique no botão abaixo para iniciar sua whitelist.

📌 O bot criará um canal privado com seu número de whitelist.
📝 Serão 10 perguntas de GTA RP.
🎯 É necessário acertar **8/10** para passar.

Boa sorte!"""
    )

    await interaction.response.send_message(
        embed=embed,
        view=AbrirWhitelistView()
    )


@bot.tree.command(
    name="aprovarpersonagem",
    description="Aprova o personagem de um jogador."
)
@app_commands.describe(jogador="Jogador que terá o personagem aprovado.")
@app_commands.checks.has_permissions(administrator=True)
async def aprovarpersonagem(
    interaction: discord.Interaction,
    jogador: discord.Member
):
    role = cargo(interaction.guild, CARGO_PERSONAGEM_APROVADA_ID)

    if role is None:
        await interaction.response.send_message(
            "❌ Configure CARGO_PERSONAGEM_APROVADA_ID no código.",
            ephemeral=True
        )
        return

    try:
        await jogador.add_roles(
            role,
            reason=f"Personagem aprovado por {interaction.user}"
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Não consegui adicionar o cargo. Verifique a hierarquia dos cargos.",
            ephemeral=True
        )
        return

    embed = embed_preto(
        "✅ PERSONAGEM APROVADO",
        f"👤 Jogador: {jogador.mention}\n\n"
        f"🎭 O personagem foi aprovado por {interaction.user.mention}."
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.error
async def erro_comando(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        mensagem = "❌ Você precisa ser administrador para usar este comando."
    else:
        print(f"Erro: {repr(error)}")
        mensagem = "❌ Ocorreu um erro ao executar o comando."

    if interaction.response.is_done():
        await interaction.followup.send(mensagem, ephemeral=True)
    else:
        await interaction.response.send_message(mensagem, ephemeral=True)


bot.run(TOKEN)

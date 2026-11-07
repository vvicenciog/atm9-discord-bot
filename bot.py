"""
Discord Bot para gestionar instancias EC2 (Start/Stop).
Comandos por chat con prefijo "!"
"""

from __future__ import annotations

import os
import asyncio
import discord
from discord.ext import commands
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# ─── Cargar variables de entorno ─────────────────────────────────────────────
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
EC2_INSTANCE_ID = os.getenv("EC2_INSTANCE_ID")
ALLOWED_ROLE_ID = os.getenv("ALLOWED_ROLE_ID")  # Opcional
ATM9_IMAGE_URL = "https://i.imgur.com/cn0OGDE.png"
JB_THE_VOICE_IMAGE_URL = "https://github.com/vvicenciog/images/blob/main/JB_THE_VOICE.jpeg?raw=true"

# ─── Validación ──────────────────────────────────────────────────────────────
if not DISCORD_TOKEN:
    raise RuntimeError("Falta DISCORD_TOKEN en las variables de entorno.")
if not EC2_INSTANCE_ID:
    raise RuntimeError("Falta EC2_INSTANCE_ID en las variables de entorno.")

# ─── Cliente AWS EC2 ─────────────────────────────────────────────────────────
ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# ─── Bot de Discord ──────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def embed(
    title: str,
    desc: str,
    color: discord.Color,
    image_url: str | None = None,
    thumbnail_url: str | None = None,
) -> discord.Embed:
    e = discord.Embed(title=title, description=desc, color=color)
    e.set_footer(text="ATM9 MODPACK 🍆")
    if image_url:
        e.set_image(url=image_url)
    if thumbnail_url:
        e.set_thumbnail(url=thumbnail_url)
    return e


def _get_instance_info_sync() -> dict:
    """(Síncrono) Devuelve estado, IP, tipo de la instancia."""
    resp = ec2.describe_instances(InstanceIds=[EC2_INSTANCE_ID])
    inst = resp["Reservations"][0]["Instances"][0]
    return {
        "state": inst["State"]["Name"],
        "ip": inst.get("PublicIpAddress", "Sin IP pública"),
        "type": inst.get("InstanceType", "N/A"),
    }


async def get_instance_info() -> dict:
    """(Async) Ejecuta la llamada AWS en un hilo para no bloquear el event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _get_instance_info_sync)


def has_permission(ctx: commands.Context) -> bool:
    """Verifica si el usuario tiene el rol permitido. Retorna False en DMs si se requiere rol."""
    if not ALLOWED_ROLE_ID:
        return True
    # En DMs no hay roles → no tiene permiso si se requiere un rol
    if not ctx.guild or not hasattr(ctx.author, "roles"):
        return False
    return any(r.id == int(ALLOWED_ROLE_ID) for r in ctx.author.roles)


async def wait_for_state(target: str, timeout: int = 120) -> dict | None:
    """Espera hasta que la instancia llegue al estado deseado. Retorna info o None si timeout."""
    for _ in range(timeout // 5):
        await asyncio.sleep(5)
        try:
            info = await get_instance_info()
            if info["state"] == target:
                return info
        except ClientError:
            pass
    return None


# ─── Eventos ─────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"[OK] Bot conectado como {bot.user} (ID: {bot.user.id})")
    print(f"[EC2] ATM9 MODPACK | Instancia: {EC2_INSTANCE_ID} | Region: {AWS_REGION}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="ATM9 MODPACK 🍆 | !ayuda")
    )


# ─── Comandos ────────────────────────────────────────────────────────────────

@bot.command(name="prender", aliases=["start", "encender", "on"])
async def cmd_prender(ctx: commands.Context):
    """🟢 Enciende el servidor ATM9 MODPACK"""
    if not has_permission(ctx):
        await ctx.reply("❌ No tienes permiso para usar este comando.")
        return

    try:
        info = await get_instance_info()

        if info["state"] == "running":
            await ctx.reply(embed=embed(
                "✅ Ya está encendido 🍆",
                f"El servidor **ATM9 MODPACK** ya está **running** 🍆\n**IP:** `{info['ip']}`",
                discord.Color.green(),
                image_url=ATM9_IMAGE_URL,
            ))
            return

        if info["state"] != "stopped":
            await ctx.reply(embed=embed(
                "⏳ Estado actual 🍆",
                f"El servidor **ATM9 MODPACK** está en estado `{info['state']}`, espera a que termine antes de encender 🍆.",
                discord.Color.yellow(),
            ))
            return

        # Enviar el comando de encendido (en hilo para no bloquear)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, lambda: ec2.start_instances(InstanceIds=[EC2_INSTANCE_ID])
        )

        msg = await ctx.reply(embed=embed(
            "⏳ Encendiendo ATM9 MODPACK... 🍆",
            f"Encendiendo servidor **ATM9 MODPACK** (`{EC2_INSTANCE_ID}`)...\nEspera, te aviso cuando esté listo 🍆.",
            discord.Color.yellow(),
            image_url=ATM9_IMAGE_URL,
        ))

        # Esperar a que arranque
        result = await wait_for_state("running", timeout=120)

        if result:
            await msg.edit(embed=embed(
                "🟢 ¡ATM9 MODPACK Encendido! 🍆",
                (
                    f"**¡El servidor ATM9 MODPACK ya está listo!** 🍆✅\n\n"
                    f"🍆 **Servidor:** ATM9 MODPACK\n"
                    f"**ID:** `{EC2_INSTANCE_ID}`\n"
                    f"**IP:** `{result['ip']}`\n"
                    f"**Tipo:** `{result['type']}`\n"
                    f"**Estado:** `running` 🍆"
                ),
                discord.Color.green(),
                image_url=ATM9_IMAGE_URL,
            ))
            # Aviso adicional mencionando al usuario
            await ctx.send(f"🔔 {ctx.author.mention} ¡El servidor **ATM9 MODPACK** está **ENCENDIDO** y listo para viciar! 🍆 IP: `{result['ip']}`")
        else:
            await msg.edit(embed=embed(
                "⚠️ Timeout 🍆",
                "El servidor ATM9 MODPACK está encendiendo pero tardó más de lo esperado.\nUsa `!estado` para verificar 🍆.",
                discord.Color.orange(),
            ))

    except ClientError as exc:
        await ctx.reply(embed=embed("❌ Error AWS", str(exc), discord.Color.red()))


@bot.command(name="apagar", aliases=["stop", "off"])
async def cmd_apagar(ctx: commands.Context):
    """🔴 Apaga la instancia EC2"""
    if not has_permission(ctx):
        await ctx.reply("❌ No tienes permiso para usar este comando.")
        return

    try:
        info = await get_instance_info()

        if info["state"] == "stopped":
            await ctx.reply(embed=embed(
                "🔴 Ya está apagado",
                "El servidor **ATM9 MODPACK** ya está **stopped**.",
                discord.Color.red(),
            ))
            return

        if info["state"] != "running":
            await ctx.reply(embed=embed(
                "⏳ Estado actual",
                f"El servidor **ATM9 MODPACK** está en estado `{info['state']}`, espera a que termine antes de apagar.",
                discord.Color.yellow(),
            ))
            return

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, lambda: ec2.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
        )

        msg = await ctx.reply(embed=embed(
            "⏳ Apagando ATM9 MODPACK...",
            f"Apagando servidor **ATM9 MODPACK** (`{EC2_INSTANCE_ID}`)...\nEspera, te aviso cuando se apague.",
            discord.Color.orange(),
        ))

        result = await wait_for_state("stopped", timeout=120)

        if result:
            await msg.edit(embed=embed(
                "🔴 ATM9 MODPACK Apagado",
                (
                    f"**El servidor ATM9 MODPACK se apagó correctamente** ✅\n\n"
                    f"**Servidor:** ATM9 MODPACK\n"
                    f"**ID:** `{EC2_INSTANCE_ID}`\n"
                    f"**Estado:** `stopped`"
                ),
                discord.Color.red(),
            ))
            await ctx.send(f"🔔 {ctx.author.mention} El servidor **ATM9 MODPACK** está **APAGADO**.")
        else:
            await msg.edit(embed=embed(
                "⚠️ Timeout",
                "El servidor ATM9 MODPACK está apagando pero tardó más de lo esperado.\nUsa `!estado` para verificar.",
                discord.Color.orange(),
            ))

    except ClientError as exc:
        await ctx.reply(embed=embed("❌ Error AWS", str(exc), discord.Color.red()))


@bot.command(name="estado", aliases=["status", "info"])
async def cmd_estado(ctx: commands.Context):
    """📊 Muestra el estado actual de la instancia EC2"""
    if not has_permission(ctx):
        await ctx.reply("❌ No tienes permiso para usar este comando.")
        return

    try:
        info = await get_instance_info()

        emojis = {"running": "🟢", "stopped": "🔴", "pending": "🟡", "stopping": "🟠"}
        colors = {
            "running": discord.Color.green(),
            "stopped": discord.Color.red(),
            "pending": discord.Color.yellow(),
            "stopping": discord.Color.orange(),
        }

        await ctx.reply(embed=embed(
            f"{emojis.get(info['state'], '⚪')} Estado de ATM9 MODPACK 🍆",
            (
                f"🍆 **Servidor:** ATM9 MODPACK\n"
                f"**ID:** `{EC2_INSTANCE_ID}`\n"
                f"**Estado:** `{info['state']}` 🍆\n"
                f"**IP Pública:** `{info['ip']}`\n"
                f"**Tipo:** `{info['type']}`\n"
                f"**Región:** `{AWS_REGION}`"
            ),
            colors.get(info["state"], discord.Color.greyple()),
            image_url=ATM9_IMAGE_URL,
        ))

    except ClientError as exc:
        await ctx.reply(embed=embed("❌ Error AWS", str(exc), discord.Color.red()))


@bot.command(name="ayuda", aliases=["help", "comandos", "commands"])
async def cmd_ayuda(ctx: commands.Context):
    """📖 Muestra los comandos disponibles"""
    await ctx.reply(embed=embed(
        "📖 Comandos Disponibles - ATM9 MODPACK 🍆",
        (
            "**🟢 Encender el servidor:**\n"
            "`!prender` · `!encender` · `!start` · `!on`\n\n"
            "**🔴 Apagar el servidor:**\n"
            "`!apagar` · `!stop` · `!off`\n\n"
            "**📊 Ver el estado:**\n"
            "`!estado` · `!status` · `!info`\n\n"
            "**🎤 JB THE VOICE:**\n"
            "`!jbthevoice` · `!jb` · `!thevoice`\n\n"
            "**📖 Ver esta ayuda:**\n"
            "`!ayuda` · `!help` · `!comandos`\n\n"
            "─────────────────────────\n"
            f"🍆 Servidor: **ATM9 MODPACK**\n"
            f"📡 Instancia: `{EC2_INSTANCE_ID}`\n"
            f"🌎 Región: `{AWS_REGION}`"
        ),
        discord.Color.blue(),
    ))


@bot.command(name="jbthevoice", aliases=["jb", "thevoice"])
async def cmd_jbthevoice(ctx: commands.Context):
    """🎤 Muestra la imagen de JB THE VOICE"""
    await ctx.reply(embed=embed(
        "🎤 JB THE VOICE",
        "🎙️ ¡Aquí está JB THE VOICE!",
        discord.Color.purple(),
        image_url=JB_THE_VOICE_IMAGE_URL,
    ))


# ─── Manejo de errores ──────────────────────────────────────────────────────

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignorar comandos desconocidos
    await ctx.reply(embed=embed("❌ Error", str(error), discord.Color.red()))


# ─── Ejecutar ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

from time import *
import logging
from logging import INFO, error, DEBUG
import asyncio
import os
import datetime
import random
import aiofiles

import discord
from discord import colour
from discord import embeds
from discord.channel import TextChannel
from discord.embeds import Embed

from discord.ext import commands
from discord.ext.commands import MissingPermissions, has_permissions, has_role
from discord.flags import Intents
from discord_slash import SlashCommand, SlashContext, error
from dotenv import load_dotenv
from discord_slash.utils.manage_commands import create_option, create_choice

load_dotenv(dotenv_path="config")

default_intents = discord.Intents.default()
default_intents.members=True

bot = commands.Bot(command_prefix="/", intents=default_intents)
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands=True)

channel_logs = bot.get_channel(848578058906238996)

image_error="https://i.ibb.co/tHWL83V/acces-denied.png"
image_acces="https://i.ibb.co/"

full_date = datetime.datetime.now()
date = full_date.strftime('%Y-%m-%d:%H:%M:%S')

bot.warnings = {} # guild_id : {user_id: [count, [(author_id, raison, preuve)]]}

try:
    logging.basicConfig(filename=f"logs/smogy.log", level=logging.INFO,
    #logging.basicConfig(filename=f"logs/{date}.log", level=logging.INFO, 
        format='%(asctime)s:%(levelname)s:%(message)s')
except FileNotFoundError:
    os.mkdir('logs')
    logging.basicConfig(filename=f"logs/{date}.log", level=logging.INFO, 
        format='%(asctime)s:%(levelname)s:%(message)s')

async def sanctions_files():
    for guild in bot.guilds:
        bot.warnings[guild.id] = {}
        
        try:
            async with aiofiles.open(f"sanctions/{guild.id}.txt", mode="a") as temp:
                pass
        except FileNotFoundError:
            os.makedirs('sanctions')
            async with aiofiles.open(f"sanctions/{guild.id}.txt", mode="a") as temp:
                pass

        async with aiofiles.open(f"sanctions/{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                sanction_id = int(data[2])
                reason = " ".join(data[3:]).strip("\n")

                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append((admin_id, sanction_id, reason))

                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, sanction_id, reason)]]

@bot.event
async def on_ready():
    try:
        await sanctions_files()
    except:
        pass
    await bot.change_presence(activity=discord.Streaming(name="/help", url="https://www.twitch.tv/Smogy"))
    logging.info("Bot pret !")

@bot.event
async def on_member_join(member):
    logging.info(f"{member} as join the discord")
    channel = bot.get_channel(848561158206259211)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0x00ff4c
    elif rand_numb == 2:
        color = 0x00f7ff
    elif rand_numb == 3:
        color = 0xeb3495
    channel:TextChannel = await bot.fetch_channel(848561158206259211)
    embed=discord.Embed(title="Bienvenue", description=f"{member.mention}, bienvenue sur le discord de **Smogy** !", color=color)
    embed.set_author(name="Smogy BOT", url="https://www.twitch.tv/Smogy", icon_url="https://i.imgur.com/ChQwvkA.png")
    embed.set_thumbnail(url="https://i.imgur.com/ChQwvkA.png")
    embed.set_footer(text=f"Date • {datetime.datetime.now()}")
    await channel.send(embed=embed)


@slash.slash(name="Clear", description="Effacer des messages", options=[
                create_option(
                    name="nombre",
                    description="Indiquer le nombre de message à clear",
                    option_type=4,
                    required=True),
             ])
@has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    await ctx.defer(hidden=True)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0xfff04f
    elif rand_numb == 2:
        color = 0x554fff
    elif rand_numb == 3:
        color = 0xff6eff
    channel_logs = bot.get_channel(848578058906238996)
    messages = await ctx.channel.history(limit=nombre + 1).flatten()
    for message in messages:
        await message.delete()
    embed = discord.Embed(title=f"Le channel {ctx.channel} a été clear !", color=color)
    embed.set_thumbnail(url=image_acces)
    embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed.add_field(name="Nombre de messages supprimés", value=nombre, inline=False)
    embed.set_footer(text=f"Date • {datetime.datetime.now()}")
    await channel_logs.send(embed=embed)
    await ctx.send(embed=discord.Embed(description=f"Le channel **{ctx.channel}** a été clear :white_check_mark:", color=0x34eb37), hidden=True)
    logging.info(f"{ctx.author} a clear {nombre} messages dans le channel {ctx.channel}")

@error.SlashCommandError
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **manage_messages**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)


@slash.slash(name="Ban", description="Bannir un membre définitivement", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être ban",
                    option_type=6,
                    required=True),
                create_option(
                    name="raison",
                    description="Indiquer la raison du ban",
                    option_type=3,
                    required=False),
             ])
@has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, raison="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    try:
        bot.warnings[ctx.guild.id][user.id][0] += 1
        bot.warnings[ctx.guild.id][user.id][1].append((ctx.author.id, 1,raison))
    except KeyError:
        bot.warnings[ctx.guild.id][user.id] = [1, [(ctx.author.id, 1,raison)]]

    async with aiofiles.open(f"sanctions/{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{user.id} {ctx.author.id} 1 {raison}\n")
    channel_logs = bot.get_channel(848578058906238996)
    embed = discord.Embed(title=f"{user.name} a été **ban** !",
                          description="Cet utilisateur n'a pas respecté les règles du serveur !", color=0xcc0202)
    embed.set_thumbnail(url=image_acces)
    embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
    embed.add_field(name="Raison", value=raison, inline=True)
    embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed.set_footer(text=f"Date • {datetime.datetime.now()}")
    await channel_logs.send(embed=embed)
    embed_user = discord.Embed(title="Vous avez été banni !",
                               description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                           "Si la raison de votre bannissement vous semble incorrecte, "
                                           "vous pouvez contacter le modérateur qui vous a banni !", color=0xcc0202)
    embed_user.set_thumbnail(url= image_acces)
    embed_user.add_field(name="Raison", value=raison, inline=True)
    embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
    await user.send(embed=embed_user)
    await ctx.guild.ban(user, reason=raison)
    await ctx.send(embed=discord.Embed(description=f"Vous avez banni **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
    logging.info(f"{ctx.author} a banni {user}, raison : {raison}")

@error.SlashCommandError
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **ban_members**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)

@slash.slash(name="Kick", description="Exclure un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être kick",
                    option_type=6,
                    required=True),
                create_option(
                    name="reason",
                    description="Indiquer la raison du kick",
                    option_type=3,
                    required=False),
             ])
@has_permissions(kick_members=True)
async def kick(ctx, user: discord.User, *, reason="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    try:
        bot.warnings[ctx.guild.id][user.id][0] += 1
        bot.warnings[ctx.guild.id][user.id][1].append((ctx.author.id, 3,reason))
    except KeyError:
        bot.warnings[ctx.guild.id][user.id] = [1, [(ctx.author.id, 3,reason)]]

    async with aiofiles.open(f"sanctions/{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{user.id} {ctx.author.id} 3 {reason} Warn\n")
    channel_logs = bot.get_channel(848578058906238996)
    embed = discord.Embed(title=f"{user.name} a été **kick** !",
                          description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=0xa8324e)
    embed.set_thumbnail(url=image_acces)
    embed.add_field(name="Utilisateur kick", value=user.mention, inline=True)
    embed.add_field(name="Raison", value=reason, inline=True)
    embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed.set_footer()
    await channel_logs.send(embed=embed)
    embed_user = discord.Embed(title="Vous avez été kick !",
                               description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                           "Si la raison de votre kick vous semble incorrecte, "
                                           "vous pouvez contacter le modérateur qui vous a kick"
                                           "vous pouvez revenir sur le serveur via le lien ci-dessous.", color=0xa8324e)
    embed_user.set_thumbnail(url=image_error)
    embed_user.add_field(name="Raison", value=reason, inline=True)
    embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
    await user.send(embed=embed_user)
    await ctx.guild.kick(user, reason=reason)
    await ctx.send(embed=discord.Embed(description=f"Vous avez kick **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
    channel_logs = bot.get_channel(848578058906238996)
    
@error.SlashCommandError
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **kick_members**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)


@slash.slash(name="Unban", description="De-bannir un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être unban, sous cette forme exemple ``user#1234``",
                    option_type=3,
                    required=True),
                create_option(
                    name="raison",
                    description="Indiquer la raison de l'unban",
                    option_type=3,
                    required=False),
             ])
@has_permissions(ban_members=True)
async def unban(ctx, user, *, raison="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0x32a852
    elif rand_numb == 2:
        color = 0x5eff8a
    elif rand_numb == 3:
        color = 0x3fc463
    channel_logs = bot.get_channel(848578058906238996)
    banned_users = await ctx.guild.bans()
    user_name, user_discriminator = user.split('#')
    unban_logs = discord.Embed(title=f"**{user}** a été dé-banni", color=color)
    unban_logs.set_thumbnail(url=image_acces)
    unban_logs.add_field(name="Raison", value=raison, inline=True)
    unban_logs.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    unban_logs.set_footer(text=f"Date • {datetime.datetime.now()}")
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (user_name, user_discriminator):
            await ctx.guild.unban(user, reason=raison)
            await channel_logs.send(embed=unban_logs)
    await ctx.send(embed=discord.Embed(description=f"Vous avez de-banni **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
    logging.info(f"{ctx.author} a dé-banni {user}, raison : {raison}")

@error.SlashCommandError
async def unban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **ban_members**",
                              color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)

@slash.slash(name="banlist", description="Permet d'obtenir la liste des membres bannis")
@has_permissions(ban_members=True)
async def banlist(ctx):
    await ctx.defer(hidden=True)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0xc43f3f
    elif rand_numb == 2:    
        color = 0xc45e3f
    elif rand_numb == 3:
        color = 0xc43f72
    banned_users_list = await ctx.guild.bans()
    embed = discord.Embed(title="Voici la liste des membres bannis du discord", color=color)
    for banned_users in banned_users_list:
        embed.add_field(name=f"{banned_users.user.name}#{banned_users.user.discriminator}",
         value=f"Raison du ban : **{banned_users.reason}**, ID : **{banned_users.user.id}**",
          inline=False)
    await ctx.send(embed=embed, hidden=True)

@slash.slash(name="Tempban", description="Bannir temporairement un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être ban",
                    option_type=6,
                    required=True),
                create_option(
                    name="duration",
                    description="Cette option doit être un nombre",
                    option_type=4,
                    required=True),
                create_option(
                    name="time",
                    description="seconde / minute / heure / mois",
                    option_type=3,
                    required=True,
                    choices=[
                 create_choice(
                    name="seconde",
                    value="s"
                  ),
                create_choice(
                    name="minute",
                    value="m"
                  ),
                create_choice(
                    name="heure",
                    value="h"
                  ),
                create_choice(
                    name="jour",
                    value="j"
                  ),
                create_choice(
                    name="mois",
                    value="mois"),
                ]),
                create_option(
                    name="raison",
                    description="Indiquer la raison du ban",
                    option_type=3,
                    required=False),
             ])
@has_permissions(ban_members=True)
async def tempban(ctx, user: discord.User, duration: int, time: str, *, raison="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    try:
        bot.warnings[ctx.guild.id][user.id][0] += 1
        bot.warnings[ctx.guild.id][user.id][1].append((ctx.author.id, 4,raison))
    except KeyError:
        bot.warnings[ctx.guild.id][user.id] = [1, [(ctx.author.id, 4,raison)]]

    async with aiofiles.open(f"sanctions/{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{user.id} {ctx.author.id} 4 {raison}\n")
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0xd459d9
    elif rand_numb == 2:
        color = 0x5973d9    
    elif rand_numb == 3:
        color = 0xd95959
    channel_logs = bot.get_channel(848578058906238996)
    author = ctx.author
    if "s" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez banni temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)

        embed = discord.Embed(title=f"{user.name} a été **ban temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} seconde(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        embed.set_thumbnail(url=image_acces)
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été banni temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre ban vous semble incorrecte, "
                                               "vous pouvez contacter le modérateur qui vous a banni."
                                               "**Vous pourrez revenir sur le serveur via le lien ci-dessous une fois que votre ban "
                                               "sera terminé.**",
                                   color=color)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} seconde(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        embed_user.set_thumbnail(url=image_error)
        await user.send(embed=embed_user)
        await ctx.guild.ban(user, reason=raison)
        await asyncio.sleep(duration)
        await ctx.guild.unban(user)
        logging.info(f"{ctx.author} a banni temporairement {user} : {duration} {time}, raison : {raison}")
    elif "m" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez banni temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)

        duration_min = duration * 60
        embed = discord.Embed(title=f"{user.name} a été **ban temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} minute(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été banni temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre ban vous semble incorrecte, "
                                               "vous pouvez contacter le modérateur qui vous a banni."
                                               "**Vous pourrez revenir sur le serveur via le lien ci-dessous une fois que votre ban "
                                               "sera terminé.**",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} minute(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await ctx.guild.ban(user, reason=raison)
        await asyncio.sleep(duration_min)
        await ctx.guild.unban(user)
        logging.info(f"{ctx.author} a banni temporairement {user} : {duration} {time}, raison : {raison}")
    elif "h" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez banni temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)

        duration_heure = duration * 3600
        embed = discord.Embed(title=f"{user.name} a été **ban temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} heure(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été banni temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre ban vous semble incorrecte, "
                                               "vous pouvez contacter le modérateur qui vous a banni."
                                               "**Vous pourrez revenir sur le serveur via le lien ci-dessous une fois que votre ban "
                                               "sera terminé.**",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} heure(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await ctx.guild.ban(user, reason=raison)
        await asyncio.sleep(duration_heure)
        await ctx.guild.unban(user)
        logging.info(f"{ctx.author} a banni temporairement {user} : {duration} {time}, raison : {raison}")
    elif "j" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez banni temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)

        duration_jour = duration * 86400
        embed = discord.Embed(title=f"{user.name} a été **ban temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} jour(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été banni temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre ban vous semble incorrecte, "
                                               "vous pouvez contacter le modérateur qui vous a banni."
                                               "**Vous pourrez revenir sur le serveur via le lien ci-dessous une fois que votre ban "
                                               "sera terminé.**",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} jour(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await ctx.guild.ban(user, reason=raison)
        await asyncio.sleep(duration_jour)
        await ctx.guild.unban(user)
        logging.info(f"{ctx.author} a banni temporairement {user} : {duration} {time}, raison : {raison}")
    elif "mois" == duration:
        await ctx.send(embed=discord.Embed(description=f"Vous avez banni temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)

        duration_mois = duration * 86400 * 30
        embed = discord.Embed(title=f"{user.name} a été **ban temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur banni", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} mois", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été banni temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre ban vous semble incorrecte, "
                                               "vous pouvez contacter le modérateur qui vous a banni. "
                                               "**Vous pourrez revenir sur le serveur via le lien ci-dessous une fois que votre ban "
                                               "sera terminé.**",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} mois", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.add_field(name="Discord", value="https://discord.gg/fqEpWkQdcf", inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await ctx.guild.ban(user, reason=raison)
        await asyncio.sleep(duration_mois)
        await ctx.guild.unban(user)
        logging.info(f"{ctx.author} a banni temporairement {user} : {duration} {time}, raison : {raison}")

    else:
        author = ctx.author
        embed = discord.Embed(title="Valeur de l'argument **[temps]** est inconnue",
                              description=f"{author.mention} L'argument [temps] doit être : **[s, m, j, mois]**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        embed.add_field(name="s", value="seconde(s)", inline=True)
        embed.add_field(name="h", value="heure(s)", inline=True)
        embed.add_field(name="j", value="jour(s)", inline=True)
        embed.add_field(name="mois", value="mois", inline=True)
        await ctx.send(embed=embed, hidden=True)


@error.SlashCommandError
async def tempban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **ban_members**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)


async def createRoleMute(ctx):
    role_mute = await ctx.guild.create_role(name = "mute",
                                            permissions= discord.Permissions(send_messages= False, speak= False))
    for channel in ctx.guild.channels:
        await channel.set_permissions(role_mute, send_messages=False, speak= False)

async def getRoleMute(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "mute":
            return role

    return await createRoleMute(ctx)

@slash.slash(name="Tempmute", description="Rendre muet temporairement un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être mute",
                    option_type=6,
                    required=True),
                create_option(
                    name="duration",
                    description="Cette option doit être un nombre",
                    option_type=4,
                    required=True),
                create_option(
                    name="time",
                    description="seconde / minute / heure / mois",
                    option_type=3,
                    required=True,
                    choices=[
                 create_choice(
                    name="seconde",
                    value="s"
                  ),
                create_choice(
                    name="minute",
                    value="m"
                  ),
                create_choice(
                    name="heure",
                    value="h"
                  ),
                create_choice(
                    name="jour",
                    value="j"
                  ),
                create_choice(
                    name="mois",
                    value="mois"),
                ]),
                create_option(
                    name="raison",
                    description="Indiquer la raison du mute",
                    option_type=3,
                    required=False),
             ])
@has_permissions(manage_roles=True)
async def tempmute(ctx, user: discord.User, duration: int, time: str, *, raison="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    try:
        bot.warnings[ctx.guild.id][user.id][0] += 1
        bot.warnings[ctx.guild.id][user.id][1].append((ctx.author.id, 2,raison))
    except KeyError:
        bot.warnings[ctx.guild.id][user.id] = [1, [(ctx.author.id, 2,raison)]]

    async with aiofiles.open(f"sanctions/{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{user.id} {ctx.author.id} 2 {raison}\n")
    channel_logs = bot.get_channel(848578058906238996)
    role_mute = await getRoleMute(ctx)
    author = ctx.author
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0xedda5f
    elif rand_numb == 2:
        color = 0xedab5f
    elif rand_numb == 3:
        color = 0xbb76f5
    if "s" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez mute temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
        embed = discord.Embed(title=f"{user.name} a été **mute temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.add_field(name="Utilisateur mute", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} seconde(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        embed.set_thumbnail(url=image_acces)
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été mute temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre mute vous semble incorrecte, "
                                               "vous vous contacter le modérateur qui vous a mute.",
                                   color=color)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de mute", value=f"{duration} seconde(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        embed_user.set_thumbnail(url=image_error)
        await user.send(embed=embed_user)
        await user.add_roles(role_mute, reason=raison)
        await asyncio.sleep(duration)
        await user.remove_roles(role_mute, reason="Fin de la période de mute")
        logging.info(f"{ctx.author} a mute temporairement {user} : {duration} {time}, raison : {raison}")
    elif "m" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez mute temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
        duration_min = duration * 60
        embed = discord.Embed(title=f"{user.name} a été **mute temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur mute", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} minute(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été mute temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre mute vous semble incorrecte, "
                                               "vous vous contacter le modérateur qui vous a mute.",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de mute", value=f"{duration} minute(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await user.add_roles(role_mute, reason=raison)
        await asyncio.sleep(duration_min)
        await user.remove_roles(role_mute, reason="Fin de la période de mute")
        logging.info(f"{ctx.author} a mute temporairement {user} : {duration} {time}, raison : {raison}")
    elif "h" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez mute temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
        duration_heure = duration * 3600
        embed = discord.Embed(title=f"{user.name} a été **mute temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur mute", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} heure(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été mute temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre mute vous semble incorrecte, "
                                               "vous vous contacter le modérateur qui vous a mute.",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de banissement", value=f"{duration} heure(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await user.add_roles(role_mute, reason=raison)
        await asyncio.sleep(duration_heure)
        await user.remove_roles(role_mute, reason="Fin de la période de mute")
        logging.info(f"{ctx.author} a mute temporairement {user} : {duration} {time}, raison : {raison}")
    elif "j" == time:
        await ctx.send(embed=discord.Embed(description=f"Vous avez mute temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
        duration_jour = duration * 86400
        embed = discord.Embed(title=f"{user.name} a été **mute temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur mute", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} jour(s)", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été mute temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre mute vous semble incorrecte, "
                                               "vous vous contacter le modérateur qui vous a mute.",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de mute", value=f"{duration} jour(s)", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await user.add_roles(role_mute, reason=raison)
        await asyncio.sleep(duration_jour)
        await user.remove_roles(role_mute, reason="Fin de la période de mute")
        logging.info(f"{ctx.author} a mute temporairement {user} : {duration} {time}, raison : {raison}")
    elif "mois" == duration:
        await ctx.send(embed=discord.Embed(description=f"Vous avez mute temporairement **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
        duration_mois = duration * 86400 * 30
        embed = discord.Embed(title=f"{user.name} a été **mute temporairement** !",
                              description=f"Cet utilisateur n'a pas respecté les règles du serveur !", color=color)
        embed.set_thumbnail(url=image_acces)
        embed.add_field(name="Utilisateur mute", value=user.mention, inline=True)
        embed.add_field(name="Raison", value=raison, inline=True)
        embed.add_field(name="Durée", value=f"{duration} mois", inline=True)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await channel_logs.send(embed=embed)
        embed_user = discord.Embed(title="Vous avez été mute temporairement !",
                                   description="Il semblerait que vous n'ayez pas respecté les règles du serveur. "
                                               "Si la raison de votre mute vous semble incorrecte, "
                                               "vous vous contacter le modérateur qui vous a mute.",
                                   color=color)
        embed_user.set_thumbnail(url=image_error)
        embed_user.add_field(name="Raison", value=raison, inline=True)
        embed_user.add_field(name="Temps de mute", value=f"{duration} mois", inline=True)
        embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
        embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
        await user.send(embed=embed_user)
        await user.add_roles(role_mute, reason=raison)
        await asyncio.sleep(duration_mois)
        await user.remove_roles(role_mute, reason="Fin de la période de mute")
        logging.info(f"{ctx.author} a mute temporairement {user} : {duration} {time}, raison : {raison}")
    else:
        author = ctx.author
        embed = discord.Embed(title="Valeur de l'argument **[temps]** est inconnue",
                              description=f"{author.mention} L'argument [temps] doit être : **[s, m, j, mois]**",
                              color=0xf09400)
        embed.set_thumbnail(url=image_error)
        embed.add_field(name="s", value="seconde(s)", inline=True)
        embed.add_field(name="h", value="heure(s)", inline=True)
        embed.add_field(name="j", value="jour(s)", inline=True)
        embed.add_field(name="mois", value="mois", inline=True)
        embed.set_footer(text=f"Date • {datetime.datetime.now()}")
        await ctx.send(embed=embed, hidden=True)


@error.SlashCommandError
async def tempmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **manage_roles**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)

@slash.slash(name="Unmute", description="Ne plus rendre muet un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être unmute",
                    option_type=6,
                    required=True),
                create_option(
                    name="raison",
                    description="Indiquer la raison de l'unmute",
                    option_type=3,
                    required=False),
             ])
@has_permissions(manage_roles=True)
async def unmute(ctx, user: discord.User, *, raison="Aucune raison fournie"):
    await ctx.defer(hidden=True)
    channel_logs = bot.get_channel(848578058906238996)
    role_mute = await getRoleMute(ctx)

    await user.remove_roles( role_mute, reason=raison)
    embed = discord.Embed(title=f"{user} été de-mute !",
                              description="Il peut maintenant re-parler dans le chat !",
                              color=0x42f557)
    embed.set_thumbnail(url=image_acces)
    embed.add_field(name="Raison", value=raison, inline=True)
    embed.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed.set_footer(text=f"Date • {datetime.datetime.now()}")
    await channel_logs.send(embed=embed)
    embed_user = discord.Embed(title="Vous avez été de-mute !",
                               description="Vous pouvez maintenant re-parler dans le chat !",
                               color=0x42f557)
    embed_user.set_thumbnail(url=image_acces)
    embed_user.add_field(name="Raison", value=raison, inline=True)
    embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
    await user.send(embed=embed_user)
    await ctx.send(embed=discord.Embed(description=f"Vous avez de-mute **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
    logging.info(f"{ctx.author} a unmute {user}, raison : {raison}")

@error.SlashCommandError
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        author = ctx.author
        embed = discord.Embed(title="Permissions insufisantes",
                              description=f"{author.mention} Vous devez avoir la permission : **manage_roles**", color=0xf09400)
        embed.set_thumbnail(url=image_error)
        await author.send(embed=embed)


@slash.slash(name="report", description="Report un membre", permissions="",     options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être report",
                    option_type=6,
                    required=True),
                create_option(
                    name="raison",
                    description="Indiquer la raison du report",
                    option_type=3,
                    required=True),
                create_option(
                    name="preuve",
                    description="Indiquer une preuve",
                    option_type=3,
                    required=False),
             ])
async def report(ctx, user: discord.User, raison, *, preuve="Aucune preuve fournie"):
    await ctx.defer(hidden=True)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0x34ebe5
    elif rand_numb == 2:
        color = 0x2f5da
    elif rand_numb == 3:
        color = 0x42f575
    channel_logs = await bot.fetch_channel(848578058906238996)
    embed = discord.Embed(title=f"{ctx.author} a report {user}", color=color)
    embed.add_field(name="Raison", value=raison, inline=True)
    embed.add_field(name="Preuve", value=preuve, inline=True)
    embed.set_footer(text=f"Date • {datetime.datetime.now()}")
    if preuve != "Aucune preuve fournie":
        if preuve.endswith(".png") or preuve.endswith(".jpg") or preuve.endswith(".gif"):
            embed.set_thumbnail(url=preuve)
        else:
            pass
    else:
            pass
    await channel_logs.send(embed=embed)
    logging.info(f"{ctx.author} a report {user}, raison : {raison}, preuve : {preuve}")
    await ctx.send(embed=discord.Embed(description=f"Vous avez report **{user}** :white_check_mark:", color=0x34eb37), hidden=True)


@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}


@slash.slash(name="warn", description="Avertir un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être warn",
                    option_type=6,
                    required=True),
                create_option(
                    name="raison",
                    description="Entrez la raison du warn",
                    option_type=3,
                    required=True)
            ])
@has_permissions(manage_roles=True)
async def warn(ctx, user: discord.User, raison):
    await ctx.defer(hidden=True)
    channel_logs = await bot.fetch_channel(848578058906238996)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0xedda5f
    elif rand_numb == 2:
        color = 0xedab5f
    elif rand_numb == 3:
        color = 0xbb76f5
    try:
        bot.warnings[ctx.guild.id][user.id][0] += 1
        bot.warnings[ctx.guild.id][user.id][1].append((ctx.author.id, 1,raison))
    except KeyError:
        bot.warnings[ctx.guild.id][user.id] = [1, [(ctx.author.id, 1,raison)]]

    async with aiofiles.open(f"sanctions/{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{user.id} {ctx.author.id} 1 {raison}\n")
    logging.info(f"{ctx.author} a warn {user}, raison : {raison}")
    await ctx.send(embed=discord.Embed(description=f"Vous avez warn **{user}** :white_check_mark:", color=0x34eb37), hidden=True)
    embed_user = discord.Embed(title="Vous avez été warn !", color=color)
    embed_user.set_thumbnail(url=image_error)
    embed_user.add_field(name="Raison", value=raison, inline=True)
    embed_user.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed_user.set_footer(text=f"Date • {datetime.datetime.now()}")
    await user.send(embed=embed_user)
    embed_logs = discord.Embed(title=f"{user} a été warn !", color=color)
    embed_logs.set_thumbnail(url=image_acces)
    embed_logs.add_field(name="Raison", value=raison, inline=True)
    embed_logs.add_field(name="Modérateur", value=ctx.author.mention, inline=True)
    embed_logs.set_footer(text=f"Date • {datetime.datetime.now()}")
    await channel_logs.send(embed=embed_logs)
    
async def get_sanction_id(sanction_id):
    if sanction_id==1:
        return "warn"
    elif sanction_id==2:
        return "tempmute"
    elif sanction_id==3:
        return "kick"
    elif sanction_id==4:
        return "tempban"
    elif sanction_id==5:
        return "ban"

@slash.slash(name="sanctions", description="Permet d'obtenir la liste des sanctions d'un membre", options=[
                create_option(
                    name="user",
                    description="Entrez l'user qui doit être warn",
                    option_type=6,
                    required=True)
            ])
@has_permissions(manage_roles=True)
async def sanctions(ctx, user: discord.User):
    await ctx.defer(hidden=True)
    rand_numb = random.randint(1, 3)
    if rand_numb == 1:
        color = 0x34ebe5
    elif rand_numb == 2:
        color = 0x2f5da
    elif rand_numb == 3:
        color = 0x42f575
    try:
        try:
            await sanctions_files()
        except:
            pass
        i = 1
        embed = discord.Embed(title=f"Listes des sanctions de {user}", description=":warning:",colour=color)
        for author_id, sanction_id, raison in bot.warnings[ctx.guild.id][user.id][1]:
            sanction_name = await get_sanction_id(sanction_id)
            author = ctx.guild.get_member(author_id)
            embed.add_field(name=f"{i}. Sanction : **{sanction_name}**", value=f"Raison : **{raison}**, Modérateur : **{author}**", inline=False)
            embed.set_footer(text=user, icon_url=user.avatar_url)
            i += 1
        await ctx.send(embed=embed, hidden=True)
    except KeyError: # no warnings
        embed = discord.Embed(title=f"Listes des sanctions de {user}", colour=color, description=f"Ce membre n'a aucune sanction !")
        embed.set_footer(text=user, icon_url=user.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    logging.info(f"{ctx.author} a utilisé la commande /sanctions {user}")
 

@slash.slash(name="help", description="Permet d'obtenir des renseignements à propos des commandes", options=[
                create_option(
                    name="command",
                    description="Renseignement à propos des commandes du bot",
                    option_type=3,
                    required=True,
                    choices=[
                 create_choice(
                    name="all commands",
                    value="all_commands"
                ),
                create_choice(
                    name="clear",
                    value="clear"
                  ),
                create_choice(
                    name="kick",
                    value="kick"
                  ),
                create_choice(
                    name="ban",
                    value="ban"
                  ),
                create_choice(
                    name="unban",
                    value="unban"
                  ),
                create_choice(
                    name="tempban",
                    value="tempban"
                  ),
                create_choice(
                    name="tempmute",
                    value="tempmute"
                  ),
                create_choice(
                    name="sanctions",
                    value="sanctions"
                ),
                create_choice(
                    name="unmute",
                    value="unmute"
                  ),
                create_choice(
                    name="report",
                    value="report"),
                create_choice(
                    name="banlist",
                    value="banlist"
                ),
                create_choice(
                    name="warn",
                    value="warn"
                )
                ]),
             ])
async def help(ctx, command):
    await ctx.defer(hidden=True)
    if command == "all_commands":
        author = ctx.author
        embed= discord.Embed(title="Liste de toutes les commandes les commandes",
        color=0x00ffaa)
        embed.add_field(name="``/clear``"
        , value="Cette commande permet d'effacer un certains nombre de message, pour plus de renseignement faites **/help clear**", inline=False)
        embed.add_field(name="``/kick``"
        , value="Cette commande permet d'expulser un membre du discord, pour plus de renseignement faites **/help kick**", inline=False)
        embed.add_field(name="``/ban``"
        , value="Cette commande permet de bannir un membre du discord, pour plus de renseignement faites **/help ban**", inline=False)
        embed.add_field(name="``/unban``"
        , value="Cette commande permet de dé-bannir un membre du discord, pour plus de renseignement faites **/help unban**", inline=False)
        embed.add_field(name="``/tempban``"
        , value="Cette commande permet de bannir temporairement un membre du discord, pour plus de renseignement faites **/help tempban**", inline=False)
        embed.add_field(name="``/tempmute``"
        , value="Cette commande permet de mute temporairement un membre du discord, pour plus de renseignement faites **/help tempmute**", inline=False)
        embed.add_field(name="``/unmute``"
        , value="Cette commande permet dé-mute un membre du discord, pour plus de renseignement faites **/help unmute**", inline=False)
        embed.add_field(name="``/report``"
        , value="Cette commande permet de report un membre du discord pour plus de renseignement faites **/help report**", inline=False)
        embed.add_field(name="``/banlist``"
        , value="Cette commande permet d'obtenir la listes des membres bannis du discord, pour plus de renseignement faites **/help banlist**", inline=False)
        embed.add_field(name="``/sanctions``"
        , value="Cette commande permet d'obtenir la listes des sanctions d'un membre du discord, pour plus de renseignement faites **/help sanctions**", inline=False)
        embed.add_field(name="``/warn``"
        , value="Cette commande permet d'avertir un membre du discord, pour plus de renseignement faites **/help banlist**", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "clear":
        author = ctx.author
        embed= discord.Embed(title="Commande clear", description="***/clear***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet d'effacer un certains nombre de message", inline=False)
        embed.add_field(name="Utilisation", value="``/clear [nombre de message]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "kick":
        author = ctx.author
        embed= discord.Embed(title="Commande kick", description="***/kick***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet d'expulser un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/kick [membre] [*raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "ban":
        author = ctx.author
        embed= discord.Embed(title="Commande ban", description="***/ban***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet de bannir un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/ban [membre] [*raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "unban":
        author = ctx.author
        embed= discord.Embed(title="Commande unban", description="***/unban***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet de dé-bannir un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/unban [membre] [*raison]`` :warning: l'option **membre** doit être rempli sous cette forme ***user#1234***", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "tempban":
        author = ctx.author
        embed= discord.Embed(title="Commande tempban", description="***/tempban***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet de bannir temporairement un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/tempban [membre] [durée : nombre] [temps : seconde / minute / heure / jour / mois] [*raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "tempmute":
        author = ctx.author
        embed= discord.Embed(title="Commande tempmute", description="***/tempmute***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet de mute temporairement un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/tempmute [membre] [durée : nombre] [temps : seconde / minute / heure / jour / mois] [*raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "unmute":
        author = ctx.author
        embed= discord.Embed(title="Commande tempban", description="***/tempmute***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet dé-mute un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/unmute [membre] [*raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "report":
        author = ctx.author
        embed= discord.Embed(title="Commande report", description="***/report***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet de report un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/report [membre] [raison] [*preuve: :warning: url vers une image :warning:]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "banlist":
        author = ctx.author
        embed= discord.Embed(title="Commande banlist", description="***/banlist***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet d'obtenir la liste des membres bannis du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/banlist``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)      
    elif command == "sanctions":
        author = ctx.author
        embed= discord.Embed(title="Commande sanctions", description="***/sanctions***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande permet d'obtenir la liste des sanctions d'un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/sanctions [membre]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    elif command == "warn":
        author = ctx.author
        embed= discord.Embed(title="Commande warn", description="***/warn***",
        color=0x00ffaa)
        embed.add_field(name="A quoi sert cette commande ?", value="Cette commande d'avertir un membre du discord", inline=False)
        embed.add_field(name="Utilisation", value="``/warn [membre] [raison]``", inline=False)
        embed.set_footer(text=author, icon_url=author.avatar_url)
        await ctx.send(embed=embed, hidden=True)
    logging.info(f"{ctx.author} a utilisé la commande /help {command}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    phrase = message.content.split(" ")

    hey_list = ['Bonjour', 'bonjour', 'Bonsoir', 'bonsoir', 'Salut', 'salut',
     'Hey', 'hey', 'Hello', 'hello', 'Coucou', 'coucou']
    hey_respond_list = ['Bonjour', 'Bonsoir', 'Salut', 'Heyyy', 'Hello', 'Coucou']
    if phrase[0] in hey_list:
        await message.reply(random.choice(hey_respond_list), delete_after=5)
    await bot.process_commands(message)
        

@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(title="Error", description=error, color=0xeb4034), hidden=True)
    elif isinstance(error, discord.errors.HTTPException):
        pass
    elif isinstance(error, MissingPermissions):
        await ctx.send(embed=discord.Embed(title="Error", description=error, color=0xeb4034), hidden=True)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        pass
    elif isinstance(error, discord.errors.HTTPException):
        pass

bot.run(os.getenv("TOKEN"))
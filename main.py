import json
import os
import random
from datetime import datetime
import requests
import sqlalchemy as db

import discord
from discord import guild, ChannelType
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, BigInteger, String, DateTime, Column, insert
from pathlib import Path

from sqlalchemy.ext.automap import automap_base

load_dotenv()

uploads_path = Path(os.getenv('ATTACHMENTS_PATH'))

AUTHORIZED_USERS = ['ExampleUser#8650']

if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
    try:
        os.makedirs(uploads_path)
    except OSError as error:
        print(error)

engine = db.create_engine(os.getenv('DB_CONNECTION_STRING'), echo=False)
connection = engine.connect()
metadata = MetaData()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILD', '').split(',')
IGNORE_USERS = os.getenv('DISCORD_IGNORED_USERS', '').split(',')
ALLOW_BOTS = os.getenv('DISCORD_ALLOW_BOTS', 'FALSE')

intent = discord.Intents.default()
intent.members = True
intent.messages = True
intent.message_content = True

client = commands.Bot(command_prefix='!', intents = intent)

def get_caller(ctx):
    caller = f'{ctx.author.name}#{ctx.author.discriminator}'
    print(caller)
    return caller

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(discord.__version__)

@client.event
async def on_message(message):
    print(message)
    is_bot = message.author.bot
    author_name = message.author.name

    if (not len(GUILDS) or message.guild.name in GUILDS) and (author_name not in IGNORE_USERS):
        if not is_bot or (is_bot and ALLOW_BOTS == 'TRUE'):

            metadata.reflect(connection)

            is_forum = "parent" in dir(message.channel)

            parent = str(message.channel.parent) if is_forum else None

            table_name = f'{message.guild.name}_{parent or message.channel.name}'

            if not connection.dialect.has_table(engine.connect(), table_name):  # If table don't exist, Create.
                Table(table_name, metadata,
                      Column('id', BigInteger, primary_key=True, nullable=False),
                      Column('date', DateTime),
                      Column('guild', String),
                      Column('container', String),
                      Column('parent_name', String),
                      Column('channel_id', String),
                      Column('channel_name', String),
                      Column('author_id', BigInteger),
                      Column('author_name', String),
                      Column('author_discriminator', String),
                      Column('author_nick', String),
                      Column('message_content', String),
                      Column('message_attachments', String),
                      )
                metadata.create_all(connection)

            tbl = metadata.tables[table_name]

            attachments = [{'id': x.id, 'filename': x.filename, 'url': x.url} for x in list(message.attachments)]

            stmt = insert(tbl).values(
                id=message.id,
                date=datetime.now(),
                guild=str(message.guild.name),
                container='Thread/Forum' if is_forum else 'channel',
                parent_name=parent,
                channel_id=message.channel.id,
                channel_name=message.channel.name,
                author_id=message.author.id,
                author_name=message.author.name,
                author_discriminator=message.author.discriminator,
                author_nick=message.author.nick,
                message_content=message.content,
                message_attachments=json.dumps(attachments)
            )
            connection.execute(stmt)

            if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
                if len(attachments):
                    try:
                        if is_forum:
                            os.makedirs(uploads_path / table_name / f'{message.channel.name}')
                        else:
                            os.makedirs(uploads_path / table_name)
                    except OSError as error:
                        if 'File exists' not in str(error):
                            print(error)

                    for attachment in attachments:
                        req = requests.get(attachment['url'], allow_redirects=True)
                        if is_forum:
                            filepath = uploads_path / f'{table_name}' / f'{message.channel.name}' / f'({attachment["id"]}){attachment["filename"]}'
                        else:
                            filepath = uploads_path / f'{table_name}' / f'({attachment["id"]}){attachment["filename"]}'

                        open(filepath, 'wb').write(req.content)

@client.command()
async def announce(ctx):
    caller = get_caller(ctx)
    if caller in AUTHORIZED_USERS:
        channel = discord.utils.get(ctx.guild.channels, name='general')
        await channel.send('Hermes is present let the banter fly, the chat just got more lively, let the good times multiply!!!')
    else:
        await ctx.send(f"Junk")

@client.command()
async def goodbye(ctx):
    caller = get_caller(ctx)
    if caller in AUTHORIZED_USERS:
        channel = discord.utils.get(ctx.guild.channels, name='general')
        await channel.send("Aaaand he's gone to bed")
    else:
        await ctx.send(f"Junk")

@client.command()
async def ping(ctx):
    caller = get_caller(ctx)
    if caller in AUTHORIZED_USERS:
        await ctx.send("Pong!")
    elif caller == 'Digmac#8194':
        await ctx.send("https://www.youtube.com/watch?v=RUaYbfKZIiA&t=25s")
    else:
        await ctx.send(f"Junk")

client.run(TOKEN)

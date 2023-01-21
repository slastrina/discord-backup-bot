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

if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
    try:
        os.makedirs(uploads_path)
    except OSError as error:
        print(error)

engine = db.create_engine(os.getenv('DB_CONNECTION_STRING'), echo=False)
connection = engine.connect()
metadata = MetaData()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILD').split(',')

intent = discord.Intents.default()
intent.members = True
intent.messages = True
intent.message_content = True

client = commands.Bot(command_prefix='!', intents = intent)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print(discord.__version__)

@client.event
async def on_message(message):
    if message.guild.name in GUILDS:

        print(message)

        metadata.reflect(connection)

        is_forum = "parent" in dir(message.channel)

        parent = str(message.channel.parent) if is_forum else None

        table_name = f'{message.guild.name}_{parent or message.channel.name}'

        if not connection.dialect.has_table(engine.connect(), table_name):  # If table don't exist, Create.
            Table(table_name, metadata,
                  Column('id', BigInteger, primary_key=True, nullable=False),
                  Column('date', DateTime),
                  Column('guild', String),
                  Column('parent', String),
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
            parent=parent,
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

        print(len(attachments))

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

client.run(TOKEN)
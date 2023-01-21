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

load_dotenv()

uploads_path = Path(os.getenv('ATTACHMENTS_PATH'))

if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
    try:
        os.makedirs(uploads_path)
    except OSError as error:
        print(error)

engine = db.create_engine(os.getenv('DB_CONNECTION_STRING'), echo=False)
connection = engine.connect()

TOKEN = os.getenv('DISCORD_TOKEN')

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
    print(message)
    print(message.content)
    print(message.attachments)
    metadata = MetaData(engine)
    metadata.reflect(bind=engine)

    parent = str(message.channel.parent) if "parent" in dir(message.channel) else None

    table_name = f'{message.guild.name}_{parent or message.channel.name}'

    if not engine.dialect.has_table(engine.connect(), table_name):  # If table don't exist, Create.
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
        metadata.create_all()

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

    if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
        try:
            os.mkdir(uploads_path / f'channel_{message.channel.name}_{message.channel.id}')
        except OSError as error:
            pass

        for attachment in attachments:
            channel_name = message.channel.name
            req = requests.get(attachment['url'], allow_redirects=True)
            filepath = uploads_path / f'channel_{message.channel.name}_{message.channel.id}' / f'{attachment["id"]}_{channel_name}_{attachment["filename"]}'
            open(filepath, 'wb').write(req.content)

client.run(TOKEN)
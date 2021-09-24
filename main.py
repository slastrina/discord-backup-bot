import json
import os
import random
from datetime import datetime
import requests
import sqlalchemy as db

import discord
from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, BigInteger, String, DateTime, Column, insert
from pathlib import Path

load_dotenv()

uploads_path = Path(os.getenv('ATTACHMENTS_PATH'))

if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
    try:
        os.mkdir(uploads_path)
    except OSError as error:
        pass

engine = db.create_engine(os.getenv('DB_CONNECTION_STRING'), echo=False)
connection = engine.connect()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    print(message)
    print(message.content)
    print(message.attachments)
    metadata = MetaData(engine)
    metadata.reflect(bind=engine)

    if not engine.dialect.has_table(engine.connect(), f'channel_{message.channel.name}_{message.channel.id}'):  # If table don't exist, Create.
        Table(f'channel_{message.channel.name}_{message.channel.id}', metadata,
              Column('id', BigInteger, primary_key=True, nullable=False),
              Column('date', DateTime),
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

    tbl = metadata.tables[f'channel_{message.channel.name}_{message.channel.id}']

    attachments = [{'id': x.id, 'filename': x.filename, 'url': x.url} for x in list(message.attachments)]

    stmt = insert(tbl).values(
        id=message.id,
        date=datetime.now(),
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
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

if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
    try:
        os.mkdir(os.getenv('ATTACHMENTS_PATH'))
    except OSError as error:
        pass

engine = db.create_engine('sqlite:///bot.db', echo=False)
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

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    print(message)
    print(message.content)
    print(message.attachments)
    metadata = MetaData(engine)
    metadata.reflect(bind=engine)

    if not engine.dialect.has_table(engine.connect(), f'channel_{message.channel.name}'):  # If table don't exist, Create.
        # Create a table with the appropriate Columns
        Table(f'channel_{message.channel.name}', metadata,
              Column('id', BigInteger, primary_key=True, nullable=False),
              Column('date', DateTime),
              Column('channel', String),
              Column('author_id', BigInteger),
              Column('author_name', String),
              Column('author_discriminator', String),
              Column('author_nick', String),
              Column('message_content', String),
              Column('message_attachments', String),
              )
              # Implement the creation
        metadata.create_all()

    tbl = metadata.tables[f'channel_{message.channel.name}']

    attachments = [{'id': x.id, 'filename': x.filename, 'url': x.url} for x in list(message.attachments)]

    stmt = insert(tbl).values(
        id=message.id,
        date=datetime.now(),
        channel=message.channel.name,
        author_id=message.author.id,
        author_name=message.author.name,
        author_discriminator=message.author.discriminator,
        author_nick=message.author.nick,
        message_content=message.content,
        message_attachments=json.dumps(attachments)
    )
    connection.execute(stmt)

    if os.getenv('DOWNLOAD_ATTACHMENTS') == 'TRUE':
        for attachment in attachments:
            channel_name = message.channel.name
            req = requests.get(attachment['url'], allow_redirects=True)
            filepath = Path(os.getenv('ATTACHMENTS_PATH')) / f'{attachment["id"]}_{channel_name}_{attachment["filename"]}'
            open(filepath, 'wb').write(req.content)

client.run(TOKEN)
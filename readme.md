## Discord Backup Bot
------------
A simple bot that admins can use to scrape messages and attachments posted in their discord groups
This bot can help preserve content in channels should discord disable/bans a guild or an admin accidentally deletes something they shouldnt

Requirements
------------
* python 3.6+
* A discord account
* A discord app account (http://discordapp.com/developers/applications)

Setup
------------
* create a copy of .envbak and rename it .env
* edit .env and supply
  * your discord bot token (DISCORD_TOKEN) (http://discordapp.com/developers/applications)
  * your discord guild name (DISCORD_GUILD)
  * whether you wish to download attachments (DOWNLOAD_ATTACHMENTS)
  * where you would like to download given attachments (ATTACHMENTS_PATH)
  * the db connection string (DB_CONNECTION_STRING) (see sqlalchemy docs for other engine types https://docs.sqlalchemy.org/en/14/core/engines.html)
    * Default will create an sqlite database in the root of the bot directory
* Ensure your bot has been created and that an OAUTH url has been created with ADMIN privileges, click the oauth link and select the guild you own in order to invite the bot
* start the python script using
  * python main.py

if you witness debug messages such as '{BOTNAME} is connected to the following guild: {SERVER Details}' your bot is ready to use.

Notes
------------
* this bot will automatically create new models to represent channels in the guild, these models/schemas will be created only once a message is received in them.
* model names are in the following format "channel_{channel_name}_{channel_id}" i.e. channel_general_1234123123123
* the model name is also used as a subdirectory within the uploads folder if attachment downloads were enabled.
* This bot/script was Haphazardly put together, there is plenty of room for improvement, i welcome collaboration in the form of suggestions or pull requests
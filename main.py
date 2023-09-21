import discord
import time
from datetime import datetime
from discord import ui
from discord.ext import commands
from elasticsearch import Elasticsearch
from discord import app_commands
from discord import SyncWebhook
from keep_alive import keep_alive

import config


class SearchBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        await self.tree.sync(guild=bot.get_guild(1154388870478168096))


bot = SearchBot()


@bot.tree.command(guild=bot.get_guild(1154388870478168096), description="Veri ara")
@app_commands.rename(search='arama')
@app_commands.describe(
    search="Aramak istediğiniz şey",
)
async def search(interaction: discord.Interaction, search: str):
    elastic = Elasticsearch(config.api_url, api_key=config.api_key)
    resp = elastic.search(index="search-archive", q=search)
    message = ""
    for hit in resp['hits']['hits']:
        message += f"<t:{str(hit['_source']['timestamp'])[:-2]}:R> {hit['_source']['author']}| {hit['_source']['title']}:\n {hit['_source']['text']}\n"
    await interaction.response.send_message(message)


@bot.tree.command(guild=bot.get_guild(1154388870478168096), description="Arşive veri ekle",
                  name="add-data-to-archive")
@app_commands.rename(name="isim", data="veri")
@app_commands.describe(
    name="Verinin ismi",
    data="Veri"
)
async def add_to_archive(interaction: discord.Interaction, name: str, data: str):
    elastic = Elasticsearch(config.api_url, api_key=config.api_key)
    doc = {
        'author': interaction.user.mention,
        'title': name,
        'text': data,
        'timestamp': time.mktime(datetime.now().timetuple()),
        "_extract_binary_content": True,
        "_reduce_whitespace": True,
        "_run_ml_inference": False
    }
    resp = elastic.index(index="search-archive", document=doc)
    channel = interaction.client.get_channel(1154389453532569691)
    await channel.send(
        f"`{name}`, {interaction.user.mention} tarafından arşive eklendi:\n## {name}\n{data}")
    await interaction.response.send_message(f"Durum: `{resp['result']}` | {name} arşive eklendi")


keep_alive()


bot.run(config.bot_token)

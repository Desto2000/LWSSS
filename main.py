import discord
import time
from datetime import datetime
from discord import ui
from discord.ext import commands
from elasticsearch import Elasticsearch
from discord import SyncWebhook

import config


class Search(ui.Modal, title='LWSSS Arşiv Veri Araması'):
    search = ui.TextInput(label='Aramak istediğin şeyi yaz')

    async def on_submit(self, interaction: discord.Interaction):
        elastic = Elasticsearch(config.api_url, api_key=config.api_key)
        resp = elastic.search(index="search-archive", q=str(self.search.value))
        message = ""
        for hit in resp['hits']['hits']:
            message += f"<t:{str(hit['_source']['timestamp'])[:-2]}:R> {hit['_source']['author']}| {hit['_source']['title']}:\n {hit['_source']['text']}\n"
        await interaction.response.send_message(message)


class AddToArchive(ui.Modal, title='LWSSS Arşive Veri Ekleme'):
    name = ui.TextInput(label='Eklemek istediğin verinin adı')
    data = ui.TextInput(label='Eklemek istediğin veri')

    async def on_submit(self, interaction: discord.Interaction):
        elastic = Elasticsearch(config.api_url, api_key=config.api_key)
        doc = {
            'author': interaction.user.mention,
            'title': self.name.value,
            'text': self.data.value,
            'timestamp': time.mktime(datetime.now().timetuple()),
            "_extract_binary_content": True,
            "_reduce_whitespace": True,
            "_run_ml_inference": False
        }
        resp = elastic.index(index="search-archive", document=doc)
        channel = interaction.client.get_channel(1154389453532569691)
        await channel.send(f"`{self.name.value}`, {interaction.user.mention} tarafından arşive eklendi:\n## {self.name.value}\n{self.data.value}")
        await interaction.response.send_message(f"Durum: `{resp['result']}` | {self.name.value} arşive eklendi")


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


@bot.tree.command(guild=bot.get_guild(1154388870478168096), description="search")
async def search(interaction: discord.Interaction):
    # Send the modal with an instance of our `Feedback` class
    # Since modals require an interaction, they cannot be done as a response to a text command.
    # They can only be done as a response to either an application command or a button press.
    await interaction.response.send_modal(Search())


@bot.tree.command(guild=bot.get_guild(1154388870478168096), description="add to archive", name="add-data-to-archive")
async def add_to_archive(interaction: discord.Interaction):
    # Send the modal with an instance of our `Feedback` class
    # Since modals require an interaction, they cannot be done as a response to a text command.
    # They can only be done as a response to either an application command or a button press.
    await interaction.response.send_modal(AddToArchive())


bot.run(config.bot_token)

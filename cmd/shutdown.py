import discord

from class_templates import GenericCommand

permission_level = 4


class Command(GenericCommand):

    permission_level = 4

    async def run(self, args, message):
        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game("shutdown"))
        await self.util.shutdown()

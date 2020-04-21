import asyncio

import discord

from class_templates import GenericCommand

permission_level = 0


class Command(GenericCommand):

    async def run(self, args, message):
        voice = message.author.voice
        if voice is None:
            await message.channel.send("you're not in a voice channel, nobody will hear me! :c")
            return
        sme = args[0]
        for x in self.util.known_smes:
            if sme in x["alias"]:
                vcs = self.client.voice_clients
                channel = voice.channel
                # check if bot active in guild
                vc = None
                if message.guild in [x.guild for x in vcs]:
                    blocking_vc = [x for x in vcs if x.guild == message.guild][0]
                    blocking_vc.pause()
                    if blocking_vc.channel != channel:
                        await blocking_vc.move_to(channel)
                    vc = blocking_vc
                else:
                    vc = await channel.connect()
                await message.channel.send("playing " + x["file"])
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("sme/" + x["file"]))
                vc.play(source)
                self.client.loop.create_task(self.leave(vc))
                return
        await message.channel.send("not found, sorry.")

    async def leave(self, vc):
        await self.client.wait_until_ready()
        while vc.is_playing():
            await asyncio.sleep(0.1)
        if not vc.is_paused():
            await vc.disconnect()

import traceback

import class_templates

alias = ["rl"]
permission_level = 4


class Command(class_templates.GenericCommand):

    async def run(self, args, message):
        msg = await message.channel.send("soft-rebooting!")
        # noinspection PyBroadException
        try:
            await self.util.reload_coro(relay=True)
            for x in "DONE":
                await msg.add_reaction(self.util.EMOJI[x])
        except Exception:
            await message.channel.send("somebody fucked up the json file. (or something else)\n")
            track = traceback.format_exc()
            await message.channel.send("```\n" + track + "\n```")

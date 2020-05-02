import discord
import traceback

from util import Util

client = discord.Client()
util = Util(client)

was_running = False


@client.event
async def on_ready():
    print("api ready!")
    global was_running
    if not was_running:
        await util.reload_coro()
        was_running = True


@client.event
async def on_message(message):
    # ignore own messages
    if message.author == client.user:
        return

    cmd = None
    args = None
    for p in util.PREFIXES:
        if message.content.startswith(p):
            cmd = message.content[len(p):]
            break

    # ignore prefixes in DM
    if cmd is None and type(message.channel) == discord.DMChannel:
        cmd = message.content

    if cmd is not None:
        args = cmd.split(" ")[1:]
        cmd = cmd.split(" ")[0]
        if cmd in util.known_cmds:
            cmdclass = util.known_cmds[cmd]
            userlvl = util.get_permission_level(message.author)
            cmdlvl = cmdclass.permission_level
            if userlvl < cmdlvl:
                await message.channel.send("insufficient permission. your level: " + str(userlvl) + " required: " + str(cmdlvl))
                return
            # noinspection PyBroadException
            try:
                print("running " + cmd)
                await cmdclass.run(args, message)
            except Exception:
                traceback.print_exc()
                await message.channel.send("an error occured running the command.")
                track = traceback.format_exc()
                await message.channel.send("```\n" + track + "\n```")
            return
        else:
            # unknown command
            pass
    else:
        # not a % command
        print(message.content)
        return

if __name__ == "__main__":
    util.run()

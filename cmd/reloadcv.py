from class_templates import GenericCommand

alias = ["rlcv"]
permission_level = 4


class Command(GenericCommand):

    async def run(self, args, message):

        num = self.util.known_cmds["cv"].load_cv_modules()
        await message.channel.send("loaded " + str(num) + " cv modules")

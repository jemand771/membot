import importlib.util
import json
import os
import shutil
import traceback
import uuid

import cv2
import discord


from class_templates import GenericCommand, FuniaGeneratorNotFoundError

permission_level = 0


class Command(GenericCommand):

    channel_images = {}
    known_modules = {}

    async def run(self, args, message):
        if not args:
            return

        ch = message.channel.id

        if len(args) == 2 and args[0] == "save":
            idd = args[1]
            ch = message.channel.id
            if ch not in self.channel_images.keys():
                await message.channel.send("no image is currently loaded")
                return
            output = self.util.SAVED_FOLDER + self.util.get_folder_id_from_message(message) + "/" + idd + ".png"
            if os.path.exists(output):
                await message.channel.send("that image already exists. use `cv delete` to delete it first")
                return
            shutil.copyfile(self.channel_images[ch][-1], output)
            await message.channel.send("saved as " + idd)
            return

        if len(args) == 2 and args[0] == "delete":
            idd = args[1]
            output = self.util.SAVED_FOLDER + self.util.get_folder_id_from_message(message) + "/" + idd + ".png"
            if not os.path.exists(output):
                await message.channel.send("that image does not exist")
                return
            os.remove(output)
            await message.channel.send("deleted " + idd)
            return

        if len(args) == 1 and args[0] == "list":
            msg = "List of CV modules:\n```\n"
            for mod in self.known_modules.keys():
                msg += mod + "\n"
            msg += "```"
            await message.channel.send(msg)
            return

        # todo make this pretty
        if args == ["funia", "list"]:
            with open("funia_generators.json") as f:
                await message.channel.send("```\n" + "\n".join([", ".join(x["alias"]) for x in json.load(f)]) + "\n```")
            return

        if 1 <= len(args) <= 2 and args[0] == "undo":
            num = 1
            if len(args) == 2:
                try:
                    num = int(args[1])
                except TypeError:
                    pass

            av = len(self.channel_images[ch])
            if av <= num:
                num = av
                del self.channel_images[ch]
                await message.channel.send("image stack cleared. (" + str(num) + " elements removed)")
            else:
                self.channel_images[ch] = self.channel_images[ch][:-num]
                await message.channel.send("popped " + str(num) + " elements from image stack")
            return

        if args == ["queue"]:
            if ch not in self.channel_images.keys():
                await message.channel.send("the image queue for channel`" + str(ch) + "` is empty")
                return
            await message.channel.send(
                "image queue for channel `" + str(ch) + "`:\n```\n" + "\n".join(
                    [x.split("/")[-1].split(".")[0] for x in self.channel_images[ch]]
                ) + "\n```"
            )
            return

        # insert more special commands above. modules are processed last

        if args[0] in self.known_modules:
            mod = self.known_modules[args[0]]
            ext_image = None
            if not hasattr(mod, "generator"):
                if ch not in self.channel_images.keys():
                    await message.channel.send("no image is selected or uploaded. nothing to do")
                    return
                ext_image = cv2.imread(self.channel_images[ch][-1])

            async def action(img):

                # noinspection PyBroadException
                try:
                    print("  applying module " + args[0])
                    images = None if ch not in self.channel_images.keys() else self.channel_images[ch][::-1]
                    img = await mod.perform(img, *args[1:], images=images, message=message)
                    # save image id directly
                    iidd = None
                    ioutput = None
                    # overwrite with image if cv2 image was returned
                    if type(img) == str:
                        iidd = img.split("/")[-1].split(".")[0]
                        ioutput = img
                    else:
                        iidd = self.util.generate_uuid()
                        ioutput = self.util.TEMP_FOLDER + iidd + ".png"
                        cv2.imwrite(ioutput, img)
                    if ch in self.channel_images.keys():
                        self.channel_images[ch].append(ioutput)
                    else:
                        self.channel_images[ch] = [ioutput]
                    mb = round(os.path.getsize(ioutput) / 1024 / 1024, self.util.MB_ROUND)
                    if mb > self.util.MAX_FILESIZE:
                        ioutput = self.util.TEMP_FOLDER + iidd + "-downsampled.png"
                        await message.channel.send("it's too big (owo), down-sampling... (original: " + str(mb) + "MB)")
                        while mb > self.util.MAX_FILESIZE:
                            print("  downscaling from " + str(mb) + "mb")
                            width = int(img.shape[1] * 0.5)
                            height = int(img.shape[0] * 0.5)
                            img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
                            cv2.imwrite(ioutput, img)
                            mb = round(os.path.getsize(ioutput) / 1024 / 1024, self.util.MB_ROUND)
                    print("  uploading..")
                    await message.channel.send(
                        "local image id: " + iidd,
                        file=discord.File(ioutput))
                    print("  done!")

                except Exception as ex:
                    if isinstance(ex, FuniaGeneratorNotFoundError):
                        await message.channel.send("generator not found in local configuration. has it been registered?")
                        return
                    await message.channel.send("An error occured while executing the CV module.")
                    track = traceback.format_exc()
                    traceback.print_exc()
                    await message.channel.send("```\n" + track + "\n```")

            self.client.loop.create_task(action(ext_image))
            return
        await message.channel.send("unknown module \"" + args[0] + "\"")
        return

    # dynamic module loader
    def load_cv_modules(self):
        self.known_modules = {}
        print("loading cv modules")
        for file in [f for f in os.listdir("cv_modules") if os.path.isfile("cv_modules/" + f)]:
            print("  cv loading", file)
            mod_name = file[:-3]
            spec = importlib.util.spec_from_file_location(mod_name, "cv_modules/" + file)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            mod = foo.CVModule(self.util)
            self.known_modules[mod_name] = mod
        return len(self.known_modules)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_cv_modules()

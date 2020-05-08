import asyncio
import aiohttp
import cv2
import importlib.util
import json
import mimetypes
import magic
import os
import sys
import traceback
import urllib.request
import uuid

import discord


class Util:

    YES_SYNONYMS = ["yes", "true", "on", "1"]
    NO_SYNONYMS = ["no", "false", "off", "0"]
    # todo there has to be a better way to do this
    EMOJI = {"D": "🇩", "E": "🇪", "N": "🇳", "O": "🇴"}

    BOT_TOKEN = "token goes here"
    PREFIXES = []
    MB_ROUND = 3
    MAX_FILESIZE = 5
    TEMP_FOLDER = "data/temp/"
    SAVED_FOLDER = "data/saved/"
    LIBRARY_FOLDER = "data/library/"

    def __init__(self, client):
        self.known_smes = []
        self.known_cmds = {}
        self.client = client

    def load_sme_index(self):
        self.known_smes = []
        file = open("config/sme.json")
        cand = json.load(file)
        file.close()
        for x in cand:
            if os.path.isfile("sme/" + x["file"]):
                self.known_smes.append(x)

    def import_commands(self):
        for file in [f for f in os.listdir("cmd") if os.path.isfile("cmd/" + f)]:
            print("loading", file)
            cmd_name = file[:-3]
            spec = importlib.util.spec_from_file_location(cmd_name, "cmd/" + file)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            cmd = foo.Command(self.client, self)
            cmd.permission_level = foo.permission_level if hasattr(foo, "permission_level") else 4
            if hasattr(foo, "alias"):
                for a in foo.alias:
                    self.known_cmds[a] = cmd
            self.known_cmds[cmd_name] = cmd

    def mkdirs(self):
        for x in (self.TEMP_FOLDER, self.LIBRARY_FOLDER, self.SAVED_FOLDER):
            if not os.path.exists(x):
                os.mkdir(x)
        for x in self.client.guilds:
            p = self.SAVED_FOLDER + str(x.id)
            if not os.path.exists(p):
                print("creating saved dir for guild " + str(x.id))
                os.mkdir(p)

    def reload(self):
        self.load_sme_index()
        self.known_cmds = {}
        self.import_commands()
        self.mkdirs()

    async def reload_coro(self, relay=False):
        version_string = os.getenv("BOT_VERSION", "unknown (non-docker)")
        await self.client.change_presence(
            status=discord.Status.idle,
            activity=discord.Game("starting " + version_string))
        exc = None
        # noinspection PyBroadException
        try:
            self.reload()
            game = discord.Game(version_string)
        except Exception as ex:
            exc = ex
            print("an error occured staring up the bot. will continue anyway. stacktrace:")
            traceback.print_exc()
            game = discord.Game("STARTUP ERROR")
        await self.client.change_presence(status=discord.Status.online, activity=game)
        print("DiscordTag: {0.user}".format(self.client))
        if relay and exc is not None:
            raise exc

    async def shutdown(self):
        await self.client.close()

    def run(self):
        with open("config/config.json") as f:
            config = json.load(f)
            self.BOT_TOKEN = config["bot_token"]
            self.PREFIXES = config["prefixes"]
            self.MB_ROUND = config["max_filesize"] if "max_filesize" in config else self.MB_ROUND
            self.MB_ROUND = config["max_filesize"] if "max_filesize" in config else self.MAX_FILESIZE
            self.TEMP_FOLDER = config["folders"]["temp"]
            self.SAVED_FOLDER = config["folders"]["saved"]
            self.LIBRARY_FOLDER = config["folders"]["library"]
        self.client.run(self.BOT_TOKEN)

    async def download_png(self, idd, url):
        output = self.TEMP_FOLDER + idd
        mime = magic.Magic(mime=True)
        # urllib.request.urlretrieve(url, output)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(output, "wb") as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
        mimes = mime.from_file(output)
        ext = mimetypes.guess_all_extensions(mimes)[0]
        os.rename(output, output + ext)
        # force convert to png
        if ext != ".png":
            img = cv2.imread(output + ext)
            cv2.imwrite(output + ".png", img)
            os.remove(output + ext)
        return output + ".png"

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4()).replace("-", "")

    @staticmethod
    def get_permission_level(user):

        # todo this is kinda selfish
        if user.id == 346668804375445505:
            return 4
        return 0

    @staticmethod
    def get_folder_id_from_message(message):
        return str(message.author.id if type(message.channel) == discord.DMChannel else message.guild.id)

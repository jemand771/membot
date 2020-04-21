import aiohttp
import asyncio
import cv2
import json
import uuid

from class_templates import GenericCVModule, FuniaGeneratorNotFoundError

with open("funia_generators.json") as f:
    allowed_generators = json.load(f)


class CVModule(GenericCVModule):

    generator = True

    async def perform(self, _, *args, **kwargs):

        if not args:
            return
        nickname = args[0]
        given_images = kwargs["images"]

        generator = None
        num_images = 0
        num_texts = 0
        texts = []
        for gen in allowed_generators:
            if nickname in gen["alias"]:
                generator = gen
                if "num_texts" in gen.keys():
                    num_texts = gen["num_texts"]
                    maxlens = generator["max_lens"]
                    texts = " ".join(args[1:]).split(";")[:num_texts]
                    texts = [t[:maxlens[i]] for i, t in enumerate(texts)]
                if "num_images" in gen.keys():
                    num_images = gen["num_images"]
                break

        if generator is None:  # not found
            raise FuniaGeneratorNotFoundError()
            pass

        generator_name = generator["name"]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
        payload = aiohttp.FormData()

        if num_images == 1:
            if not given_images:
                return
            payload.add_field("image", open(given_images[0], "rb"))

        # text parameters
        if num_texts == 1:
            payload.add_field("text", texts[0])
        else:
            for i, txt in enumerate(texts):
                key = "text" + str(i + 1)
                if key in generator.keys():
                    key = generator[key]
                payload.add_field(key, txt)

        # image parameters

        url = "https://photofunia.com//categories/all_effects/" + generator_name + "?server=3"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=headers) as r:
                    txt = await r.text()
        except asyncio.TimeoutError:
            print("asyncio timeout")
            return
        url = None
        for size in ["l", "r", "s"]:
            for line in txt.split("\n"):
                if "/results/" in line and "_" + size + ".jpg?download" in line:
                    url = line.split("?download")[0].split("\"")[1]
                    break
            if url is not None:
                break
        if url is None:
            print("download error")
            # todo error handling if no image is returned
            return

        idd = self.util.generate_uuid()
        await self.util.download_png(idd, url)
        img = cv2.imread(self.util.TEMP_FOLDER + idd + ".png")
        return img
